from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import get_db

router = APIRouter(prefix="/temporal", tags=["temporal"])

@router.get("/hourly-distribution")
async def get_hourly_distribution(db: Session = Depends(get_db)):
    """
    Get trip distribution by hour of day
    """
    query = text("""
    SELECT 
        pickup_hour,
        COUNT(*) as trip_count,
        AVG(trip_duration) as avg_duration,
        AVG(trip_speed_km_h) as avg_speed
    FROM trips
    GROUP BY pickup_hour
    ORDER BY pickup_hour
    """)
    
    results = db.execute(query).fetchall()
    
    hourly_data = []
    for row in results:
        hourly_data.append({
            "hour": row[0],
            "trip_count": row[1],
            "avg_duration_minutes": round((row[2] or 0) / 60, 2),
            "avg_speed_km_h": round(row[3] or 0, 2)
        })
    
    return {"hourly_distribution": hourly_data}

@router.get("/daily-patterns")
async def get_daily_patterns(db: Session = Depends(get_db)):
    """
    Get trip patterns by day of week
    """
    query = text("""
    SELECT 
        day_of_week,
        COUNT(*) as trip_count,
        AVG(trip_duration) as avg_duration,
        AVG(trip_speed_km_h) as avg_speed,
        AVG(passenger_count) as avg_passengers
    FROM trips
    GROUP BY day_of_week
    ORDER BY day_of_week
    """)
    
    results = db.execute(query).fetchall()
    
    daily_data = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for row in results:
        daily_data.append({
            "day_of_week": row[0],
            "day_name": days[row[0]] if row[0] < len(days) else "Unknown",
            "trip_count": row[1],
            "avg_duration_minutes": round((row[2] or 0) / 60, 2),
            "avg_speed_km_h": round(row[3] or 0, 2),
            "avg_passengers": round(row[4] or 0, 2)
        })
    
    return {"daily_patterns": daily_data}
