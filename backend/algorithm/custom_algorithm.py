"""Custom algorithm implementations for the Urban_mobi project.

Constraints:
- Algorithms are implemented manually without using specialized libraries
  (no heapq, collections.Counter, numpy sorting helpers, pandas, etc.).

Provided functions:
- selection_sort_trips(trips, key): selection-sort a list of trip dicts by numeric key
- pickup_hour_frequency(trips, timestamp_key): count pickups per hour (0-23)
- rank_clusters_by_total_duration(cluster_map): rank clusters by total trip duration
- haversine_distance(lat1, lon1, lat2, lon2): compute great-circle distance in km

All functions accept and return plain Python data structures so they are
easy to integrate into any backend or test harness.
"""
from datetime import datetime
from math import radians, sin, cos, asin, sqrt
from typing import List, Dict, Any, Tuple


def selection_sort_trips(trips: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
	"""
	Sort trips by numeric `key` using selection sort (ascending).

	Inputs:
	- trips: list of dict-like objects that contain `key` with numeric values
	- key: the dict key to sort by

	Returns a new list (does not mutate the input list).

	Time complexity: O(n^2)
	Space complexity: O(n) (we create a shallow copy)
	"""
	n = len(trips)
	arr = trips.copy()
	for i in range(n):
		min_idx = i
		for j in range(i + 1, n):
			a = arr[j].get(key)
			b = arr[min_idx].get(key)
			if a is None:
				continue
			if b is None or a < b:
				min_idx = j
		if min_idx != i:
			arr[i], arr[min_idx] = arr[min_idx], arr[i]
	return arr


def pickup_hour_frequency(trips: List[Dict[str, Any]], timestamp_key: str = "pickup_datetime") -> Dict[int, int]:
	"""
	Count number of pickups per hour (0-23). Timestamp is expected to be a
	string parseable by datetime.fromisoformat or common formats.

	Returns: dict hour -> count

	Time complexity: O(n)
	Space complexity: O(k) where k<=24
	"""
	counts: Dict[int, int] = {h: 0 for h in range(24)}
	for trip in trips:
		ts = trip.get(timestamp_key)
		if ts is None:
			continue
		dt = None
		if isinstance(ts, datetime):
			dt = ts
		else:
			s = str(ts)
			try:
				dt = datetime.fromisoformat(s)
			except Exception:
				try:
					dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
				except Exception:
					continue
		counts[dt.hour] = counts.get(dt.hour, 0) + 1
	return counts


def rank_clusters_by_total_duration(cluster_map: Dict[Any, List[Dict[str, Any]]]) -> List[Tuple[Any, float]]:
	"""
	Given a mapping cluster_id -> list of trip dicts (each with 'trip_duration' numeric),
	return a list of tuples (cluster_id, total_duration) sorted descending by total_duration.

	Implemented without using builtin `sorted` to satisfy the manual-algorithm requirement.

	Time complexity: O(c^2) for c clusters due to selection-sort style ranking + O(n) to sum durations
	Space complexity: O(c)
	"""
	summaries: List[Tuple[Any, float]] = []
	for cid, trips in cluster_map.items():
		total = 0.0
		for t in trips:
			d = t.get("trip_duration")
			try:
				if d is None:
					continue
				total += float(d)
			except Exception:
				continue
		summaries.append((cid, total))

	ranked: List[Tuple[Any, float]] = summaries.copy()
	c = len(ranked)
	for i in range(c):
		max_idx = i
		for j in range(i + 1, c):
			if ranked[j][1] > ranked[max_idx][1]:
				max_idx = j
		if max_idx != i:
			ranked[i], ranked[max_idx] = ranked[max_idx], ranked[i]
	return ranked


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	"""
	Compute the great-circle distance between two points (lat/lon in decimal degrees).
	Returns distance in kilometers.

	Uses the haversine formula.

	Time complexity: O(1)
	Space complexity: O(1)
	"""
	lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
	dlat = lat2 - lat1
	dlon = lon2 - lon1
	a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
	c = 2 * asin(sqrt(a))
	R_km = 6371.0
	return R_km * c


if __name__ == "__main__":
	sample_trips = [
		{"id": 1, "trip_duration": 300, "pickup_datetime": "2025-10-15T08:12:00"},
		{"id": 2, "trip_duration": 120, "pickup_datetime": "2025-10-15 09:05:00"},
		{"id": 3, "trip_duration": 600, "pickup_datetime": "2025-10-15T08:45:00"},
	]
	print("Selection sort by trip_duration:", selection_sort_trips(sample_trips, "trip_duration"))
	print("Pickup hour frequency:", pickup_hour_frequency(sample_trips))
	clusters = {"A": [sample_trips[0], sample_trips[2]], "B": [sample_trips[1]]}
	print("Cluster ranking:", rank_clusters_by_total_duration(clusters))
	print("Haversine NY->SF (approx):", haversine_distance(40.7128, -74.0060, 37.7749, -122.4194))

