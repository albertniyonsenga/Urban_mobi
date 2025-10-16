import sqlite3
import pandas as pd
import os
import sys

# add the parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DatabaseSetup:
    """
    Complete database setup and data loading
    """
    
    def __init__(self):
        self.db_path = "db/mobility.db"  # SQLite database file
        self.schema_path = "db/schema.sql"
        self.cleaned_data_path = "data/clean/clean.csv"
        
    def create_database(self):
        """Create the database with schema"""
        print("Creating database...")
        
        try:
            # connect to SQLite database (creates file if it doesn't exist)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # read and execute schema
            with open(self.schema_path, 'r') as f:
                schema_sql = f.read()
            
            cursor.executescript(schema_sql)
            conn.commit()
            
            print("Database schema created successfully")
            
            # verify tables were created
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [table[0] for table in cursor.fetchall()]
            print(f"Created tables: {tables}")
            
            # verify views were created
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='view'
            """)
            views = [view[0] for view in cursor.fetchall()]
            print(f"Created views: {views}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Database creation failed: {e}")
            return False
    
    def load_cleaned_data(self):
        """Load cleaned CSV data into the database"""
        print("Loading cleaned data into database...")
        
        if not os.path.exists(self.cleaned_data_path):
            print(f"\nCleaned data file not found: {self.cleaned_data_path}")
            print("Please run the cleaning pipeline first:")
            print("   python data/cleaning.py")
            return False
        
        try:
            # read cleaned data
            df = pd.read_csv(self.cleaned_data_path)
            print(f"Loaded {len(df):,} records from cleaned CSV")
            
            # connect to database
            conn = sqlite3.connect(self.db_path)
            
            # insert data into trips table
            print("Inserting data into trips table...")
            df.to_sql('trips', conn, if_exists='replace', index=False)
            
            # update metadata
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE system_metadata SET value = ? WHERE key = 'total_trips'",
                (str(len(df)),)
            )
            cursor.execute(
                "UPDATE system_metadata SET value = datetime('now') WHERE key = 'last_data_load'"
            )
            
            conn.commit()
            conn.close()
            
            print("Data successfully loaded into database")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def verify_database(self):
        """Verify the database was set up correctly"""
        print("Verifying database setup...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # check trip count
            cursor.execute("SELECT COUNT(*) FROM trips")
            trip_count = cursor.fetchone()[0]
            print(f"Trips in database: {trip_count:,}")
            
            # check metadata
            cursor.execute("SELECT key, value FROM system_metadata")
            metadata = cursor.fetchall()
            print("System metadata:")
            for key, value in metadata:
                print(f"   - {key}: {value}")
            
            # check views
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
            views = [view[0] for view in cursor.fetchall()]
            print(f"Available views: {views}")
            
            # test a sample query
            cursor.execute("SELECT COUNT(*) FROM hourly_stats")
            hourly_count = cursor.fetchone()[0]
            print(f"Hourly stats entries: {hourly_count}")
            
            conn.close()
            
            if trip_count > 0:
                print("Database verification successful!")
                return True
            else:
                print("Database verification failed: No trips found")
                return False
                
        except Exception as e:
            print(f"Database verification failed: {e}")
            return False
    
    def run_setup(self):
        """Run complete database setup"""
        print("Starting Database Setup")
        print("-" * 50)
        
        success = True
        
        # create database schema
        if not self.create_database():
            success = False
        
        # load cleaned data
        if success and not self.load_cleaned_data():
            success = False
        
        # verify setup
        if success and not self.verify_database():
            success = False
        
        if success:
            print("\nDatabase setup completed successfully!")
            print(f"Database file: {self.db_path}")
            print(f"Total trips loaded: [check verification output]")
        else:
            print("\nDatabase setup failed!")
        
        return success

def main():
    """Main function to run database setup"""
    setup = DatabaseSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
