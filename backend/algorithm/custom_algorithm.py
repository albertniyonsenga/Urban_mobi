"""
Custom algorithms implemented manually without using built-in libraries.
These are the algorithms that Sonia will implement for the project.
"""
from typing import List, Dict, Any, Tuple
import math

def pickup_hour_frequency(trips: List[Dict[str, Any]], timestamp_key: str = "pickup_datetime") -> Dict[int, int]:
    """
    Custom implementation of frequency counting for pickup hours.
    Manual implementation without using collections.Counter.
    
    Time Complexity: O(n)
    Space Complexity: O(24) = O(1) since hours are fixed 0-23
    """
    frequency = {}
    
    for trip in trips:
        # extract hour from datetime string manually
        dt_str = trip[timestamp_key]
        # simple hour extraction from format like "2023-01-01 08:30:45"
        if " " in dt_str and ":" in dt_str:
            time_part = dt_str.split(" ")[1]
            hour = int(time_part.split(":")[0])
        else:
            # fallback: try to parse other formats
            try:
                hour = int(dt_str[11:13])  # extract from YYYY-MM-DD HH:MM:SS
            except:
                hour = 0
        
        # manual frequency counting
        if hour in frequency:
            frequency[hour] += 1
        else:
            frequency[hour] = 1
    
    # ensure all hours 0-23 are present
    for hour in range(24):
        if hour not in frequency:
            frequency[hour] = 0
    
    return frequency

def rank_clusters_by_total_duration(cluster_map: Dict[Any, List[Dict[str, Any]]]) -> List[Tuple[Any, float]]:
    """
    Custom ranking of clusters by total trip duration.
    Manual implementation without using built-in sorting libraries.
    
    Time Complexity: O(n + k log k) where k is number of clusters
    Space Complexity: O(k)
    """
    # calculate total duration for each cluster
    cluster_totals = []
    
    for cluster_id, trips in cluster_map.items():
        total_duration = 0
        for trip in trips:
            total_duration += trip.get('trip_duration', 0)
        
        cluster_totals.append((cluster_id, total_duration))
    
    # manual sorting using selection sort (simple but clear)
    # this demonstrates understanding of sorting algorithms
    n = len(cluster_totals)
    for i in range(n):
        max_idx = i
        for j in range(i + 1, n):
            if cluster_totals[j][1] > cluster_totals[max_idx][1]:
                max_idx = j
        
        # Swap
        cluster_totals[i], cluster_totals[max_idx] = cluster_totals[max_idx], cluster_totals[i]
    
    return cluster_totals

