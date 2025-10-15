"""API routes exposing Sonia's custom algorithms.

This file provides lightweight functions that can be imported into the project's
FastAPI router. It intentionally avoids heavy framework coupling so the team can
adapt it to their existing `main.py` / router structure.
"""
from typing import List, Dict, Any

from algorithm.custom_algorithm import pickup_hour_frequency, rank_clusters_by_total_duration


def hourly_pickups_endpoint(trips: List[Dict[str, Any]], timestamp_key: str = "pickup_datetime") -> Dict[int, int]:
    """Return hourly pickup frequency map for the provided trips.

    This function is route-agnostic: the backend should call it and return JSON.
    """
    return pickup_hour_frequency(trips, timestamp_key=timestamp_key)


def rank_clusters_endpoint(cluster_map: Dict[Any, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Rank clusters by total trip duration and return JSON-serializable list.

    Input: cluster_map: cluster_id -> list of trip dicts (each with 'trip_duration')
    Output: list of {"cluster_id": id, "total_duration": x} sorted descending.
    """
    ranked = rank_clusters_by_total_duration(cluster_map)
    return [{"cluster_id": cid, "total_duration": total} for cid, total in ranked]
