<<<<<<< HEAD
-- Vendors dimension table
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id INTEGER PRIMARY KEY,
    vendor_name TEXT NOT NULL
);

-- Date dimension table for calendar dates
CREATE TABLE IF NOT EXISTS dates (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- Time dimension table for pickup times
CREATE TABLE IF NOT EXISTS times (
    time_id INTEGER PRIMARY KEY,
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    time_of_day TEXT NOT NULL CHECK(time_of_day IN ('morning', 'afternoon', 'evening', 'night'))
);

-- Locations dimension table (for both pickup and dropoff)
CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    location_type TEXT CHECK(location_type IN ('pickup', 'dropoff', 'both')),
    UNIQUE(latitude, longitude)
);

-- Main trips fact table
CREATE TABLE IF NOT EXISTS trips (
    trip_id TEXT PRIMARY KEY,
    vendor_id INTEGER NOT NULL,
    pickup_datetime DATETIME NOT NULL,
    dropoff_datetime DATETIME NOT NULL,
    passenger_count INTEGER NOT NULL,
    pickup_location_id INTEGER NOT NULL,
    dropoff_location_id INTEGER NOT NULL,
    store_and_fwd_flag TEXT NOT NULL,
    trip_duration INTEGER NOT NULL,
    trip_distance_km REAL NOT NULL,
    trip_speed_km_h REAL NOT NULL,
    
    -- Foreign key constraints
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (pickup_location_id) REFERENCES locations(location_id),
    FOREIGN KEY (dropoff_location_id) REFERENCES locations(location_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_dropoff_datetime ON trips(dropoff_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_trip_duration ON trips(trip_duration);
CREATE INDEX IF NOT EXISTS idx_trips_passenger_count ON trips(passenger_count);
CREATE INDEX IF NOT EXISTS idx_trips_vendor_id ON trips(vendor_id);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_location ON trips(pickup_location_id);
CREATE INDEX IF NOT EXISTS idx_trips_dropoff_location ON trips(dropoff_location_id);
CREATE INDEX IF NOT EXISTS idx_trips_trip_distance ON trips(trip_distance_km);
CREATE INDEX IF NOT EXISTS idx_trips_trip_speed ON trips(trip_speed_km_h);

CREATE INDEX IF NOT EXISTS idx_locations_coords ON locations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_dates_full_date ON dates(full_date);
CREATE INDEX IF NOT EXISTS idx_times_hour ON times(hour);
=======
-- Urban Mobility Database Schema for NYC Taxi Trips

-- trips table with all cleaned data
CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY,
    vendor_id INTEGER,
    pickup_datetime DATETIME NOT NULL,
    dropoff_datetime DATETIME NOT NULL,
    passenger_count INTEGER,
    pickup_longitude REAL NOT NULL,
    pickup_latitude REAL NOT NULL,
    dropoff_longitude REAL NOT NULL,
    dropoff_latitude REAL NOT NULL,
    store_and_fwd_flag TEXT,
    trip_duration INTEGER NOT NULL,
    
    -- derived features from cleaning pipeline
    trip_distance_km REAL NOT NULL,
    trip_speed_km_h REAL NOT NULL,
    
    -- temporal features
    pickup_hour INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    pickup_month INTEGER NOT NULL,
    pickup_year INTEGER NOT NULL,
    
    -- metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- indexes for optimal query performance
CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_hour ON trips(pickup_hour);
CREATE INDEX IF NOT EXISTS idx_trips_day_of_week ON trips(day_of_week);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_month ON trips(pickup_month);
CREATE INDEX IF NOT EXISTS idx_trips_duration ON trips(trip_duration);
CREATE INDEX IF NOT EXISTS idx_trips_distance ON trips(trip_distance_km);
CREATE INDEX IF NOT EXISTS idx_trips_speed ON trips(trip_speed_km_h);
CREATE INDEX IF NOT EXISTS idx_trips_vendor ON trips(vendor_id);
CREATE INDEX IF NOT EXISTS idx_trips_passenger_count ON trips(passenger_count);

-- spatial indexes (composite for coordinates)
CREATE INDEX IF NOT EXISTS idx_trips_pickup_location ON trips(pickup_latitude, pickup_longitude);
CREATE INDEX IF NOT EXISTS idx_trips_dropoff_location ON trips(dropoff_latitude, dropoff_longitude);

-- analytics views for common queries
CREATE VIEW IF NOT EXISTS hourly_stats AS
SELECT 
    pickup_hour,
    COUNT(*) as trip_count,
    AVG(trip_duration) / 60 as avg_duration_minutes,
    AVG(trip_distance_km) as avg_distance_km,
    AVG(trip_speed_km_h) as avg_speed_km_h,
    AVG(passenger_count) as avg_passengers
FROM trips
GROUP BY pickup_hour
ORDER BY pickup_hour;

CREATE VIEW IF NOT EXISTS daily_patterns AS
SELECT 
    day_of_week,
    CASE day_of_week
        WHEN 0 THEN 'Monday'
        WHEN 1 THEN 'Tuesday'
        WHEN 2 THEN 'Wednesday'
        WHEN 3 THEN 'Thursday'
        WHEN 4 THEN 'Friday'
        WHEN 5 THEN 'Saturday'
        WHEN 6 THEN 'Sunday'
    END as day_name,
    COUNT(*) as trip_count,
    AVG(trip_duration) / 60 as avg_duration_minutes,
    AVG(trip_distance_km) as avg_distance_km,
    AVG(trip_speed_km_h) as avg_speed_km_h,
    AVG(passenger_count) as avg_passengers
FROM trips
GROUP BY day_of_week
ORDER BY day_of_week;

CREATE VIEW IF NOT EXISTS popular_routes AS
SELECT 
    ROUND(pickup_latitude, 3) as pickup_lat,
    ROUND(pickup_longitude, 3) as pickup_lon,
    ROUND(dropoff_latitude, 3) as dropoff_lat,
    ROUND(dropoff_longitude, 3) as dropoff_lon,
    COUNT(*) as trip_count,
    AVG(trip_duration) / 60 as avg_duration_minutes,
    AVG(trip_distance_km) as avg_distance_km
FROM trips
GROUP BY 
    ROUND(pickup_latitude, 3),
    ROUND(pickup_longitude, 3),
    ROUND(dropoff_latitude, 3),
    ROUND(dropoff_longitude, 3)
HAVING COUNT(*) > 5
ORDER BY trip_count DESC;

-- system metadata table
CREATE TABLE IF NOT EXISTS system_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- snsert initial metadata
INSERT OR REPLACE INTO system_metadata (key, value, description) VALUES
('database_version', '1.0', 'Current database schema version'),
('last_data_load', datetime('now'), 'Timestamp of last data load'),
('total_trips', '0', 'Total number of trips in database'),
('data_source', 'NYC Taxi Trip Dataset', 'Source of the trip data'),
('schema_created', datetime('now'), 'When this schema was created');
>>>>>>> 05d2109 (feat: database setup and testing scripts for mobility analysis)
