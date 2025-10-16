# Urban Mobility Data Explorer API Guide
This API provides analytical insights into urban mobility patterns by analyzing **where** and **when** people move within the city. The system processes trip data to uncover mobility hotspots, traffic patterns, and temporal trends that help understand urban transportation dynamics.

## Key Objectives
- Identify **mobility hotspots** (pickup & dropoff clusters)
- Analyze **traffic peaks** by hour, day, or month  
- Map **travel patterns** and origin-destination flows
- Detect emerging **transportation demands** and **congestion zones**

## Implementation Approach

### Data Foundation
The analysis leverages core trip data features:
- **Spatial**: `pickup_latitude`, `pickup_longitude`, `dropoff_latitude`, `dropoff_longitude`
- **Temporal**: `pickup_datetime`, `trip_duration`
- **Contextual**: `vendor_id`, `passenger_count`

### Analytical Methodology

#### Stage 1: Spatial Analysis
- **Geospatial clustering** using K-Means/DBSCAN to identify mobility hotspots
- **Density heatmaps** for pickup/dropoff concentration visualization
- **Origin-destination flows** to map major movement corridors

#### Stage 2: Temporal Analysis  
- **Time-series decomposition** of trip patterns by hour, day, week
- **Peak hour identification** and weekday/weekend comparisons
- **Trip frequency analysis** across temporal dimensions

#### Stage 3: Spatiotemporal Fusion
- **Dynamic hotspot evolution** tracking how zones change activity throughout day
- **Animated heatmaps** showing mobility pattern transitions
- **Interactive time filters** for exploratory analysis

### Technical Stack
- **Clustering**: K-means, duration-based ranking)
- **Visualization**: Leaflet for interactive maps
- **Analysis**: Pandas for temporal aggregation
- **Geospatial**: Coordinate-based clustering and density estimation

## API Capabilities
This API enables:
- Hotspot cluster identification and ranking
- Temporal pattern analysis with customizable time windows
- Interactive map visualization of mobility flows
- Real-time filtering by time periods and geographic zones
- Export of analytical insights for urban planning

## Use Cases
- **City Planning**: Identify transportation infrastructure needs
- **Transport Services**: Optimize fleet allocation based on demand patterns  
- **Urban Research**: Study human mobility behavior and city dynamics
- **Real-time Monitoring**: Dashboard for current mobility conditions


## Quick Start

**Base URL:** `http://localhost:8000`
**API Version:** `v1`
**Full Base URL:** `http://localhost:8000/api/v1`

```bash
# Start the server
cd backend
python main.py

# Or use uvicorn
uvicorn main:app --reload

# Test if it's working
curl http://localhost:8000/health
# Response: {"status":"healthy"}
```

## API Endpoints
| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Summary Stats** | `GET /api/v1/summary/overview`<br>`GET /api/v1/summary/busiest-hour` | Overall summary statistics<br>Find the busiest hour |
| **Temporal Analysis** | `GET /api/v1/temporal/hourly-distribution`<br>`GET /api/v1/temporal/daily-patterns` | Hourly trip distribution<br>Daily trip patterns |
| **Spatial Analysis** | `GET /api/v1/clusters/pickup`<br>`GET /api/v1/flows/top-pairs` | Pickup location clusters<br>Top origin-destination flows |
| **Custom Analytics** | `GET /api/v1/custom/hourly-pickups`<br>`GET /api/v1/custom/cluster-ranking`<br>`GET /api/v1/custom/trip-sorting` | Custom hourly pickups algorithm<br>Cluster ranking by trip duration<br>Custom trip sorting |

### API Categories & Endpoints

<details>
<summary>Summary Statistics</summary>

- `GET /api/v1/summary/overview`  
  Get overall statistics about trips
- `GET /api/v1/summary/busiest-hour`  
  Find peak activity hours
</details>

<details>
<summary>Temporal Analysis</summary>

- `GET /api/v1/temporal/hourly-distribution`  
  See how trips distribute across hours
- `GET /api/v1/temporal/daily-patterns`  
  Analyze patterns across days
</details>

<details>
<summary>Spatial Analysis</summary>

- `GET /api/v1/clusters/pickup`  
  Discover popular pickup locations
- `GET /api/v1/flows/top-pairs`  
  Find common origin-destination pairs
</details>

<details>
<summary>Custom Analytics</summary>

- `GET /api/v1/custom/hourly-pickups`  
  Advanced hourly analysis
- `GET /api/v1/custom/cluster-ranking`  
  Sophisticated cluster analysis
