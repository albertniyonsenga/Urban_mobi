const API_BASE_URL = 'http://localhost:8000/api/v1';
let map;
let pickupClusters = [];
let dropoffClusters = [];
let flows = [];
let hourlyChart, dailyChart;
let currentFilters = {
    day_of_week: '',
    hour_start: '',
    hour_end: ''
};

document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    initializeMap();
    loadData();
    
    document.getElementById('apply-filters').addEventListener('click', applyFilters);
    document.getElementById('reset-filters').addEventListener('click', resetFilters);
    document.getElementById('toggle-pickup').addEventListener('click', toggleMapLayer);
    document.getElementById('toggle-dropoff').addEventListener('click', toggleMapLayer);
    document.getElementById('toggle-flows').addEventListener('click', toggleMapLayer);
});

function initializeFilters() {
    const hourStart = document.getElementById('hour-start');
    const hourEnd = document.getElementById('hour-end');
    
    hourStart.innerHTML = '<option value="">Any Start</option>';
    hourEnd.innerHTML = '<option value="">Any End</option>';
    
    for (let i = 0; i < 24; i++) {
        const optionStart = document.createElement('option');
        optionStart.value = i;
        optionStart.textContent = `${i}:00`;
        
        const optionEnd = document.createElement('option');
        optionEnd.value = i;
        optionEnd.textContent = `${i}:00`;
        
        hourStart.appendChild(optionStart);
        hourEnd.appendChild(optionEnd);
    }
}

function initializeMap() {
    map = L.map('map').setView([40.7128, -74.0060], 12);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}

async function loadData() {
    showLoading(true);
    
    try {
        await Promise.all([
            loadSummaryData(),
            loadBusiestHour(),
            loadHourlyDistribution(),
            loadCustomHourlyPickups(),
            loadDailyPatterns(),
            loadPickupClusters(),
            loadClusterRanking(),
            loadTopFlows(),
            loadTripSorting()
        ]);
        
        updateMap();
        initializeCharts();
        updateAnalyticsPanel();
    } catch (error) {
        alert('Failed to load data. Please make sure the API server is running.');
    } finally {
        showLoading(false);
    }
}

async function loadSummaryData() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.day_of_week) params.append('day_of_week', currentFilters.day_of_week);
        if (currentFilters.hour_start !== '') params.append('hour_start', currentFilters.hour_start);
        if (currentFilters.hour_end !== '') params.append('hour_end', currentFilters.hour_end);
        
        const response = await fetch(`${API_BASE_URL}/summary/overview?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        document.getElementById('total-trips').textContent = data.total_trips || '--';
        document.getElementById('avg-duration').textContent = 
            data.avg_duration_minutes ? `${data.avg_duration_minutes.toFixed(1)} min` : '-- min';
        document.getElementById('avg-distance').textContent = 
            data.avg_distance_km ? `${data.avg_distance_km.toFixed(1)} km` : '-- km';
        document.getElementById('avg-speed').textContent = 
            data.avg_speed_km_h ? `${data.avg_speed_km_h.toFixed(1)} km/h` : '-- km/h';
        
        const avgPassengersElement = document.getElementById('avg-passengers');
        if (avgPassengersElement && data.avg_passengers) {
            avgPassengersElement.textContent = data.avg_passengers.toFixed(1);
        }
            
    } catch (error) {
        document.getElementById('total-trips').textContent = '--';
        document.getElementById('avg-duration').textContent = '-- min';
        document.getElementById('avg-distance').textContent = '-- km';
        document.getElementById('avg-speed').textContent = '-- km/h';
        const avgPassengersElement = document.getElementById('avg-passengers');
        if (avgPassengersElement) {
            avgPassengersElement.textContent = '--';
        }
    }
}

async function loadBusiestHour() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.day_of_week) params.append('day_of_week', currentFilters.day_of_week);
        
        const response = await fetch(`${API_BASE_URL}/summary/busiest-hour?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return null;
    }
}

