document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    
    if (startBtn) {
        startBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/session/start', {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (response.ok) {
                    console.log('Session started:', data);
                    startBtn.classList.add('hidden');
                    stopBtn.classList.remove('hidden');
                    document.getElementById('status-indicator').classList.replace('bg-gray-400', 'bg-green-500');
                    document.getElementById('status-text').textContent = 'Active';
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error starting session: ' + error.message);
            }
        });
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/session/stop', {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (response.ok) {
                    console.log('Session stopped');
                    stopBtn.classList.add('hidden');
                    startBtn.classList.remove('hidden');
                    document.getElementById('status-indicator').classList.replace('bg-green-500', 'bg-gray-400');
                    document.getElementById('status-text').textContent = 'Stopped';
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error stopping session: ' + error.message);
            }
        });
    }
    
    const voiceCommandBtn = document.getElementById('voice-command-btn');
    if (voiceCommandBtn) {
        voiceCommandBtn.addEventListener('click', async () => {
            const command = prompt('Enter voice command:');
            if (command) {
                try {
                    const response = await fetch('/api/voice/command', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ command: command })
                    });
                    const data = await response.json();
                    console.log('Voice command response:', data);
                } catch (error) {
                    console.error('Error sending voice command:', error);
                }
            }
        });
    }
});

