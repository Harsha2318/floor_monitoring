// Employee Monitoring System - Frontend Application
const socket = io();

// State management
let systemRunning = false;
let cameras = [];
let activePresences = [];
let alerts = [];

// DOM elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const systemStatus = document.getElementById('systemStatus');
const cameraGrid = document.getElementById('cameraGrid');
const presenceTableBody = document.getElementById('presenceTableBody');
const alertsList = document.getElementById('alertsList');
const historyTableBody = document.getElementById('historyTableBody');
const addCameraForm = document.getElementById('addCameraForm');

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    setupSocketHandlers();
});

function initializeApp() {
    loadCameras();
    loadSystemStatus();
    loadStatistics();
    loadActivePresences();
    loadAlerts();
    loadHistory();
    
    // Set default dates for history filter
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('endDate').value = today;
    document.getElementById('startDate').value = today;
    
    // Start auto-refresh
    setInterval(() => {
        if (systemRunning) {
            loadStatistics();
            loadActivePresences();
            loadAlerts();
        }
    }, 5000); // Refresh every 5 seconds
}

function setupEventListeners() {
    startBtn.addEventListener('click', startSystem);
    stopBtn.addEventListener('click', stopSystem);
    addCameraForm.addEventListener('submit', addCamera);
    document.getElementById('filterHistory').addEventListener('click', loadHistory);
}

function setupSocketHandlers() {
    socket.on('connect', () => {
        console.log('Connected to server');
        showNotification('Connected to monitoring system', 'success');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        showNotification('Disconnected from server', 'warning');
    });
    
    socket.on('camera_update', (data) => {
        console.log('Camera update:', data);
        updateCameraStats(data);
    });
    
    socket.on('alert', (data) => {
        console.log('New alert:', data);
        handleNewAlert(data);
    });
}

// System control functions
async function startSystem() {
    try {
        const response = await fetch('/api/system/start', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            systemRunning = true;
            updateSystemStatus(true);
            showNotification('System started successfully', 'success');
        } else {
            showNotification(data.message || 'Failed to start system', 'error');
        }
    } catch (error) {
        console.error('Error starting system:', error);
        showNotification('Error starting system', 'error');
    }
}

async function stopSystem() {
    try {
        const response = await fetch('/api/system/stop', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            systemRunning = false;
            updateSystemStatus(false);
            showNotification('System stopped', 'info');
        }
    } catch (error) {
        console.error('Error stopping system:', error);
        showNotification('Error stopping system', 'error');
    }
}

function updateSystemStatus(running) {
    if (running) {
        systemStatus.textContent = 'System Online';
        systemStatus.className = 'badge bg-success me-3';
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        systemStatus.textContent = 'System Offline';
        systemStatus.className = 'badge bg-secondary me-3';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

async function loadSystemStatus() {
    try {
        const response = await fetch('/api/system/status');
        const data = await response.json();
        
        systemRunning = data.processing_active;
        updateSystemStatus(systemRunning);
        
        document.getElementById('detectionModel').value = data.detection_model;
        document.getElementById('absenceTimeout').value = data.alert_timeout;
    } catch (error) {
        console.error('Error loading system status:', error);
    }
}

// Camera management
async function loadCameras() {
    try {
        const response = await fetch('/api/cameras');
        cameras = await response.json();
        
        renderCameras();
    } catch (error) {
        console.error('Error loading cameras:', error);
    }
}

function renderCameras() {
    cameraGrid.innerHTML = '';
    
    if (cameras.length === 0) {
        cameraGrid.innerHTML = `
            <div class="col-12">
                <div class="empty-state">
                    <i class="fas fa-video-slash"></i>
                    <p>No cameras configured. Add cameras in the Configuration tab.</p>
                </div>
            </div>
        `;
        return;
    }
    
    cameras.forEach(camera => {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 camera-grid-item';
        
        col.innerHTML = `
            <div class="camera-feed">
                <img src="/video_feed/${camera.camera_id}" alt="${camera.name}">
                <div class="camera-info">
                    <p class="camera-name">${camera.name}</p>
                    <p class="camera-stats">
                        <span class="badge ${camera.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${camera.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <span class="ms-2">${camera.resolution[0]}x${camera.resolution[1]}</span>
                        <span class="ms-2" id="detections-${camera.camera_id}">0 detected</span>
                    </p>
                </div>
            </div>
        `;
        
        cameraGrid.appendChild(col);
    });
}

function updateCameraStats(data) {
    const detectionsElement = document.getElementById(`detections-${data.camera_id}`);
    if (detectionsElement) {
        detectionsElement.textContent = `${data.detections} detected`;
    }
}

async function addCamera(event) {
    event.preventDefault();
    
    const cameraData = {
        camera_id: document.getElementById('cameraId').value,
        name: document.getElementById('cameraName').value,
        type: document.getElementById('cameraType').value,
        source: document.getElementById('cameraSource').value
    };
    
    try {
        const response = await fetch('/api/cameras/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(cameraData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Camera added successfully', 'success');
            addCameraForm.reset();
            loadCameras();
        } else {
            showNotification('Failed to add camera', 'error');
        }
    } catch (error) {
        console.error('Error adding camera:', error);
        showNotification('Error adding camera', 'error');
    }
}

// Statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const stats = await response.json();
        
        document.getElementById('currentlyPresent').textContent = stats.currently_present || 0;
        document.getElementById('totalEntries').textContent = stats.total_entries || 0;
        document.getElementById('activeCameras').textContent = stats.cameras ? Object.keys(stats.cameras).length : 0;
        document.getElementById('unacknowledgedAlerts').textContent = stats.unacknowledged_alerts || 0;
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Presence management
async function loadActivePresences() {
    try {
        const response = await fetch('/api/presence/active');
        activePresences = await response.json();
        
        renderPresences();
    } catch (error) {
        console.error('Error loading presences:', error);
    }
}

function renderPresences() {
    presenceTableBody.innerHTML = '';
    
    if (activePresences.length === 0) {
        presenceTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">No employees currently present</td>
            </tr>
        `;
        return;
    }
    
    activePresences.forEach(presence => {
        const entryTime = new Date(presence.entry_time);
        const duration = calculateDuration(entryTime);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${presence.tracking_id}</td>
            <td>${presence.employee_name || presence.employee_id || 'Unknown'}</td>
            <td>${presence.camera_id}</td>
            <td>${formatDateTime(entryTime)}</td>
            <td><span class="badge bg-primary duration-badge">${duration}</span></td>
        `;
        
        presenceTableBody.appendChild(row);
    });
}

