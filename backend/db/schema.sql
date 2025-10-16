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