import pandas as pd
import numpy as np
import logging
import os
from sqlalchemy import create_engine

# ---------------------------
# Setup logging
# ---------------------------
os.makedirs("../logs", exist_ok=True)
log_file = os.path.join("../logs", "cleaning.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ---------------------------
# Load raw dataset
# ---------------------------
raw_file = os.path.join("../data/raw/train.csv")
df = pd.read_csv(raw_file)
logging.info(f"Initial dataset shape: {df.shape}")

# ---------------------------
# Handle missing values
# ---------------------------
critical_cols = [
    'pickup_datetime', 'dropoff_datetime',
    'pickup_longitude', 'pickup_latitude',
    'dropoff_longitude', 'dropoff_latitude',
    'trip_distance', 'fare_amount'
]

df = df.dropna(subset=critical_cols)
if 'passenger_count' in df.columns:
    df['passenger_count'] = df['passenger_count'].fillna(1)

# ---------------------------
# Remove duplicates
# ---------------------------
df = df.drop_duplicates()

# ---------------------------
# Handle suspicious records
# ---------------------------
min_lat, max_lat = 40.5, 41.0
min_lon, max_lon = -74.3, -73.6

suspicious_rows = df[
    (df['trip_distance'] <= 0) |
    (df['fare_amount'] < 0) |
    (df['pickup_latitude'] < min_lat) | (df['pickup_latitude'] > max_lat) |
    (df['dropoff_latitude'] < min_lat) | (df['dropoff_latitude'] > max_lat) |
    (df['pickup_longitude'] < min_lon) | (df['pickup_longitude'] > max_lon) |
    (df['dropoff_longitude'] < min_lon) | (df['dropoff_longitude'] > max_lon)
]

# Save suspicious rows
suspicious_file = os.path.join("../logs/suspicious_rows.csv")
suspicious_rows.to_csv(suspicious_file, index=False)
df = df.drop(suspicious_rows.index)

# ---------------------------
# Normalize timestamps and coordinates
# ---------------------------
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], errors='coerce')
df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], errors='coerce')
coord_cols = ['pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude']
df[coord_cols] = df[coord_cols].apply(pd.to_numeric, errors='coerce')
df = df.dropna(subset=['pickup_datetime', 'dropoff_datetime'] + coord_cols)

# ---------------------------
# Compute derived features
# ---------------------------
df['trip_duration_minutes'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60
df['trip_speed_kmph'] = df['trip_distance'] / (df['trip_duration_minutes'] / 60)
df['fare_per_km'] = df['fare_amount'] / df['trip_distance']

# ---------------------------
# Save cleaned CSV
# ---------------------------
os.makedirs("../data/cleaned", exist_ok=True)
cleaned_file = os.path.join("../data/cleaned/train_cleaned.csv")
df.to_csv(cleaned_file, index=False)
logging.info(f"Cleaned dataset saved with shape {df.shape}")

# ---------------------------
# Insert into PostgreSQL
# ---------------------------
db_url = "postgresql://username:password@localhost:5432/nyc_taxi_db"  # Update credentials
engine = create_engine(db_url)
df.to_sql('taxi_trips', engine, if_exists='replace', index=False)
logging.info("Cleaned data inserted into database 'taxi_trips'")