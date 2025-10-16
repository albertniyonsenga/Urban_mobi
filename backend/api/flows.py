from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from core.database import get_db

router = APIRouter(prefix="/flows", tags=["flows"])

@router.get("/top-pairs")
async def get_top_flow_pairs(
    limit: int = Query(20, ge=1, le=100),
    hour_start: Optional[int] = Query(None, ge=0, le=23),
    hour_end: Optional[int] = Query(None, ge=0, le=23),
    db: Session = Depends(get_db)
):
    """
    Get top origin-destination flow pairs
    """
    try:
        query = text("""
        SELECT 
            ROUND(pickup_latitude, 3) as pickup_lat,
            ROUND(pickup_longitude, 3) as pickup_lon,
            ROUND(dropoff_latitude, 3) as dropoff_lat,
            ROUND(dropoff_longitude, 3) as dropoff_lon,
            COUNT(*) as trip_count,
            AVG(trip_duration) as avg_duration,
            AVG(trip_distance_km) as avg_distance
        FROM trips
        WHERE pickup_latitude IS NOT NULL AND dropoff_latitude IS NOT NULL
        """)
        
        params = {}
        
        if hour_start is not None and hour_end is not None:
            query = text(str(query) + " AND pickup_hour BETWEEN :hour_start AND :hour_end")
            params['hour_start'] = hour_start
            params['hour_end'] = hour_end
        
        query = text(str(query) + """
        GROUP BY 
            ROUND(pickup_latitude, 3),
            ROUND(pickup_longitude, 3),
            ROUND(dropoff_latitude, 3), 
            ROUND(dropoff_longitude, 3)
        ORDER BY trip_count DESC
        LIMIT :limit
        """)
        
        params['limit'] = limit
        
        results = db.execute(query, params).fetchall()
        
        flows = []
        for row in results:
            flows.append({
                "pickup": {"lat": row[0], "lon": row[1]},
                "dropoff": {"lat": row[2], "lon": row[3]},
                "trip_count": row[4],
                "avg_duration_minutes": round((row[5] or 0) / 60, 2),
                "avg_distance_km": round(row[6] or 0, 2)
            })
        
        return {
            "flows": flows,
            "total_flows": len(flows),
            "filters_applied": {
                "hour_start": hour_start,
                "hour_end": hour_end
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in flow analysis: {str(e)}")
    