
## 3. Frontend Documentation

**frontend/USER_GUIDE.md**
```markdown
# Urban Mobility Dashboard - User Guide

## Overview

The Urban Mobility Dashboard provides an interactive interface to explore and visualize urban transportation patterns. It connects to the backend API to display real-time insights about taxi mobility patterns.

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Backend server running on http://localhost:8000
- Internet connection (for map tiles and libraries)

### Quick Start
1. Ensure the backend server is running
2. Open `index.html` in your web browser
3. The dashboard will automatically load and display data

## Dashboard Layout

### 1. Header Section
- Application title and description
- Quick overview of the system's purpose

### 2. Filter Controls
- **Day of Week**: Filter by specific days (Monday-Sunday)
- **Time Range**: Select start and end hours for analysis
- **Apply/Rest**: Buttons to apply or clear filters

### 3. Summary Cards
- **Total Trips**: Overall trip count
- **Avg Duration**: Average trip duration in minutes
- **Avg Distance**: Average trip distance in kilometers
- **Avg Speed**: Average speed in km/h

### 4. Charts Section
- **Hourly Distribution**: Bar chart showing trips by hour
- **Daily Patterns**: Bar chart showing trips by day of week

### 5. Interactive Map
- **Pickup Clusters**: Blue circles showing popular pickup locations
- **Dropoff Clusters**: Red circles showing popular dropoff locations
- **Flow Lines**: Green lines showing common routes between locations

## How to Use

### Basic Exploration

1. **View Overall Patterns**
   - Open the dashboard without filters
   - Observe the general distribution of trips
   - Identify peak hours and busy locations

2. **Analyze Specific Time Periods**
   - Use time filters to focus on rush hours (7-10 AM, 4-7 PM)
   - Compare weekday vs weekend patterns
   - Study nightlife patterns (10 PM - 2 AM)

3. **Explore Spatial Patterns**
   - Toggle map layers to show/hide different data types
   - Click on clusters to see detailed information
   - Follow flow lines to understand common routes

### Advanced Analysis

#### Morning Commute Analysis
1. Set Day of Week: Monday-Friday (0-4)
2. Set Time Range: 7 AM to 10 AM
3. Apply filters and observe:
   - Which areas have the most pickups?
   - What are the common routes to business districts?
   - How long are typical morning commutes?

#### Weekend Patterns
1. Set Day of Week: Saturday-Sunday (5-6)
2. Set Time Range: 8 PM to 2 AM
3. Analyze:
   - Entertainment district activity
   - Late-night transportation demand
   - Popular destination clusters

#### Business District Focus
1. Set Time Range: 8 AM to 6 PM
2. Observe:
   - Peak business hours
   - Lunchtime patterns (12-1 PM)
   - Evening commute patterns

### Map Controls

#### Layer Toggles
- **Pickup Clusters**: Show/hide blue pickup location markers
- **Dropoff Clusters**: Show/hide red dropoff location markers
- **Show Flows**: Show/hide green route lines between locations

#### Interactive Features
- **Click Clusters**: View trip count and average duration
- **Click Flow Lines**: See route statistics and popularity
- **Zoom/Pan**: Navigate the map for detailed exploration
- **Map Controls**: Standard Leaflet zoom and layer controls

## Interpreting Visualizations

### Cluster Sizes
- Larger circles indicate more trips in that area
- Circle size is proportional to the square root of trip count
- Color intensity shows cluster activity level

### Flow Lines
- Thicker lines indicate more popular routes
- Line opacity shows relative traffic volume
- Straight lines represent direct routes (curved for visualization)

### Chart Patterns
- **Hourly Chart**: Look for morning/evening peaks
- **Daily Chart**: Compare weekday vs weekend volumes
- **Color Coding**: Consistent color scheme across visualizations

## Common Use Cases

### Urban Planners
- Identify transportation infrastructure needs
- Plan public transit routes
- Locate areas needing taxi stands

### Taxi Companies
- Optimize fleet allocation
- Identify high-demand areas and times
- Plan driver shifts and coverage

### Researchers
- Study human mobility patterns
- Analyze spatial-temporal dynamics
- Compare different time periods

### City Officials
- Monitor transportation system performance
- Identify congestion areas
- Plan for special events

## Tips for Effective Analysis

1. **Start Broad**: Begin with no filters to understand overall patterns
2. **Use Comparative Analysis**: Compare different days or time periods
3. **Combine Filters**: Use both day and time filters for precise insights
4. **Leverage Multiple Views**: Correlate map data with chart patterns
5. **Save Interesting Views**: Note filter combinations that reveal insights

## Troubleshooting

### Data Not Loading
- Check if backend server is running
- Verify API health at http://localhost:8000/health
- Check browser console for errors

### Map Not Displaying
- Ensure internet connection is active
- Check if map tiles are loading
- Verify Leaflet library is loaded

### Filters Not Working
- Ensure valid time ranges (0-23 for hours)
- Check console for validation errors
- Try resetting and reapplying filters

### Performance Issues
- Use appropriate time ranges
- Limit the number of clusters
- Close other browser tabs if needed

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Mobile Usage

The dashboard is fully responsive and works on:
- Tablets and iPads
- Smartphones (landscape recommended for best experience)
- Touch-enabled devices with gesture support

## Data Refresh

- Data updates when filters are applied
- Manual refresh by reapplying filters
- Real-time data depends on backend updates

## Support

For technical issues:
1. Check browser console for errors
2. Verify backend API status
3. Review this documentation
4. Check system requirements

---

*Last updated: January 2024*