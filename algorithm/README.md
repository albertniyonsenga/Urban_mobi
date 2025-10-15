Custom Algorithms — Sonia's deliverable
======================================

Purpose
-------
This module contains manually implemented algorithms required by the course assignment.
You must not use library helpers for these core routines; they are intentionally simple and
reusable in the backend API.

Files
-----
- `custom_algorithm.py` — implementations and a small CLI demo
- `tests/test_custom_algorithm.py` — pytest cases that validate behavior

Provided functions and rationale
-------------------------------
1. selection_sort_trips(trips, key)
   - Description: Selection-sort a list of trip dictionaries by a numeric field (e.g., `trip_duration`).
   - Use: Small lists where an easy-to-explain manual sorter is required (assignment requirement).
   - Complexity: O(n^2) time, O(n) space (shallow copy returned).

2. pickup_hour_frequency(trips, timestamp_key="pickup_datetime")
   - Description: Build a frequency map of pickups per hour (0-23).
   - Use: Useful for generating the "Peak traffic timeline" visualization.
   - Complexity: O(n) time, O(1) extra space (24 keys).

3. rank_clusters_by_total_duration(cluster_map)
   - Description: Given mapping cluster_id -> list of trips (with `trip_duration`), compute
     total duration per cluster and rank clusters by that total using a manual selection-style sort.
   - Use: Rank mobility hotspots by total activity (duration) without using library sorts.
   - Complexity: O(c^2 + n) time where c is number of clusters and n total trips; O(c) space.

4. haversine_distance(lat1, lon1, lat2, lon2)
   - Description: Compute distance in kilometers between two points using the haversine formula.
   - Use: Compute accurate distances for derived features (e.g., fare per km, trip speed).
   - Complexity: O(1) time and space.

Integration notes (how Sonia's code plugs into the backend)
----------------------------------------------------------
- The backend should import these functions from `algorithm.custom_algorithm`.
- Suggested endpoints to use:
  - `routes_custom.py` — provide endpoints that call `rank_clusters_by_total_duration` and
    `pickup_hour_frequency` to power charts and leaderboards.
  - During data cleaning, use `haversine_distance` to compute derived features: `distance_km`,
    `fare_per_km`, and `avg_speed_kmph`.

Examples
--------
Python usage examples (from backend):

```python
from algorithm.custom_algorithm import pickup_hour_frequency, rank_clusters_by_total_duration

# trips: list of dicts loaded from database or cleaned CSV
hour_freq = pickup_hour_frequency(trips, timestamp_key='pickup_datetime')

# clusters: mapping produced by clustering routine in backend (e.g., KMeans cluster id -> trips)
ranked = rank_clusters_by_total_duration(clusters)
```

Testing
-------
Run pytest from repository root (recommended):

```bash
pip install pytest
pytest algorithm/tests/test_custom_algorithm.py
```

Academic note
-------------
Per course rules, this file contains original algorithmic implementations created by the student.
Do not auto-generate or copy these parts from external AI tools.