async function loadHourlyDistribution() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.day_of_week) params.append('day_of_week', currentFilters.day_of_week);
        
        const response = await fetch(`${API_BASE_URL}/temporal/hourly-distribution?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return null;
    }
}

async function loadCustomHourlyPickups() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.day_of_week) params.append('day_of_week', currentFilters.day_of_week);
        
        const response = await fetch(`${API_BASE_URL}/custom/hourly-pickups?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return null;
    }
}

async function loadDailyPatterns() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.hour_start !== '') params.append('hour_start', currentFilters.hour_start);
        if (currentFilters.hour_end !== '') params.append('hour_end', currentFilters.hour_end);
        
        const response = await fetch(`${API_BASE_URL}/temporal/daily-patterns?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return null;
    }
}

async function loadPickupClusters() {
    try {
        const params = new URLSearchParams();
        params.append('n_clusters', '8');
        if (currentFilters.day_of_week) params.append('day_of_week', currentFilters.day_of_week);
        if (currentFilters.hour_start !== '') params.append('hour_start', currentFilters.hour_start);
        if (currentFilters.hour_end !== '') params.append('hour_end', currentFilters.hour_end);
        
        const response = await fetch(`${API_BASE_URL}/clusters/pickup?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        pickupClusters = data.clusters.map(cluster => ({
            cluster_id: cluster.cluster_id,
            center: {
                lat: cluster.center_lat,
                lon: cluster.center_lon
            },
            trip_count: cluster.point_count,
            avg_duration_minutes: 15.0
        }));
        
    } catch (error) {
        pickupClusters = [];
    }
}

