import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# add the parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

# import utility functions directly to avoid circular imports
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    import math
    
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def validate_nyc_coordinates(lat, lon):
    """
    Validate if coordinates are within NYC bounds using configured values
    """
    # handle NaN values
    if pd.isna(lat) or pd.isna(lon):
        return False
    
    return (
        settings.NYC_MIN_LAT <= lat <= settings.NYC_MAX_LAT and 
        settings.NYC_MIN_LON <= lon <= settings.NYC_MAX_LON
    )

class TaxiDataCleaner:
    """
    Comprehensive cleaning pipeline for NYC Taxi Trip data
    """
    
    def __init__(self):
        self.raw_data_path = "./raw/train.csv"
        self.cleaned_data_path = "./clean/clean.csv"
        self.log_path = "./clean/clean_log.txt"
        self.cleaning_stats = {}
        
    def load_raw_data(self):
        """Load the raw CSV data"""
        print("📥 Loading raw data...")
        
        try:
            # read the CSV file
            df = pd.read_csv(self.raw_data_path)
            print(f"Loaded {len(df)} raw records")
            
            # show basic info about the dataset
            print(f"Dataset shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            return df
        except FileNotFoundError:
            print(f"Error: Raw data file not found at {self.raw_data_path}")
            print("Please make sure train.csv is in the data/raw/ directory")
            raise
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def clean_data(self, df):
        """
        Main cleaning pipeline
        """
        initial_count = len(df)
        self.cleaning_stats['initial_count'] = initial_count
        print(f"Starting cleaning process with {initial_count:,} records...")
        
        # basic data quality checks
        df = self._handle_missing_values(df)
        
        # remove duplicates
        df = self._remove_duplicates(df)
        
        # validate and filter coordinates
        df = self._filter_valid_coordinates(df)
        
        # filter valid trip durations
        df = self._filter_valid_durations(df)
        
        # convert timestamps and extract temporal features
        df = self._process_timestamps(df)
        
        # calculate derived features
        df = self._calculate_derived_features(df)
        
        # filter impossible speeds and distances
        df = self._filter_impossible_trips(df)
        
        # sample data if too large (for performance)
        df = self._sample_data_if_needed(df)
        
        # final data validation
        df = self._final_validation(df)
        
        final_count = len(df)
        self.cleaning_stats['final_count'] = final_count
        self.cleaning_stats['records_removed'] = initial_count - final_count
        self.cleaning_stats['retention_rate'] = (final_count / initial_count) * 100
        
        print(f"Cleaning complete! {final_count:,} records retained ({self.cleaning_stats['retention_rate']:.1f}%)")
        
        return df
    
    def _handle_missing_values(self, df):
        """Handle missing values in the dataset"""
        print("Handling missing values...")
        
        initial_count = len(df)
        
        # check for missing values
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            print("Missing values per column:")
            for col, count in missing_data.items():
                if count > 0:
                    print(f"  - {col}: {count} missing ({count/len(df)*100:.1f}%)")
        else:
            print("No missing values found")
        
        # remove rows with critical missing values
        critical_columns = [
            'pickup_datetime', 'dropoff_datetime',
            'pickup_longitude', 'pickup_latitude',
            'dropoff_longitude', 'dropoff_latitude',
            'trip_duration'
        ]
        
        # check which critical columns exist in the dataset
        existing_critical = [col for col in critical_columns if col in df.columns]
        
        df_clean = df.dropna(subset=existing_critical)
        
        removed = initial_count - len(df_clean)
        if removed > 0:
            print(f"Removed {removed} records with missing critical data")
        else:
            print("No records with missing critical data")
            
        self.cleaning_stats['missing_removed'] = removed
        
        return df_clean
    
    def _remove_duplicates(self, df):
        """Remove duplicate records"""
        print("Removing duplicates...")
        
        initial_count = len(df)
        
        # remove exact duplicates
        df_clean = df.drop_duplicates()
        
        # if ID column exists, remove duplicates by ID
        if 'id' in df.columns:
            initial_before_id = len(df_clean)
            df_clean = df_clean.drop_duplicates(subset=['id'])
            id_duplicates = initial_before_id - len(df_clean)
            if id_duplicates > 0:
                print(f"Removed {id_duplicates} duplicates by ID")
        
        removed = initial_count - len(df_clean)
        if removed > 0:
            print(f"Removed {removed} duplicate records")
        else:
            print("No duplicate records found")
            
        self.cleaning_stats['duplicates_removed'] = removed
        
        return df_clean
    
    def _filter_valid_coordinates(self, df):
        """Filter records with valid NYC coordinates"""
        print("Filtering valid NYC coordinates...")
        
        initial_count = len(df)
        
        # filter pickup coordinates within NYC bounds
        pickup_mask = df.apply(
            lambda row: validate_nyc_coordinates(row['pickup_latitude'], row['pickup_longitude']), 
            axis=1
        )
        
        # filter dropoff coordinates within NYC bounds
        dropoff_mask = df.apply(
            lambda row: validate_nyc_coordinates(row['dropoff_latitude'], row['dropoff_longitude']), 
            axis=1
        )
        
        df_clean = df[pickup_mask & dropoff_mask]
        
        removed = initial_count - len(df_clean)
        if removed > 0:
            print(f"Removed {removed} records with coordinates outside NYC bounds")
        else:
            print("All coordinates are within NYC bounds")
            
        self.cleaning_stats['invalid_coords_removed'] = removed
        
        return df_clean
    
    def _filter_valid_durations(self, df):
        """Filter valid trip durations"""
        print("Filtering valid trip durations...")
        
        initial_count = len(df)
        
        # remove trips that are too short or too long
        # minimum: 30 seconds, Maximum: 3 hours (10800 seconds)
        duration_mask = (df['trip_duration'] >= 30) & (df['trip_duration'] <= 10800)
        
        df_clean = df[duration_mask]
        
        removed = initial_count - len(df_clean)
        if removed > 0:
            print(f"Removed {removed} records with invalid trip durations")
        else:
            print("All trip durations are valid")
            
        self.cleaning_stats['invalid_duration_removed'] = removed
        
        return df_clean
    
    def _process_timestamps(self, df):
        """Convert timestamps and extract temporal features"""
        print("Processing timestamps...")
        
        # convert to datetime
        df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
        df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])
        
        # extract temporal features
        df['pickup_hour'] = df['pickup_datetime'].dt.hour
        df['pickup_day'] = df['pickup_datetime'].dt.day
        df['pickup_month'] = df['pickup_datetime'].dt.month
        df['pickup_year'] = df['pickup_datetime'].dt.year
        df['day_of_week'] = df['pickup_datetime'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        print("Extracted temporal features: hour, day, month, day_of_week, is_weekend")
        
        return df
    
    def _calculate_derived_features(self, df):
        """Calculate derived features like distance and speed"""
        print("Calculating derived features...")
        
        # calculate trip distance using Haversine formula
        print("  Calculating trip distances...")
        df['trip_distance_km'] = df.apply(
            lambda row: haversine_distance(
                row['pickup_latitude'], row['pickup_longitude'],
                row['dropoff_latitude'], row['dropoff_longitude']
            ), 
            axis=1
        )
        
        # calculate trip speed (km/h)
        print("  Calculating trip speeds...")
        df['trip_speed_km_h'] = (df['trip_distance_km'] / (df['trip_duration'] / 3600))
        
        # handle infinite values from division by zero
        df['trip_speed_km_h'] = df['trip_speed_km_h'].replace([np.inf, -np.inf], np.nan)
        
        print("Calculated derived features: distance, speed")
        
        return df
    
    def _filter_impossible_trips(self, df):
        """Filter trips with impossible speeds or distances"""
        print("Filtering impossible trips...")
        
        initial_count = len(df)
        
        # filter reasonable speeds (1 km/h to 120 km/h)
        speed_mask = (df['trip_speed_km_h'] >= 1) & (df['trip_speed_km_h'] <= 120)
        
        # filter reasonable distances (0.1 km to 100 km)
        distance_mask = (df['trip_distance_km'] >= 0.1) & (df['trip_distance_km'] <= 100)
        
        # filter zero passenger trips
        if 'passenger_count' in df.columns:
            passenger_mask = (df['passenger_count'] > 0) & (df['passenger_count'] <= 6)
        else:
            passenger_mask = pd.Series([True] * len(df))
        
        df_clean = df[speed_mask & distance_mask & passenger_mask]
        
        removed = initial_count - len(df_clean)
        if removed > 0:
            print(f"Removed {removed} records with impossible trip characteristics")
        else:
            print("All trips have reasonable characteristics")
            
        self.cleaning_stats['impossible_trips_removed'] = removed
        
        return df_clean
    
    def _sample_data_if_needed(self, df):
        """Sample data if it exceeds the configured limit"""
        if len(df) > settings.MAX_TRIPS_PROCESS:
            print(f"Sampling data from {len(df):,} to {settings.MAX_TRIPS_PROCESS:,} records...")
            df_sampled = df.sample(n=settings.MAX_TRIPS_PROCESS, random_state=42)
            self.cleaning_stats['sampled'] = True
            self.cleaning_stats['sample_size'] = settings.MAX_TRIPS_PROCESS
            return df_sampled
        else:
            self.cleaning_stats['sampled'] = False
            return df
    
    def _final_validation(self, df):
        """Perform final data validation"""
        print("Performing final validation...")
        
        # check for any remaining missing values
        missing_final = df.isnull().sum().sum()
        if missing_final > 0:
            print(f"Warning: {missing_final} missing values remain in the dataset")
        else:
            print("No missing values in final dataset")
        
        # validate data ranges
        valid_speed = ((df['trip_speed_km_h'] >= 1) & (df['trip_speed_km_h'] <= 120)).all()
        valid_duration = ((df['trip_duration'] >= 30) & (df['trip_duration'] <= 10800)).all()
        valid_distance = ((df['trip_distance_km'] >= 0.1) & (df['trip_distance_km'] <= 100)).all()
        
        if all([valid_speed, valid_duration, valid_distance]):
            print("All data validation checks passed")
        else:
            print("Warning: Some data validation checks failed")
        
        return df
    
    def save_cleaned_data(self, df):
        """Save the cleaned data to CSV"""
        print("Saving cleaned data...")
        
        # create cleaned directory if it doesn't exist
        os.makedirs(os.path.dirname(self.cleaned_data_path), exist_ok=True)
        
        # save the cleaned data
        df.to_csv(self.cleaned_data_path, index=False)
        print(f"Cleaned data saved to {self.cleaned_data_path}")
        
        # save cleaning log
        self._save_cleaning_log()
    
    def _save_cleaning_log(self):
        """Save a log of the cleaning process"""
        log_content = f"""
NYC Taxi Data Cleaning Log
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Cleaning Statistics:
- Initial records: {self.cleaning_stats.get('initial_count', 0):,}
- Final records: {self.cleaning_stats.get('final_count', 0):,}
- Records removed: {self.cleaning_stats.get('records_removed', 0):,}
- Retention rate: {self.cleaning_stats.get('retention_rate', 0):.1f}%

Breakdown of removed records:
- Missing values: {self.cleaning_stats.get('missing_removed', 0):,}
- Duplicates: {self.cleaning_stats.get('duplicates_removed', 0):,}
- Invalid coordinates: {self.cleaning_stats.get('invalid_coords_removed', 0):,}
- Invalid durations: {self.cleaning_stats.get('invalid_duration_removed', 0):,}
- Impossible trips: {self.cleaning_stats.get('impossible_trips_removed', 0):,}

Data sampling:
- Sampled: {self.cleaning_stats.get('sampled', False)}
- Sample size: {self.cleaning_stats.get('sample_size', 'N/A')}

Configuration used:
- MAX_TRIPS_PROCESS: {settings.MAX_TRIPS_PROCESS}
- NYC bounds: ({settings.NYC_MIN_LAT}, {settings.NYC_MIN_LON}) to ({settings.NYC_MAX_LAT}, {settings.NYC_MAX_LON})
"""
        
        with open(self.log_path, 'w') as f:
            f.write(log_content)
        
        print(f"Cleaning log saved to {self.log_path}")
    
    def run_pipeline(self):
        """Run the complete cleaning pipeline"""
        print("Starting NYC Taxi Data Cleaning Pipeline")
        print("=" * 50)
        
        try:
            # load raw data
            raw_df = self.load_raw_data()
            
            # clean data
            cleaned_df = self.clean_data(raw_df)
            
            # save cleaned data
            self.save_cleaned_data(cleaned_df)
            
            print("=" * 50)
            print("Cleaning pipeline completed successfully!")
            
            return cleaned_df
            
        except Exception as e:
            print(f"Cleaning pipeline failed: {e}")
            raise

def main():
    """Main function to run the cleaning pipeline"""
    cleaner = TaxiDataCleaner()
    cleaner.run_pipeline()

if __name__ == "__main__":
    main()
