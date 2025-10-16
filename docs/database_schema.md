# Database Design & Implementation Documentation

### Overview
I designed and implemented a SQLite database schema to store and analyze New York City taxi trip data. The database supports efficient analytical queries for urban mobility patterns.

### Database Schema Design

**Schema Type:** Star Schema  
**Optimization:** Analytical query performance  
**Database:** SQLite

#### Tables Created:

1. **VENDORS** (Dimension Table)
   - `vendor_id` (INTEGER PRIMARY KEY)
   - `vendor_name` (TEXT)

2. **LOCATIONS** (Dimension Table) 
   - `location_id` (INTEGER PRIMARY KEY)
   - `latitude` (REAL)
   - `longitude` (REAL)
   - `zone_type` (TEXT)

3. **DATE_DIMENSION** (Dimension Table)
   - `date_id` (INTEGER PRIMARY KEY) - Format: YYYYMMDD
   - `full_date` (DATE)
   - `day_of_week` (INTEGER)
   - `day_name` (TEXT)
   - `month` (INTEGER)
   - `quarter` (INTEGER)
   - `year` (INTEGER)
   - `is_weekend` (BOOLEAN)
   - `is_holiday` (BOOLEAN)
   - `holiday_name` (TEXT)

4. **TRIPS** (Fact Table)
   - `trip_id` (INTEGER PRIMARY KEY)
   - `vendor_id` (INTEGER, FOREIGN KEY)
   - `pickup_datetime` (TIMESTAMP)
   - `dropoff_datetime` (TIMESTAMP)
   - `passenger_count` (INTEGER)
   - `pickup_location_id` (INTEGER, FOREIGN KEY)
   - `dropoff_location_id` (INTEGER, FOREIGN KEY)
   - `store_and_fwd_flag` (TEXT)
   - `trip_duration` (INTEGER)
   - `trip_distance_km` (REAL)
   - `trip_speed_km_h` (REAL)
   - `pickup_date` (INTEGER, FOREIGN KEY)

### Key Design Decisions

**Why Star Schema?**
- Optimized for analytical queries and aggregations
- Fast performance for business intelligence use cases
- Simplified query structure for dashboard visualizations

**Data Types Selection:**
- Used INTEGER for IDs and counts for optimal storage
- REAL for coordinates and decimal values
- TEXT for descriptive fields
- TIMESTAMP for precise time tracking

**Foreign Key Relationships:**
- TRIPS.vendor_id → VENDORS.vendor_id
- TRIPS.pickup_location_id → LOCATIONS.location_id  
- TRIPS.dropoff_location_id → LOCATIONS.location_id
- TRIPS.pickup_date → DATE_DIMENSION.date_id

### Implementation Details

**Database:** SQLite (.db file)
**File Created:** `mobility.db`
**Schema File:** `schema.sql`
**Sample Queries:** `samples.sql`

### Data Processing Pipeline
1. Received cleaned CSV data from @ulrichr7's data cleaning pipeline
2. Transformed and loaded into normalized tables
3. Maintained data integrity through foreign key constraints
4. Added calculated fields for analytical efficiency

### Query Optimization Features
- Foreign key relationships for data integrity
- Pre-calculated derived fields (distance, speed, duration)
- Date dimension for flexible time-based analysis
- Efficient indexing on frequently queried columns


