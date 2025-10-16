import sqlite3
import csv
import os

def create_database():
    print("Building mobility.db database...")
    
    os.makedirs('backend/db', exist_ok=True)
    os.makedirs('backend/data/cleaned', exist_ok=True)
    
    conn = sqlite3.connect('backend/db/mobility.db')
    cursor = conn.cursor()
    
    with open('backend/db/schema.sql', 'r') as f:
        schema = f.read()
    cursor.executescript(schema)
    
    vendors = [
        (1, 'Creative Mobile Technologies'),
        (2, 'VeriFone Inc.')
    ]
    cursor.executemany("INSERT OR IGNORE INTO vendors VALUES (?, ?)", vendors)
    
    time_data = []
    for hour in range(24):
        if 6 <= hour <= 9:
            time_of_day = 'morning'
        elif 16 <= hour <= 19:
            time_of_day = 'evening'
        elif 10 <= hour <= 15:
            time_of_day = 'afternoon'
        elif 20 <= hour <= 23:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
        time_data.append((hour, 0, time_of_day))

    cursor.executemany("INSERT OR IGNORE INTO times (hour, minute, time_of_day) VALUES (?, ?, ?)", time_data)
    
    print("Loading cleaned data...")
    
    sample_trips = []
    
    csv_data = [
        ['id2875421', '2', '2016-03-14 17:24:55', '2016-03-14 17:32:30', '1', '-73.98215484619139', '40.76793670654297', '-73.96463012695312', '40.765602111816406', 'N', '455', '17', '14', '3', '2016', '0', '0', '1.4985207796458557', '11.856428146648529'],
        ['id2377394', '1', '2016-06-12 00:43:35', '2016-06-12 00:54:38', '1', '-73.98041534423827', '40.738563537597656', '-73.99948120117188', '40.731151580810554', 'N', '663', '0', '12', '6', '2016', '6', '1', '1.8055071687965203', '9.803658835094227'],
        ['id3858529', '2', '2016-01-19 11:35:24', '2016-01-19 12:10:48', '1', '-73.97902679443358', '40.763938903808594', '-74.00533294677734', '40.710086822509766', 'N', '2124', '11', '19', '1', '2016', '1', '0', '6.385098495252868', '10.822200839411641'],
        ['id3504673', '2', '2016-04-06 19:32:31', '2016-04-06 19:39:40', '1', '-74.01004028320312', '40.719970703125', '-74.01226806640625', '40.70671844482422', 'N', '429', '19', '6', '4', '2016', '2', '0', '1.4854984227709382', '12.465721030245636'],
        ['id2181028', '2', '2016-03-26 13:30:55', '2016-03-26 13:38:10', '1', '-73.97305297851561', '40.79320907592773', '-73.9729232788086', '40.782520294189446', 'N', '435', '13', '26', '3', '2016', '5', '1', '1.1885884593338754', '9.836594146211382']
    ]
    
    for row in csv_data:
        trip_id = row[0]
        vendor_id = int(row[1])
        pickup_datetime = row[2]
        dropoff_datetime = row[3]
        passenger_count = int(row[4])

        pickup_location_id = 1
        dropoff_location_id = 2

        store_and_fwd_flag = row[9]
        trip_duration = int(row[10])
        trip_distance_km = float(row[17])
        trip_speed_km_h = float(row[18])
        pickup_hour = int(row[11])

        pickup_date = f"{int(row[14])}-{int(row[13]):02d}-{int(row[12]):02d}"

        sample_trips.append((
            trip_id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count,
            pickup_location_id, dropoff_location_id, store_and_fwd_flag, trip_duration,
            trip_distance_km, trip_speed_km_h
        ))
    
    locations = [
        (40.7679367, -73.982155, 'both'),
        (40.7656021, -73.964630, 'both'),
        (40.7385635, -73.980415, 'both')
    ]
    cursor.executemany("INSERT OR IGNORE INTO locations (latitude, longitude, location_type) VALUES (?, ?, ?)", locations)
    
    cursor.executemany("""
        INSERT OR IGNORE INTO trips
        (trip_id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count,
         pickup_location_id, dropoff_location_id, store_and_fwd_flag, trip_duration,
         trip_distance_km, trip_speed_km_h)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_trips)
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM trips")
    trip_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM vendors")
    vendor_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM locations")
    location_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("mobility.db created successfully!")
    print(f"Contains: {trip_count} trips, {vendor_count} vendors, {location_count} locations")
    print("File: backend/db/mobility.db")

if __name__ == "__main__":
    create_database()