from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from core.database import get_db

router = APIRouter(prefix="/clusters", tags=["clusters"])

@router.get("/pickup")
async def get_pickup_clusters(
    n_clusters: int = Query(10, ge=2, le=50),
    db: Session = Depends(get_db)
):
    """
    Get pickup location clusters
    """
    try:
        # get pickup coordinates
        query = text("SELECT pickup_latitude, pickup_longitude FROM trips WHERE pickup_latitude IS NOT NULL")
        results = db.execute(query).fetchall()
        
        if len(results) == 0:
            return {"clusters": [], "message": "No data available"}
        
        # convert to DataFrame
        df = pd.DataFrame(results, columns=['pickup_latitude', 'pickup_longitude'])
        
        # simple clustering by rounding coordinates (temporary implementation)
        df['cluster_lat'] = df['pickup_latitude'].round(2)
        df['cluster_lon'] = df['pickup_longitude'].round(2)
        
        clusters = []
        for (lat, lon), group in df.groupby(['cluster_lat', 'cluster_lon']):
            if len(clusters) >= n_clusters:
                break
                
            clusters.append({
                "cluster_id": len(clusters),
                "center_lat": float(lat),
                "center_lon": float(lon),
                "point_count": len(group),
                "points": group[['pickup_latitude', 'pickup_longitude']].head(10).to_dict('records')
            })
        
        return {
            "clusters": clusters,
            "total_clusters": len(clusters),
            "total_points": len(df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in clustering: {str(e)}")
    