from algorithm import custom_algorithm as ca


def test_selection_sort_trips():
    trips = [
        {"id": 1, "trip_duration": 10},
        {"id": 2, "trip_duration": 5},
        {"id": 3, "trip_duration": 20},
    ]
    sorted_trips = ca.selection_sort_trips(trips, "trip_duration")
    assert [t["id"] for t in sorted_trips] == [2, 1, 3]


def test_pickup_hour_frequency():
    trips = [
        {"pickup_datetime": "2025-10-15T00:01:00"},
        {"pickup_datetime": "2025-10-15T00:59:00"},
        {"pickup_datetime": "2025-10-15T13:00:00"},
    ]
    freq = ca.pickup_hour_frequency(trips)
    assert freq[0] == 2
    assert freq[13] == 1


def test_rank_clusters_by_total_duration():
    clusters = {
        "x": [{"trip_duration": 10}, {"trip_duration": 20}],
        "y": [{"trip_duration": 5}],
        "z": [{"trip_duration": 50}],
    }
    ranked = ca.rank_clusters_by_total_duration(clusters)
    assert ranked[0][0] == "z"
    assert ranked[1][0] == "x"


def test_haversine_distance():
    d = ca.haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
    assert abs(d) < 1e-6