- `GET /api/v1/custom/trip-sorting`  
  Custom trip sorting and ranking
</details>

## About our endpoints

<details>
<summary><strong> 1. Summary Statistics</strong></summary>

#### Get Overall Summary
*Endpoint: `GET /api/v1/summary/overview`*

This endpoint Gives us the big picture - total trips, average duration, speed, and more.

**Example:**
```bash
# Basic summary
curl "http://localhost:8000/api/v1/summary/overview"

# Summary for morning rush hour (8AM-10AM)
curl "http://localhost:8000/api/v1/summary/overview?hour_start=8&hour_end=10"

# Summary for Mondays only
curl "http://localhost:8000/api/v1/summary/overview?day_of_week=0"
```

**Sample Response:**
```json
{
  "total_trips": 65,
  "avg_duration_minutes": 15.02,
  "avg_distance_km": 3.58,
  "avg_speed_km_h": 14.03,
  "avg_passengers": 1.6,
  "filters_applied": {
    "hour_start": 1,
    "hour_end": 22,
    "day_of_week": 2
  }
}
```

#### Find Busiest Hour
*Endpoint: `GET /api/v1/summary/busiest-hour`*

This endpoint help us to explore which hour has the most taxi trips.

**Example:**
```bash
# Busiest hour overall
curl "http://localhost:8000/api/v1/summary/busiest-hour"

# Busiest hour on weekends
curl "http://localhost:8000/api/v1/summary/busiest-hour?day_of_week=5"
```

**Sample Response:**
```json
{
  "busiest_hour": 9,
  "trip_count": 7,
  "day_of_week": 1
}
```
</details>

<details>
<summary><strong>2. Time-Based Analysis</strong></summary>

#### Hourly Distribution
*Endpoint: `GET /api/v1/temporal/hourly-distribution`*

This endpoint shows how trips are distributed across all 24 hours.

**Example:**
```bash
curl "http://localhost:8000/api/v1/temporal/hourly-distribution"
```

#### Daily Patterns
*Endpoint: `GET /api/v1/temporal/daily-patterns`*

This endpoint compares trip patterns across different days of the week.

**Example:**
```bash
curl "http://localhost:8000/api/v1/temporal/daily-patterns"
```
</details>

<details><summary><strong>3. Location Analysis</strong></summary>

#### Pickup Clusters
*Endpoint:`GET /api/v1/clusters/pickup`*

This endpoint groups pickup locations into clusters to find hotspots.

**Parameters:**
- `n_clusters`: How many clusters to create (2-20, default: 10)

**Example:**
```bash
# Find top 5 pickup hotspots
curl "http://localhost:8000/api/v1/clusters/pickup?n_clusters=5"
```

#### Top Origin-Destination Flows
*Endpoint: `GET /api/v1/flows/top-pairs`*

This endpoint shows the most common routes people take.

**Parameters:**
- `limit`: How many routes to show (1-100, default: 20)
- `hour_start` & `hour_end`: Filter by time range

**Example:**
```bash
# Top 10 busiest routes
curl "http://localhost:8000/api/v1/flows/top-pairs?limit=10"

# Busiest routes during evening rush hour
curl "http://localhost:8000/api/v1/flows/top-pairs?hour_start=17&hour_end=19&limit=15"
```

**Sample Response:**
```json
{
  "flows": [
    {
      "pickup": {"lat": 40.750, "lon": -73.990},
      "dropoff": {"lat": 40.770, "lon": -73.980},
      "trip_count": 450,
      "avg_duration_minutes": 12.5,
      "avg_distance_km": 3.2
    }
    // ... more flows
  ],
  "total_flows": 10,
  "filters_applied": {
    "hour_start": 17,
    "hour_end": 19
  }
}

```
</details>

<details>
<summary><strong>4. Custom Algorithms</strong></summary>

#### Custom Hourly Pickups
*Endpoint: `GET /api/v1/custom/hourly-pickups`*

It uses a custom algorithm to count pickups per hour.

**Example:**
```bash
curl "http://localhost:8000/api/v1/custom/hourly-pickups"
```
**Sample response**
```json
{
  "hourly_pickups": {
    "0": 1,
    "1": 0,
    "2": 1,
    "3": 0,
    "4": 1,
    "5": 0,
    "6": 2,
    "7": 2,
    "8": 2,
    "9": 3,
    "10": 1,
    "11": 3,
    "12": 1,
    "13": 5,
    "14": 7,
    "15": 4,
    "16": 3,
    "17": 5,
    "18": 4,
    "19": 6,
    "20": 5,
    "21": 4,
    "22": 3,
    "23": 3
  },
  "total_trips": 66,
  "filters": {
    "day_of_week": 0
  }
}
```