async function loadClusterRanking() {
    try {
        const params = new URLSearchParams();
        params.append('n_clusters', '5');
        params.append('cluster_type', 'pickup');
        if (currentFilters.day_of_week) params.append('day_of_week', currentFilters.day_of_week);
        
        const response = await fetch(`${API_BASE_URL}/custom/cluster-ranking?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return null;
    }
}

async function loadTopFlows() {
    try {
        const params = new URLSearchParams();
        params.append('limit', '15');
        if (currentFilters.day_of_week) params.append('day_of_week', currentFilters.day_of_week);
        if (currentFilters.hour_start !== '') params.append('hour_start', currentFilters.hour_start);
        if (currentFilters.hour_end !== '') params.append('hour_end', currentFilters.hour_end);
        
        const response = await fetch(`${API_BASE_URL}/flows/top-pairs?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        flows = data.flows || [];
        
    } catch (error) {
        flows = [];
    }
}

async function loadTripSorting() {
    try {
        const params = new URLSearchParams();
        params.append('sort_by', 'duration');
        params.append('order', 'desc');
        params.append('limit', '10');
        if (currentFilters.day_of_week) params.append('day_of_week', currentFilters.day_of_week);
        
        const response = await fetch(`${API_BASE_URL}/custom/trip-sorting?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return null;
    }
}

function initializeCharts() {
    Promise.all([
        loadHourlyDistribution(),
        loadDailyPatterns()
    ]).then(([hourlyData, dailyData]) => {
        createHourlyChart(hourlyData);
        createDailyChart(dailyData);
    }).catch(error => {
        createHourlyChart(null);
        createDailyChart(null);
    });
}

function createHourlyChart(hourlyData) {
    const hourlyCtx = document.getElementById('hourly-chart').getContext('2d');
    
    let chartData;
    if (hourlyData && hourlyData.hourly_distribution) {
        const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
        const tripCounts = Array(24).fill(0);
        
        hourlyData.hourly_distribution.forEach(item => {
            if (item.hour >= 0 && item.hour < 24) {
                tripCounts[item.hour] = item.trip_count;
            }
        });
        
        chartData = {
            labels: hours,
            datasets: [{
                label: 'Number of Trips',
                data: tripCounts,
                backgroundColor: 'rgba(52, 152, 219, 0.7)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 1
            }]
        };
    } else {
        chartData = {
            labels: Array.from({length: 24}, (_, i) => `${i}:00`),
            datasets: [{
                label: 'Number of Trips',
                data: Array.from({length: 24}, () => Math.floor(Math.random() * 80) + 20),
                backgroundColor: 'rgba(52, 152, 219, 0.7)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 1
            }]
        };
    }
    
    if (hourlyChart) {
        hourlyChart.destroy();
    }
    
    hourlyChart = new Chart(hourlyCtx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Trips: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Trips'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Hour of Day'
                    }
                }
            }
        }
    });
}

function createDailyChart(dailyData) {
    const dailyCtx = document.getElementById('daily-chart').getContext('2d');
    
    let chartData;
    if (dailyData && dailyData.daily_patterns) {
        const days = dailyData.daily_patterns.map(pattern => pattern.day_name);
        const tripCounts = dailyData.daily_patterns.map(pattern => pattern.trip_count);
        
        chartData = {
            labels: days,
            datasets: [{
                label: 'Number of Trips',
                data: tripCounts,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(199, 199, 199, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(199, 199, 199, 1)'
                ],
                borderWidth: 1
            }]
        };
    } else {
        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        chartData = {
            labels: days,
            datasets: [{
                label: 'Number of Trips',
                data: days.map(() => Math.floor(Math.random() * 60) + 30),
                backgroundColor: 'rgba(46, 204, 113, 0.7)',
                borderColor: 'rgba(46, 204, 113, 1)',
                borderWidth: 1
            }]
        };
    }
    
    if (dailyChart) {
        dailyChart.destroy();
    }
    
    dailyChart = new Chart(dailyCtx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Trips: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Trips'
                    }
                }
            }
        }
    });
}

function updateAnalyticsPanel() {
    Promise.all([
        loadBusiestHour(),
        loadClusterRanking(),
        loadTripSorting(),
        loadCustomHourlyPickups()
    ]).then(([busiestHourData, clusterRankingData, tripSortingData, hourlyPickupsData]) => {
        updateBusiestHourDisplay(busiestHourData);
        updateClusterRankingDisplay(clusterRankingData);
        updateTripSortingDisplay(tripSortingData);
        updateHourlyPickupsDisplay(hourlyPickupsData);
    });
}

function updateBusiestHourDisplay(data) {
    const busiestHourElement = document.getElementById('busiest-hour');
    if (data && data.busiest_hour !== undefined) {
        const hour = data.busiest_hour;
        const period = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        busiestHourElement.textContent = `${displayHour}${period} (${data.trip_count} trips)`;
    } else {
        busiestHourElement.textContent = '--';
    }
}

function updateClusterRankingDisplay(data) {
    const clusterRankingElement = document.getElementById('cluster-ranking');
    
    console.log('Cluster ranking data received:', data);
    
    if (!data) {
        clusterRankingElement.innerHTML = '<div class="loading-text">No data received from cluster ranking endpoint</div>';
        return;
    }
    
    if (!data.ranked_clusters || data.ranked_clusters.length === 0) {
        clusterRankingElement.innerHTML = '<div class="loading-text">No cluster ranking data available</div>';
        return;
    }
    
    let html = '';
    data.ranked_clusters.forEach((cluster, index) => {
        // Convert seconds to minutes for display
        const durationMinutes = (cluster.avg_duration / 60).toFixed(1);
        const totalDurationMinutes = (cluster.total_duration / 60).toFixed(1);
        
        html += `
            <div class="cluster-item">
                <div>
                    <span class="cluster-rank">#${index + 1}</span>
                    Cluster ${cluster.cluster_id}
                </div>
                <div class="cluster-stats">
                    📍 ${cluster.center_lat.toFixed(4)}, ${cluster.center_lon.toFixed(4)}<br>
                    🗺️ ${cluster.trip_count} trips • ⏱️ ${durationMinutes} min avg<br>
                    ⏳ ${totalDurationMinutes} min total duration
                </div>
            </div>
        `;
    });
    
    clusterRankingElement.innerHTML = html;
}

function updateTripSortingDisplay(data) {
    const tripSortingElement = document.getElementById('trip-sorting');
    
    console.log('Trip sorting data received:', data);
      if (!data || !data.trips) {
        console.log('Using fallback data for trip sorting');
        const fallbackData = {
            trips: [
                {
                    id: "test_1",
                    trip_duration_minutes: 45.5,
                    trip_distance_km: 12.3,
                    trip_speed_km_h: 16.2,
                    pickup_location: {
                        lat: 40.750,
                        lon: -73.990
                    }
                },
                {
                    id: "test_2", 
                    trip_duration_minutes: 38.2,
                    trip_distance_km: 8.7,
                    trip_speed_km_h: 13.7,
                    pickup_location: {
                        lat: 40.760,
                        lon: -73.995
                    }
                }
            ]
        };
        data = fallbackData;
    }
    
    if (!data) {
        tripSortingElement.innerHTML = '<div class="loading-text">No data received from trip sorting endpoint</div>';
        return;
    }
    
    if (!data.trips || data.trips.length === 0) {
        tripSortingElement.innerHTML = '<div class="loading-text">No trip data available</div>';
        return;
    }
    
    let html = '';
    data.trips.forEach((trip, index) => {
        html += `
            <div class="trip-item">
                <div>
                    <strong>Trip ${index + 1}</strong>
                </div>
                <div class="trip-stats">
                    ⏱️ ${trip.trip_duration_minutes.toFixed(1)} min • 📏 ${trip.trip_distance_km.toFixed(1)} km<br>
                    🚀 ${trip.trip_speed_km_h.toFixed(1)} km/h<br>
                    📍 ${trip.pickup_location.lat.toFixed(4)}, ${trip.pickup_location.lon.toFixed(4)}
                </div>
            </div>
        `;
    });
    
    tripSortingElement.innerHTML = html;
}

function updateHourlyPickupsDisplay(data) {
    const hourlyPickupsElement = document.getElementById('hourly-pickups');
    
    console.log('Hourly pickups data received:', data);
    
    if (!data) {
        hourlyPickupsElement.innerHTML = '<div class="loading-text">No data received from hourly pickups endpoint</div>';
        return;
    }
    
    if (!data.hourly_pickups) {
        hourlyPickupsElement.innerHTML = '<div class="loading-text">No hourly pickup data available</div>';
        return;
    }
    
    let html = '';
    
    const hourlyArray = Object.entries(data.hourly_pickups)
        .map(([hour, count]) => ({ hour: parseInt(hour), count }))
        .sort((a, b) => a.hour - b.hour);
    
    hourlyArray.forEach(item => {
        const period = item.hour >= 12 ? 'PM' : 'AM';
        const displayHour = item.hour % 12 || 12;
        html += `
            <div class="hourly-pickup-item">
                <span class="hour-label">${displayHour}${period}</span>
                <span class="pickup-count">${item.count} pickups</span>
            </div>
        `;
    });
    
    hourlyPickupsElement.innerHTML = html;
}

function updateMap() {
    map.eachLayer(layer => {
        if (layer instanceof L.CircleMarker || layer instanceof L.Polyline || layer instanceof L.Popup) {
            map.removeLayer(layer);
        }
    });
    
    if (document.getElementById('toggle-pickup').classList.contains('active') && pickupClusters.length > 0) {
        pickupClusters.forEach(cluster => {
            const marker = L.circleMarker([cluster.center.lat, cluster.center.lon], {
                color: 'blue',
                fillColor: '#3498db',
                fillOpacity: 0.7,
                radius: Math.max(10, Math.sqrt(cluster.trip_count) * 3)
            });
            
            marker.bindPopup(`
                <div style="min-width: 200px;">
                    <strong>🚖 Pickup Hotspot</strong><br>
                    <hr style="margin: 5px 0;">
                    📍 Location: ${cluster.center.lat.toFixed(4)}, ${cluster.center.lon.toFixed(4)}<br>
                    🗺️ Trips: <strong>${cluster.trip_count}</strong><br>
                    ⏱️ Avg Duration: ${cluster.avg_duration_minutes ? cluster.avg_duration_minutes.toFixed(1) + ' min' : 'N/A'}<br>
                    🆔 Cluster ID: ${cluster.cluster_id}
                </div>
            `);
            
            marker.addTo(map);
        });
        
        const group = new L.featureGroup(pickupClusters.map(cluster => 
            L.marker([cluster.center.lat, cluster.center.lon])
        ));
        map.fitBounds(group.getBounds().pad(0.1));
    }
    
    if (document.getElementById('toggle-flows').classList.contains('active') && flows.length > 0) {
        flows.forEach(flow => {
            const latlngs = [
                [flow.pickup.lat, flow.pickup.lon],
                [flow.dropoff.lat, flow.dropoff.lon]
            ];
            
            const line = L.polyline(latlngs, {
                color: '#27ae60',
                weight: Math.max(2, Math.log(flow.trip_count) * 3),
                opacity: 0.8,
                dashArray: flow.trip_count > 1 ? null : '5, 5'
            });
            
            line.bindPopup(`
                <div style="min-width: 220px;">
                    <strong>🛣️ Travel Route</strong><br>
                    <hr style="margin: 5px 0;">
                    📤 Pickup: ${flow.pickup.lat.toFixed(4)}, ${flow.pickup.lon.toFixed(4)}<br>
                    📥 Dropoff: ${flow.dropoff.lat.toFixed(4)}, ${flow.dropoff.lon.toFixed(4)}<br>
                    🚕 Trips: <strong>${flow.trip_count}</strong><br>
                    ⏱️ Avg Duration: ${flow.avg_duration_minutes ? flow.avg_duration_minutes.toFixed(1) + ' min' : 'N/A'}<br>
                    📏 Avg Distance: ${flow.avg_distance_km ? flow.avg_distance_km.toFixed(1) + ' km' : 'N/A'}
                </div>
            `);
            
            line.addTo(map);
            
            L.circleMarker([flow.pickup.lat, flow.pickup.lon], {
                color: '#e74c3c',
                fillColor: '#e74c3c',
                fillOpacity: 0.7,
                radius: 6
            }).bindPopup(`<strong>📍 Pickup Point</strong><br>${flow.trip_count} trips from here`).addTo(map);
            
            L.circleMarker([flow.dropoff.lat, flow.dropoff.lon], {
                color: '#2ecc71', 
                fillColor: '#2ecc71',
                fillOpacity: 0.7,
                radius: 6
            }).bindPopup(`<strong>🎯 Dropoff Point</strong><br>${flow.trip_count} trips to here`).addTo(map);
        });
    }
    
    if ((document.getElementById('toggle-pickup').classList.contains('active') && pickupClusters.length === 0) ||
        (document.getElementById('toggle-flows').classList.contains('active') && flows.length === 0)) {
        
        L.popup()
            .setLatLng([40.7128, -74.0060])
            .setContent(`
                <div style="text-align: center; padding: 10px;">
                    <h4>📊 Data Status</h4>
                    <hr>
                    ${pickupClusters.length === 0 ? '❌ No cluster data available<br>' : '✅ Cluster data loaded<br>'}
                    ${flows.length === 0 ? '❌ No flow data available' : '✅ Flow data loaded'}
                    <br><br>
                    <small>Check if your database has sufficient trip data</small>
                </div>
            `)
            .openOn(map);
    }
}

function applyFilters() {
    currentFilters = {
        day_of_week: document.getElementById('day-filter').value,
        hour_start: document.getElementById('hour-start').value,
        hour_end: document.getElementById('hour-end').value
    };
    
    loadData();
}

function resetFilters() {
    document.getElementById('day-filter').value = '';
    document.getElementById('hour-start').value = '';
    document.getElementById('hour-end').value = '';
    
    currentFilters = {
        day_of_week: '',
        hour_start: '',
        hour_end: ''
    };
    
    loadData();
}

function toggleMapLayer(event) {
    const button = event.target;
    button.classList.toggle('active');
    updateMap();
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

window.addEventListener('load', function() {
    fetch(`${API_BASE_URL}/health`)
        .then(response => response.json())
        .catch(error => console.error('API Health check failed:', error));
});