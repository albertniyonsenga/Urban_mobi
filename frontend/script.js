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
            loadHourlyDistribution(),
            loadDailyPatterns(),
            loadPickupClusters(),
            loadTopFlows()
        ]);
        
        updateMap();
        initializeCharts();
    } catch (error) {
        console.error('Error loading data:', error);
        alert('Failed to load data. Please make sure the API server is running.');
    } finally {
        showLoading(false);
    }
}
async function loadSummaryData() {
    const params = new URLSearchParams();
    if (currentFilters.day_of_week) params.append('day_of_week', currentFilters.day_of_week);
    if (currentFilters.hour_start) params.append('hour_start', currentFilters.hour_start);
    if (currentFilters.hour_end) params.append('hour_end', currentFilters.hour_end);
    
    const response = await fetch(`${API_BASE_URL}/summary/overview?${params}`);
    const data = await response.json();
    document.getElementById('total-trips').textContent = data.total_trips || '--';
    document.getElementById('avg-duration').textContent = 
        data.avg_duration_minutes ? `${data.avg_duration_minutes.toFixed(1)} min` : '-- min';
    document.getElementById('avg-distance').textContent = 
        data.avg_distance_km ? `${data.avg_distance_km.toFixed(1)} km` : '-- km';
    document.getElementById('avg-speed').textContent = 
        data.avg_speed_km_h ? `${data.avg_speed_km_h.toFixed(1)} km/h` : '-- km/h';
}
async function loadHourlyDistribution() {
    const response = await fetch(`${API_BASE_URL}/temporal/hourly-distribution`);
    return await response.json();
}
async function loadDailyPatterns() {
    const response = await fetch(`${API_BASE_URL}/temporal/daily-patterns`);
    return await response.json();
}
async function loadPickupClusters() {
    const response = await fetch(`${API_BASE_URL}/clusters/pickup?n_clusters=8`);
    const data = await response.json();
    pickupClusters = data.clusters || [];
}
async function loadTopFlows() {
    const params = new URLSearchParams();
    params.append('limit', '15');
    if (currentFilters.hour_start) params.append('hour_start', currentFilters.hour_start);
    if (currentFilters.hour_end) params.append('hour_end', currentFilters.hour_end);
    
    const response = await fetch(`${API_BASE_URL}/flows/top-pairs?${params}`);
    const data = await response.json();
    flows = data.flows || [];
}
function initializeCharts() {
    const hourlyCtx = document.getElementById('hourly-chart').getContext('2d');
    const hourlyData = {
        labels: Array.from({length: 24}, (_, i) => `${i}:00`),
        datasets: [{
            label: 'Number of Trips',
            data: Array.from({length: 24}, () => Math.floor(Math.random() * 100)),
            backgroundColor: 'rgba(52, 152, 219, 0.7)',
            borderColor: 'rgba(52, 152, 219, 1)',
            borderWidth: 1
        }]
    };
    
    hourlyChart = new Chart(hourlyCtx, {
        type: 'bar',
        data: hourlyData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
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
    const dailyCtx = document.getElementById('daily-chart').getContext('2d');
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const dailyData = {
        labels: days,
        datasets: [{
            label: 'Average Trips',
            data: days.map(() => Math.floor(Math.random() * 100)),
            backgroundColor: 'rgba(46, 204, 113, 0.7)',
            borderColor: 'rgba(46, 204, 113, 1)',
            borderWidth: 1
        }]
    };
    
    dailyChart = new Chart(dailyCtx, {
        type: 'bar',
        data: dailyData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
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
function updateMap() {
    map.eachLayer(layer => {
        if (layer instanceof L.Marker || layer instanceof L.Polyline) {
            map.removeLayer(layer);
        }
    });
    if (document.getElementById('toggle-pickup').classList.contains('active')) {
        pickupClusters.forEach(cluster => {
            L.circleMarker([cluster.center.lat, cluster.center.lon], {
                color: 'blue',
                fillColor: '#3498db',
                fillOpacity: 0.7,
                radius: Math.sqrt(cluster.trip_count) * 2
            })
            .bindPopup(`
                <strong>Pickup Cluster</strong><br>
                Trips: ${cluster.trip_count}<br>
                Avg Duration: ${cluster.avg_duration_minutes ? cluster.avg_duration_minutes.toFixed(1) : 'N/A'} min
            `)
            .addTo(map);
        });
    }
    if (document.getElementById('toggle-dropoff').classList.contains('active')) {
        pickupClusters.forEach(cluster => {
            L.circleMarker([cluster.center.lat + 0.01, cluster.center.lon + 0.01], {
                color: 'red',
                fillColor: '#e74c3c',
                fillOpacity: 0.7,
                radius: Math.sqrt(cluster.trip_count) * 2
            })
            .bindPopup(`
                <strong>Dropoff Cluster</strong><br>
                Trips: ${cluster.trip_count}<br>
                Avg Duration: ${cluster.avg_duration_minutes ? cluster.avg_duration_minutes.toFixed(1) : 'N/A'} min
            `)
            .addTo(map);
        });
    }
    if (document.getElementById('toggle-flows').classList.contains('active') && flows.length > 0) {
        flows.forEach(flow => {
            const latlngs = [
                [flow.pickup.lat, flow.pickup.lon],
                [flow.dropoff.lat, flow.dropoff.lon]
            ];
            
            L.polyline(latlngs, {
                color: 'green',
                weight: Math.log(flow.trip_count) * 2,
                opacity: 0.7
            })
            .bindPopup(`
                <strong>Route</strong><br>
                Trips: ${flow.trip_count}<br>
                Avg Duration: ${flow.avg_duration_minutes ? flow.avg_duration_minutes.toFixed(1) : 'N/A'} min<br>
                Avg Distance: ${flow.avg_distance_km ? flow.avg_distance_km.toFixed(1) : 'N/A'} km
            `)
            .addTo(map);
        });
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