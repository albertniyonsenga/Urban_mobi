-- 1. BASIC AGGREGATIONS
-- Total trips by vendor
SELECT 
    v.vendor_name,
    COUNT(*) as total_trips,
    ROUND(AVG(t.trip_duration)/60, 2) as avg_duration_min,
    ROUND(AVG(t.trip_distance_km), 2) as avg_distance_km,
    ROUND(AVG(t.trip_speed_km_h), 2) as avg_speed_km_h
FROM trips t
JOIN vendors v ON t.vendor_id = v.vendor_id
GROUP BY v.vendor_name;

-- 2. TEMPORAL ANALYSIS
-- Trips by hour of day
SELECT 
    strftime('%H', pickup_datetime) as hour,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_duration)/60, 2) as avg_duration_min
FROM trips
GROUP BY hour
ORDER BY hour;

-- Trips by day of week
SELECT 
    CASE 
        WHEN strftime('%w', pickup_datetime) = '0' THEN 'Sunday'
        WHEN strftime('%w', pickup_datetime) = '1' THEN 'Monday'
        WHEN strftime('%w', pickup_datetime) = '2' THEN 'Tuesday'
        WHEN strftime('%w', pickup_datetime) = '3' THEN 'Wednesday'
        WHEN strftime('%w', pickup_datetime) = '4' THEN 'Thursday'
        WHEN strftime('%w', pickup_datetime) = '5' THEN 'Friday'
        WHEN strftime('%w', pickup_datetime) = '6' THEN 'Saturday'
    END as day_name,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_duration)/60, 2) as avg_duration_min
FROM trips
GROUP BY day_name
ORDER BY MIN(strftime('%w', pickup_datetime));

-- 3. SPATIAL ANALYSIS
-- Top 10 pickup locations by trip count
SELECT 
    l.latitude,
    l.longitude,
    COUNT(*) as pickup_count
FROM trips t
JOIN locations l ON t.pickup_location_id = l.location_id
GROUP BY l.latitude, l.longitude
ORDER BY pickup_count DESC
LIMIT 10;

-- Top 10 dropoff locations by trip count
SELECT 
    l.latitude,
    l.longitude,
    COUNT(*) as dropoff_count
FROM trips t
JOIN locations l ON t.dropoff_location_id = l.location_id
GROUP BY l.latitude, l.longitude
ORDER BY dropoff_count DESC
LIMIT 10;

-- 4. TRIP CHARACTERISTICS
-- Trip duration distribution
SELECT 
    CASE 
        WHEN trip_duration < 300 THEN '0-5 min'
        WHEN trip_duration < 600 THEN '5-10 min'
        WHEN trip_duration < 900 THEN '10-15 min'
        WHEN trip_duration < 1800 THEN '15-30 min'
        WHEN trip_duration < 3600 THEN '30-60 min'
        ELSE '60+ min'
    END as duration_range,
    COUNT(*) as trip_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trips), 2) as percentage
FROM trips
GROUP BY duration_range
ORDER BY MIN(trip_duration);

-- Distance distribution
SELECT 
    CASE 
        WHEN trip_distance_km < 1 THEN '0-1 km'
        WHEN trip_distance_km < 3 THEN '1-3 km'
        WHEN trip_distance_km < 5 THEN '3-5 km'
        WHEN trip_distance_km < 10 THEN '5-10 km'
        WHEN trip_distance_km < 20 THEN '10-20 km'
        ELSE '20+ km'
    END as distance_range,
    COUNT(*) as trip_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trips), 2) as percentage
FROM trips
GROUP BY distance_range
ORDER BY MIN(trip_distance_km);

-- 5. SPEED ANALYSIS
-- Average speed by hour
SELECT 
    strftime('%H', pickup_datetime) as hour,
    ROUND(AVG(trip_speed_km_h), 2) as avg_speed,
    COUNT(*) as trip_count
FROM trips
WHERE trip_speed_km_h > 0 AND trip_speed_km_h < 100  -- Filter outliers
GROUP BY hour
ORDER BY hour;

-- 6. PASSENGER ANALYSIS
-- Trips by passenger count
SELECT 
    passenger_count,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_duration)/60, 2) as avg_duration_min,
    ROUND(AVG(trip_distance_km), 2) as avg_distance_km
FROM trips
GROUP BY passenger_count
ORDER BY passenger_count;

-- 7. PEAK HOUR ANALYSIS
-- Busiest hours for pickups
SELECT 
    strftime('%H', pickup_datetime) as hour,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_duration)/60, 2) as avg_duration_min,
    ROUND(AVG(trip_speed_km_h), 2) as avg_speed_km_h
FROM trips
GROUP BY hour
ORDER BY trip_count DESC
LIMIT 5;

-- 8. SPATIOTEMPORAL QUERIES
-- Hourly trip patterns for top pickup locations
WITH top_pickups AS (
    SELECT 
        pickup_location_id,
        COUNT(*) as pickup_count
    FROM trips
    GROUP BY pickup_location_id
    ORDER BY pickup_count DESC
    LIMIT 5
)
SELECT 
    l.latitude,
    l.longitude,
    strftime('%H', t.pickup_datetime) as hour,
    COUNT(*) as hourly_trips
FROM trips t
JOIN top_pickups tp ON t.pickup_location_id = tp.pickup_location_id
JOIN locations l ON t.pickup_location_id = l.location_id
GROUP BY l.latitude, l.longitude, hour
ORDER BY l.latitude, l.longitude, hour;

-- 9. EFFICIENCY METRICS
-- Most efficient trips (highest speed during peak hours)
SELECT 
    trip_id,
    trip_duration,
    trip_distance_km,
    trip_speed_km_h,
    pickup_datetime
FROM trips
WHERE strftime('%H', pickup_datetime) IN ('08', '09', '17', '18')  -- Peak hours
    AND trip_speed_km_h > 0
    AND trip_distance_km > 1
ORDER BY trip_speed_km_h DESC
LIMIT 10;

-- 10. CORRELATION ANALYSIS
-- Relationship between distance and duration
SELECT 
    ROUND(trip_distance_km, 1) as distance_km,
    ROUND(AVG(trip_duration)/60, 2) as avg_duration_min,
    COUNT(*) as sample_size
FROM trips
WHERE trip_distance_km BETWEEN 1 AND 20
    AND trip_duration BETWEEN 60 AND 3600
GROUP BY ROUND(trip_distance_km, 1)
ORDER BY distance_km;