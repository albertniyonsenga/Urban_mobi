"""
Quick test script to verify the database is working
"""

import sqlite3
import pandas as pd
from colorama import init, Fore

init(autoreset=True)

def test_database():
    """Test basic database functionality"""
    print(Fore.CYAN + "Testing Database Connection\n")
    
    try:
        # connect to database
        conn = sqlite3.connect('mobility.db')
        cursor = conn.cursor()
        
        # check if database exists and has data
        print("1. Checking database existence...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"   Tables found: {tables}")
        
        # check trip count
        print("2. Checking trip data...")
        cursor.execute("SELECT COUNT(*) FROM trips")
        trip_count = cursor.fetchone()[0]
        print(f"   Total trips: {trip_count:,}")
        
        # check sample data
        print("3. Checking sample data...")
        cursor.execute("SELECT * FROM trips LIMIT 5")
        columns = [description[0] for description in cursor.description]
        sample_data = cursor.fetchall()
        print(f"   Columns: {columns}")
        print(f"   Sample rows: {len(sample_data)}")
        
        # test views
        print("4. Testing analytics views...")
        cursor.execute("SELECT * FROM hourly_stats LIMIT 5")
        hourly_data = cursor.fetchall()
        print(f"   Hourly stats: {len(hourly_data)} entries")
        
        # test a complex query
        print("5. Testing complex query...")
        cursor.execute("""
            SELECT 
                day_of_week,
                COUNT(*) as trips,
                AVG(trip_duration)/60 as avg_duration_min
            FROM trips 
            GROUP BY day_of_week 
            ORDER BY day_of_week
        """)
        daily_stats = cursor.fetchall()
        print(f"   Daily stats: {len(daily_stats)} days")
        
        conn.close()
        
        print("\nAll database tests passed!")
        return True
        
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

def test_api_queries():
    """Test queries that will be used by the API"""
    print(Fore.CYAN + "\nTesting API Queries\n")
    
    try:
        conn = sqlite3.connect('mobility.db')
        
        # query1 - summary statistics
        print("1. Testing summary query...")
        summary_df = pd.read_sql("""
            SELECT 
                COUNT(*) as total_trips,
                AVG(trip_duration)/60 as avg_duration_minutes,
                AVG(trip_distance_km) as avg_distance_km,
                AVG(trip_speed_km_h) as avg_speed_km_h,
                AVG(passenger_count) as avg_passengers
            FROM trips
        """, conn)
        print(f"   Summary: {len(summary_df)} result")
        print(f"      Total trips: {summary_df['total_trips'].iloc[0]:,}")
        
        # query2 - hourly distribution
        print("2. Testing hourly distribution...")
        hourly_df = pd.read_sql("SELECT * FROM hourly_stats", conn)
        print(f"   Hourly stats: {len(hourly_df)} hours")
        
        # query3 - daily patterns
        print("3. Testing daily patterns...")
        daily_df = pd.read_sql("SELECT * FROM daily_patterns", conn)
        print(f"   Daily patterns: {len(daily_df)} days")
        
        # query4 - filtered query (example for API)
        print("4. Testing filtered query...")
        filtered_df = pd.read_sql("""
            SELECT 
                COUNT(*) as trip_count,
                AVG(trip_duration)/60 as avg_duration
            FROM trips 
            WHERE pickup_hour BETWEEN 8 AND 10
            AND day_of_week = 0
        """, conn)
        print(f"   Filtered results: {filtered_df['trip_count'].iloc[0]:,} trips")
        
        conn.close()
        
        print("\nAll API query tests passed!")
        return True
        
    except Exception as e:
        print(f"API query test failed: {e}")
        return False

if __name__ == "__main__":
    print(Fore.MAGENTA + "\nUrban Mobility Database Test Suite\n")
    
    # Run tests
    db_ok = test_database()
    api_ok = test_api_queries()
    
    if db_ok and api_ok:
        print("\nALL TESTS PASSED! Your database is ready for the backend API.")
    else:
        print("\nSome tests failed. Please check your database setup.")