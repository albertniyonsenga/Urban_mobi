"""API routes exposing Sonia's custom algorithms.
This file provides FastAPI endpoints for custom algorithms that work with the database.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db, execute_query
from algorithm.custom_algorithm import (
    pickup_hour_frequency, 
    rank_clusters_by_total_duration,
    manual_kmeans_clustering,
    custom_trip_sorter
)

router = APIRouter(prefix="/custom", tags=["custom"])

@router.get("/hourly-pickups")
async def get_hourly_pickups(
    day_of_week: Optional[int] = Query(None, ge=0, le=6, description="Filter by day of week (0=Monday, 6=Sunday)"),
    db: Session = Depends(get_db)
):
    """Get hourly pickup frequency using custom algorithm."""
    try:
        # build query to get pickup data
        query = "SELECT pickup_datetime FROM trips WHERE 1=1"
        params = {}
        
        if day_of_week is not None:
            query += " AND day_of_week = :day_of_week"
            params['day_of_week'] = day_of_week
        
        # execute query and get results
        results = execute_query(query, params)
        
        if not results:
            return {"hourly_pickups": {}, "message": "No data found"}
        
        # convert to list of trip dictionaries for the custom algorithm
        trips = [{"pickup_datetime": row["pickup_datetime"]} for row in results]
        
        # use custom algorithm
        frequency = pickup_hour_frequency(trips, timestamp_key="pickup_datetime")
        
        return {
            "hourly_pickups": frequency,
            "total_trips": len(trips),
            "filters": {"day_of_week": day_of_week}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing hourly pickups: {str(e)}")

@router.get("/cluster-ranking")
async def get_cluster_ranking(
    n_clusters: int = Query(5, ge=2, le=20, description="Number of clusters to create"),
    cluster_type: str = Query("pickup", description="Type of clustering: 'pickup' or 'dropoff'"),
    db: Session = Depends(get_db)
):
    """Rank clusters by total trip duration using custom algorithm."""
    try:
        # get coordinates and durations from database
        if cluster_type == "pickup":
            query = "SELECT pickup_latitude, pickup_longitude, trip_duration FROM trips"
        else:
            query = "SELECT dropoff_latitude, dropoff_longitude, trip_duration FROM trips"
        
        results = execute_query(query)
        
        if not results:
            return {"clusters": [], "message": "No data found for clustering"}
        
        # convert to format expected by custom algorithm
        trips = []
        for row in results:
            if cluster_type == "pickup":
                trips.append({
                    "pickup_latitude": row["pickup_latitude"],
                    "pickup_longitude": row["pickup_longitude"],
                    "trip_duration": row["trip_duration"]
                })
            else:
                trips.append({
                    "dropoff_latitude": row["dropoff_latitude"],
                    "dropoff_longitude": row["dropoff_longitude"],
                    "trip_duration": row["trip_duration"]
                })
        
        # create clusters using custom K-means
        clusters = manual_kmeans_clustering(trips, n_clusters, cluster_type)
        
        # build cluster map for ranking
        cluster_map = {}
        for cluster_id, cluster_data in clusters.items():
            cluster_map[cluster_id] = [
                {"trip_duration": trip["trip_duration"]} 
                for trip in cluster_data["trips"]
            ]
        
        # rank clusters by total duration
        ranked_clusters = rank_clusters_by_total_duration(cluster_map)
        
        # format response
        ranked_result = []
        for cluster_id, total_duration in ranked_clusters:
            cluster_info = clusters[cluster_id]
            ranked_result.append({
                "cluster_id": cluster_id,
                "total_duration": total_duration,
                "center_lat": cluster_info["center"][0],
                "center_lon": cluster_info["center"][1],
                "trip_count": len(cluster_info["trips"]),
                "avg_duration": total_duration / len(cluster_info["trips"]) if cluster_info["trips"] else 0
            })
        
        return {
            "ranked_clusters": ranked_result,
            "cluster_type": cluster_type,
            "total_clusters": n_clusters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in cluster ranking: {str(e)}")

@router.get("/trip-sorting")
async def get_sorted_trips(
    sort_by: str = Query("duration", description="Sort by: 'duration', 'distance', or 'speed'"),
    limit: int = Query(100, ge=1, le=1000, description="Number of trips to return"),
    order: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    db: Session = Depends(get_db)
):
    """Sort trips using custom sorting algorithm."""
    try:
        # get trip data from database
        query = """
            SELECT 
                id, trip_duration, trip_distance_km, trip_speed_km_h,
                pickup_latitude, pickup_longitude
            FROM trips 
            WHERE trip_duration IS NOT NULL 
            AND trip_distance_km IS NOT NULL
            LIMIT :limit
        """
        
        results = execute_query(query, {"limit": limit * 2})  # Get more for sampling
        
        if not results:
            return {"sorted_trips": [], "message": "No trip data found"}
        
        # convert to format for custom algorithm
        trips = []
        for row in results:
            trips.append({
                "id": row["id"],
                "trip_duration": row["trip_duration"],
                "trip_distance_km": row["trip_distance_km"],
                "trip_speed_km_h": row["trip_speed_km_h"],
                "pickup_latitude": row["pickup_latitude"],
                "pickup_longitude": row["pickup_longitude"]
            })
        
        # use custom sorting algorithm
        sorted_trips = custom_trip_sorter(trips, sort_by=sort_by, order=order)
        
        # format response
        formatted_trips = []
        for trip in sorted_trips[:limit]:  # limit after sorting
            formatted_trips.append({
                "id": trip["id"],
                "trip_duration_minutes": round(trip["trip_duration"] / 60, 2),
                "trip_distance_km": round(trip["trip_distance_km"], 2),
                "trip_speed_km_h": round(trip["trip_speed_km_h"], 2),
                "pickup_location": {
                    "lat": trip["pickup_latitude"],
                    "lon": trip["pickup_longitude"]
                }
            })
        
        return {
            "sorted_trips": formatted_trips,
            "sort_by": sort_by,
            "order": order,
            "total_sorted": len(formatted_trips)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in trip sorting: {str(e)}")

@router.get("/peak-analysis")
async def get_peak_analysis(
    db: Session = Depends(get_db)
):
    """Custom algorithm to identify peak hours and patterns."""
    try:
        # get hourly data for analysis
        query = """
            SELECT 
                pickup_hour,
                COUNT(*) as trip_count,
                AVG(trip_duration) as avg_duration,
                AVG(trip_distance_km) as avg_distance,
                AVG(trip_speed_km_h) as avg_speed
            FROM trips
            GROUP BY pickup_hour
            ORDER BY pickup_hour
        """
        
        results = execute_query(query)
        
        if not results:
            return {"peaks": [], "message": "No data found for analysis"}
        
        # convert to format for analysis
        hourly_data = []
        for row in results:
            hourly_data.append({
                "hour": row["pickup_hour"],
                "trip_count": row["trip_count"],
                "avg_duration": row["avg_duration"],
                "avg_distance": row["avg_distance"],
                "avg_speed": row["avg_speed"]
            })
        
        # custom peak detection algorithm
        peaks = []
        for i, hour_data in enumerate(hourly_data):
            if i == 0 or i == len(hourly_data) - 1:
                continue
                
            prev_count = hourly_data[i-1]["trip_count"]
            current_count = hour_data["trip_count"]
            next_count = hourly_data[i+1]["trip_count"]
            
            # simple peak detection: current count is higher than neighbors
            if current_count > prev_count and current_count > next_count:
                peaks.append({
                    "hour": hour_data["hour"],
                    "trip_count": current_count,
                    "peak_type": "morning" if hour_data["hour"] < 12 else "afternoon/evening",
                    "intensity": current_count / ((prev_count + next_count) / 2) if (prev_count + next_count) > 0 else 1
                })
        
        # sort peaks by intensity
        peaks_sorted = sorted(peaks, key=lambda x: x["intensity"], reverse=True)
        
        return {
            "peak_hours": peaks_sorted,
            "total_peaks": len(peaks_sorted),
            "analysis_based_on": f"{len(hourly_data)} hours of data"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in peak analysis: {str(e)}")

@router.get("/algorithm-info") # just for quick reference
async def get_algorithm_info():
    """Get information about the custom algorithms available."""
    return {
        "algorithms": [
            {
                "name": "Hourly Pickup Frequency",
                "endpoint": "/custom/hourly-pickups",
                "description": "Custom frequency counter for pickup hours",
                "parameters": ["day_of_week (optional)"]
            },
            {
                "name": "Cluster Ranking",
                "endpoint": "/custom/cluster-ranking", 
                "description": "Manual K-means clustering and duration-based ranking",
                "parameters": ["n_clusters", "cluster_type"]
            },
            {
                "name": "Trip Sorting",
                "endpoint": "/custom/trip-sorting",
                "description": "Custom sorting algorithm for trips",
                "parameters": ["sort_by", "limit", "order"]
            },
            {
                "name": "Peak Analysis",
                "endpoint": "/custom/peak-analysis", 
                "description": "Custom peak detection in hourly patterns",
                "parameters": "None"
            }
        ],
        "custom_implementation": "All algorithms implemented manually without sklearn/pandas built-ins"
    }