// Alert management
async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts/active');
        alerts = await response.json();
        
        renderAlerts();
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

function renderAlerts() {
    alertsList.innerHTML = '';
    
    if (alerts.length === 0) {
        alertsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-check-circle"></i>
                <p>No active alerts</p>
            </div>
        `;
        return;
    }
    
    alerts.forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `card alert-item ${alert.acknowledged ? 'acknowledged' : 'alert-pulse'}`;
        
        const leftTime = new Date(alert.left_at);
        const triggerTime = new Date(alert.alert_triggered_at);
        
        alertDiv.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="card-title">
                            <i class="fas fa-exclamation-triangle text-danger"></i>
                            ${alert.employee_name || alert.employee_id || 'Unknown Employee'}
                        </h5>
                        <p class="card-text">
                            <strong>Left at:</strong> ${formatDateTime(leftTime)}<br>
                            <strong>Alert triggered:</strong> ${formatDateTime(triggerTime)}<br>
                            <strong>Timeout:</strong> ${alert.timeout_minutes} minutes
                        </p>
                    </div>
                    <div>
                        ${alert.acknowledged ? 
                            '<span class="badge bg-secondary">Acknowledged</span>' :
                            `<button class="btn btn-sm btn-primary" onclick="acknowledgeAlert(${alert.id})">
                                <i class="fas fa-check"></i> Acknowledge
                            </button>`
                        }
                    </div>
                </div>
            </div>
        `;
        
        alertsList.appendChild(alertDiv);
    });
}

async function acknowledgeAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/${alertId}/acknowledge`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Alert acknowledged', 'success');
            loadAlerts();
            loadStatistics();
        }
    } catch (error) {
        console.error('Error acknowledging alert:', error);
        showNotification('Error acknowledging alert', 'error');
    }
}

function handleNewAlert(alertData) {
    // Play alert sound
    const audio = document.getElementById('alertSound');
    if (audio) {
        audio.play().catch(e => console.log('Could not play sound:', e));
    }
    
    // Show browser notification
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Employee Absence Alert', {
            body: `Employee ${alertData.employee_id} has been absent for ${alertData.timeout_minutes} minutes`,
            icon: '/static/images/alert-icon.png'
        });
    }
    
    // Reload alerts
    loadAlerts();
    loadStatistics();
}

// History
async function loadHistory() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    try {
        let url = '/api/presence/history';
        const params = new URLSearchParams();
        
        if (startDate) params.append('start_date', startDate + 'T00:00:00');
        if (endDate) params.append('end_date', endDate + 'T23:59:59');
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        const history = await response.json();
        
        renderHistory(history);
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function renderHistory(history) {
    historyTableBody.innerHTML = '';
    
    if (history.length === 0) {
        historyTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">No history records found</td>
            </tr>
        `;
        return;
    }
    
    history.forEach(record => {
        const entryTime = new Date(record.entry_time);
        const exitTime = record.exit_time ? new Date(record.exit_time) : null;
        const durationMin = record.duration_seconds ? Math.round(record.duration_seconds / 60) : '-';
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.employee_name || record.employee_id || 'Unknown'}</td>
            <td>${record.camera_id}</td>
            <td>${formatDateTime(entryTime)}</td>
            <td>${exitTime ? formatDateTime(exitTime) : '-'}</td>
            <td>${durationMin}</td>
            <td>
                <span class="badge ${record.status === 'present' ? 'bg-success' : 'bg-secondary'}">
                    ${record.status}
                </span>
            </td>
        `;
        
        historyTableBody.appendChild(row);
    });
}

// Utility functions
function formatDateTime(date) {
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function calculateDuration(startTime) {
    const now = new Date();
    const diff = now - startTime;
    
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

function showNotification(message, type = 'info') {
    // Simple notification - could be enhanced with a toast library
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // You could implement a toast notification here
    // For now, using browser alerts for important messages
    if (type === 'error') {
        alert(message);
    }
}

// Request notification permission on load
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