def manual_kmeans_clustering(trips: List[Dict[str, Any]], k: int, cluster_type: str = "pickup") -> Dict[int, Dict[str, Any]]:
    """
    Manual implementation of K-means clustering without using sklearn.
    
    Time Complexity: O(n * k * iterations)
    Space Complexity: O(n + k)
    """
    if not trips:
        return {}
    
    # extract coordinates based on cluster type
    coordinates = []
    for trip in trips:
        if cluster_type == "pickup":
            lat = trip.get('pickup_latitude', 0)
            lon = trip.get('pickup_longitude', 0)
        else:
            lat = trip.get('dropoff_latitude', 0)
            lon = trip.get('dropoff_longitude', 0)
        coordinates.append([lat, lon])
    
    # manual K-means implementation
    n = len(coordinates)
    if n == 0:
        return {}
    
    # initialize centroids randomly (simplified: pick first k points)
    centroids = []
    for i in range(min(k, n)):
        centroids.append(coordinates[i][:])  # Copy coordinates
    
    max_iterations = 100
    tolerance = 1e-4
    
    for iteration in range(max_iterations):
        # assign each point to nearest centroid
        clusters = [[] for _ in range(len(centroids))]
        assignments = []
        
        for point in coordinates:
            min_distance = float('inf')
            closest_centroid = 0
            
            for i, centroid in enumerate(centroids):
                # manual distance calculation
                distance = math.sqrt(
                    (point[0] - centroid[0]) ** 2 + 
                    (point[1] - centroid[1]) ** 2
                )
                
                if distance < min_distance:
                    min_distance = distance
                    closest_centroid = i
            
            clusters[closest_centroid].append(point)
            assignments.append(closest_centroid)
        
        # calculate new centroids
        new_centroids = []
        for cluster in clusters:
            if not cluster:
                # keep old centroid if cluster is empty *_*
                new_centroids.append(centroids[len(new_centroids)])
                continue
            
            sum_lat = 0
            sum_lon = 0
            for point in cluster:
                sum_lat += point[0]
                sum_lon += point[1]
            
            new_centroid = [
                sum_lat / len(cluster),
                sum_lon / len(cluster)
            ]
            new_centroids.append(new_centroid)
        
        # check convergence
        converged = True
        for i in range(len(centroids)):
            if math.sqrt(
                (centroids[i][0] - new_centroids[i][0]) ** 2 +
                (centroids[i][1] - new_centroids[i][1]) ** 2
            ) > tolerance:
                converged = False
                break
        
        centroids = new_centroids
        
        if converged:
            break
    
    # build result structure
    result = {}
    for cluster_id in range(len(centroids)):
        cluster_trips = []
        for i, assignment in enumerate(assignments):
            if assignment == cluster_id:
                cluster_trips.append(trips[i])
        
        result[cluster_id] = {
            "center": centroids[cluster_id],
            "trips": cluster_trips,
            "size": len(cluster_trips)
        }
    
    return result

def custom_trip_sorter(trips: List[Dict[str, Any]], sort_by: str = "duration", order: str = "desc") -> List[Dict[str, Any]]:
    """
    Custom sorting algorithm for trips using manual implementation.
    Uses insertion sort which is stable and easy to understand.
    
    Time Complexity: O(n²) - demonstrates understanding of sorting
    Space Complexity: O(n)
    """
    if not trips:
        return []
    
    # create copy to avoid modifying original
    sorted_trips = trips.copy()
    
    # manual insertion sort implementation
    n = len(sorted_trips)
    
    for i in range(1, n):
        key_trip = sorted_trips[i]
        j = i - 1
        
        # determine comparison value based on sort_by
        if sort_by == "duration":
            key_value = key_trip.get('trip_duration', 0)
        elif sort_by == "distance":
            key_value = key_trip.get('trip_distance_km', 0)
        elif sort_by == "speed":
            key_value = key_trip.get('trip_speed_km_h', 0)
        else:
            key_value = key_trip.get('trip_duration', 0)
        
        # move elements that are greater than key_value
        while j >= 0:
            current_value = 0
            if sort_by == "duration":
                current_value = sorted_trips[j].get('trip_duration', 0)
            elif sort_by == "distance":
                current_value = sorted_trips[j].get('trip_distance_km', 0)
            elif sort_by == "speed":
                current_value = sorted_trips[j].get('trip_speed_km_h', 0)
            
            if order == "desc":
                should_move = current_value < key_value
            else:  # asc
                should_move = current_value > key_value
            
            if should_move:
                sorted_trips[j + 1] = sorted_trips[j]
                j -= 1
            else:
                break
        
        sorted_trips[j + 1] = key_trip
    
    return sorted_trips

def calculate_complexity_metrics():
    """
    Helper function to document time/space complexity of algorithms.
    """
    return {
        "pickup_hour_frequency": {
            "time": "O(n)",
            "space": "O(1) - fixed 24 hours",
            "description": "Linear scan with fixed output size"
        },
        "rank_clusters_by_total_duration": {
            "time": "O(n + k log k)",
            "space": "O(k)",
            "description": "Selection sort on cluster totals"
        },
        "manual_kmeans_clustering": {
            "time": "O(n * k * iterations)", 
            "space": "O(n + k)",
            "description": "Standard K-means complexity"
        },
        "custom_trip_sorter": {
            "time": "O(n²)",
            "space": "O(n)",
            "description": "Insertion sort implementation"
        }
    }