#### Cluster Ranking
*Endpoint: `GET /api/v1/custom/cluster-ranking`*

This endpoint ranks clusters by total trip duration using custom algorithms.

**Parameters:**
- `n_clusters`: Number of clusters (2-20)
- `cluster_type`: "pickup" or "dropoff"

**Example:**
```bash
curl "http://localhost:8000/api/v1/custom/cluster-ranking?n_clusters=8&cluster_type=pickup"
```

#### Trip Sorting
*Endpoint: `GET /api/v1/custom/trip-sorting`*

It sorts trips using custom sorting algorithms.

**Parameters:**
- `sort_by`: "duration", "distance", or "speed"
- `order`: "asc" or "desc" 
- `limit`: How many results to return

**Example:**
```bash
# Longest trips first
curl "http://localhost:8000/api/v1/custom/trip-sorting?sort_by=duration&order=desc&limit=50"

# Shortest distances first  
curl "http://localhost:8000/api/v1/custom/trip-sorting?sort_by=distance&order=asc&limit=30"
```
</details>

## Code Examples

### Python Usage
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

def get_summary():
    response = requests.get(f"{BASE_URL}/summary/overview")
    return response.json()

def get_busiest_hours():
    response = requests.get(f"{BASE_URL}/temporal/hourly-distribution")
    data = response.json()
    
    # Find peak hours (more than 1000 trips)
    peak_hours = [
        hour for hour in data['hourly_distribution'] 
        if hour['trip_count'] > 1000
    ]
    return peak_hours

def get_top_routes(limit=10):
    response = requests.get(
        f"{BASE_URL}/flows/top-pairs", 
        params={"limit": limit}
    )
    return response.json()

# Usage examples
print("Summary:", get_summary())
print("Peak hours:", get_busiest_hours()) 
print("Top routes:", get_top_routes(5))
```

### JavaScript Usage
```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

async function fetchUrbanData() {
    try {
        // Get summary statistics
        const summaryResponse = await fetch(`${BASE_URL}/summary/overview`);
        const summary = await summaryResponse.json();
        
        // Get hourly patterns
        const hourlyResponse = await fetch(`${BASE_URL}/temporal/hourly-distribution`);
        const hourlyData = await hourlyResponse.json();
        
        // Get top clusters
        const clustersResponse = await fetch(`${BASE_URL}/clusters/pickup?n_clusters=5`);
        const clusters = await clustersResponse.json();
        
        return { summary, hourlyData, clusters };
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Usage
fetchUrbanData().then(data => {
    console.log('Urban Mobility Data:', data);
});
```

## Filter Combinations

### Real-World Scenarios

- **Morning Commute Analysis:**
```bash
# Monday-Friday, 7-10 AM
curl "http://localhost:8000/api/v1/summary/overview?hour_start=7&hour_end=10"
curl "http://localhost:8000/api/v1/flows/top-pairs?hour_start=7&hour_end=10&limit=10"
```

- **Weekend Night Life:**
```bash
# Friday-Saturday, 10 PM - 2 AM  
curl "http://localhost:8000/api/v1/summary/overview?hour_start=22&hour_end=2"
curl "http://localhost:8000/api/v1/clusters/pickup?n_clusters=8"
```

- **Business District Focus:**
```bash
# Weekdays 8 AM-6 PM
curl "http://localhost:8000/api/v1/summary/overview?hour_start=8&hour_end=18&day_of_week=0"
```

## Interactive Documentation

Visit **`http://localhost:8000/docs`** for:
- Live API testing
- Automatic parameter validation  
- Request/response examples
- Schema documentation

**Tips**
> 1. Start Simple: Begin with `/summary/overview` to understand your data
> 2. Use Filters: Combine time and day filters for targeted insights
> 3. Visualize: Use the cluster and flow data for maps
> 4. Compare: Use different time ranges to spot patterns
> 5. Experiment: Try the custom algorithms for unique insights

## Error Handling

The API returns standard HTTP status codes:
- `200` Success
- `400` Bad request (invalid parameters)
- `404` Endpoint not found
- `500` Server error

```json
// Error response example
{
  "detail": "Invalid hour range: hour_start must be between 0 and 23"
}
```

---

**Thanks.**

Now it's your turn to hack, start the server, explore the docs (via `http://localhost:8000/docs`), and connect it to your dashboard.
