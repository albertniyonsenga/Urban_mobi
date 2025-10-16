from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from core.database import get_db
import logging

router = APIRouter(prefix="/summary", tags=["summary"])
logger = logging.getLogger(__name__)

@router.get("/overview")
async def get_summary_overview(
    hour_start: Optional[int] = Query(None, ge=0, le=23),
    hour_end: Optional[int] = Query(None, ge=0, le=23),
    day_of_week: Optional[int] = Query(None, ge=0, le=6),
    db: Session = Depends(get_db)
):
    """
    Get overall summary statistics with optional time filtering
    """
    try:
        # build query based on filters
        query = text("""
        SELECT 
            COUNT(*) as total_trips,
            AVG(trip_duration) / 60 as avg_duration_minutes,
            AVG(trip_distance_km) as avg_distance_km,
            AVG(trip_speed_km_h) as avg_speed_km_h,
            AVG(passenger_count) as avg_passengers
        FROM trips
        WHERE 1=1
        """)
        
        # build WHERE conditions dynamically
        where_conditions = []
        params = {}
        
        if hour_start is not None and hour_end is not None:
            where_conditions.append("pickup_hour BETWEEN :hour_start AND :hour_end")
            params['hour_start'] = hour_start
            params['hour_end'] = hour_end
        
        if day_of_week is not None:
            where_conditions.append("day_of_week = :day_of_week")
            params['day_of_week'] = day_of_week
        
        # add WHERE conditions if any
        if where_conditions:
            where_clause = " AND " + " AND ".join(where_conditions)
            query = text(str(query) + where_clause)
        
        result = db.execute(query, params).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="No data found")
        
        return {
            "total_trips": result[0],
            "avg_duration_minutes": round(result[1] or 0, 2),
            "avg_distance_km": round(result[2] or 0, 2),
            "avg_speed_km_h": round(result[3] or 0, 2),
            "avg_passengers": round(result[4] or 0, 2),
            "filters_applied": {
                "hour_start": hour_start,
                "hour_end": hour_end,
                "day_of_week": day_of_week
            }
        }
        
    except Exception as e:
        logger.error(f"Error in summary overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/busiest-hour")
async def get_busiest_hour(
    day_of_week: Optional[int] = Query(None, ge=0, le=6),
    db: Session = Depends(get_db)
):
    """
    Find the busiest hour based on trip counts
    """
    try:
        query = text("""
        SELECT pickup_hour, COUNT(*) as trip_count
        FROM trips
        WHERE 1=1
        """)
        
        params = {}
        if day_of_week is not None:
            query = text(str(query) + " AND day_of_week = :day_of_week")
            params['day_of_week'] = day_of_week
        
        query = text(str(query) + " GROUP BY pickup_hour ORDER BY trip_count DESC LIMIT 1")
        
        result = db.execute(query, params).fetchone()
        
        if not result:
            return {
                "busiest_hour": None,
                "trip_count": 0,
                "day_of_week": day_of_week
            }
        
        return {
            "busiest_hour": result[0],
            "trip_count": result[1],
            "day_of_week": day_of_week
        }
        
    except Exception as e:
        logger.error(f"Error in busiest hour: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    