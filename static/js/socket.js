const socket = io();

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('connected', (data) => {
    console.log('Socket connected:', data);
});

socket.on('session_started', (data) => {
    console.log('Session started:', data);
    updateSessionStatus(true);
});

socket.on('session_stopped', () => {
    console.log('Session stopped');
    updateSessionStatus(false);
});

socket.on('session_paused', (data) => {
    console.log('Session paused:', data);
    alert('Session paused due to inactivity');
    updateSessionStatus(false);
});

socket.on('alert', (data) => {
    console.log('Alert received:', data);
    addAlertToLog(data);
});

socket.on('wake_word_detected', () => {
    console.log('Wake word detected');
    showWakeWordStatus(true);
});

socket.on('voice_command', (data) => {
    console.log('Voice command received:', data);
    showWakeWordStatus(false);
});

socket.on('frame', (data) => {
    const img = document.getElementById('camera-feed');
    if (img) {
        img.src = data.data;
        img.classList.remove('hidden');
        document.getElementById('camera-placeholder')?.classList.add('hidden');
    }
});

function updateSessionStatus(isActive) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    
    if (indicator) {
        indicator.className = isActive ? 'w-4 h-4 rounded-full bg-green-500' : 'w-4 h-4 rounded-full bg-gray-400';
    }
    
    if (statusText) {
        statusText.textContent = isActive ? 'Active' : 'Stopped';
    }
    
    if (startBtn) {
        startBtn.classList.toggle('hidden', isActive);
    }
    
    if (stopBtn) {
        stopBtn.classList.toggle('hidden', !isActive);
    }
}

function addAlertToLog(alert) {
    const log = document.getElementById('alert-log');
    if (!log) return;
    
    const priorityColors = {
        'critical': 'bg-red-100 border-red-500',
        'important': 'bg-yellow-100 border-yellow-500',
        'informational': 'bg-blue-100 border-blue-500'
    };
    
    const color = priorityColors[alert.priority] || 'bg-gray-100 border-gray-500';
    
    const alertElement = document.createElement('div');
    alertElement.className = `p-3 rounded-lg border-l-4 ${color} mb-2`;
    alertElement.innerHTML = `
        <div class="flex justify-between items-start">
            <div>
                <p class="font-semibold">${alert.priority.toUpperCase()}</p>
                <p class="text-sm">${alert.message}</p>
            </div>
            <span class="text-xs text-gray-500">${new Date(alert.timestamp).toLocaleTimeString()}</span>
        </div>
    `;
    
    if (log.firstChild && log.firstChild.textContent === 'No alerts yet') {
        log.innerHTML = '';
    }
    
    log.insertBefore(alertElement, log.firstChild);
    
    while (log.children.length > 50) {
        log.removeChild(log.lastChild);
    }
}

function showWakeWordStatus(show) {
    const statusDiv = document.getElementById('wake-word-status');
    if (statusDiv) {
        if (show) {
            statusDiv.classList.remove('hidden');
        } else {
            setTimeout(() => {
                statusDiv.classList.add('hidden');
            }, 2000);
        }
    }
}

function requestFrame() {
    socket.emit('get_frame');
}

if (document.getElementById('camera-feed')) {
    requestFrame();
}

