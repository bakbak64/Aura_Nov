import time
from typing import Dict, Optional
from collections import deque


class AlertManager:
    def __init__(self, config: dict):
        self.config = config
        self.cooldowns = {}
        self.alert_history = deque(maxlen=100)
        self.last_critical_alert = 0
        self.critical_repeat_interval = config['alerts']['critical'].get('repeat_interval_seconds', 3)
        self.paused = False

    def should_alert(self, alert_type: str, priority: str, identifier: str = None) -> bool:
        if self.paused:
            return False
        
        current_time = time.time()
        key = f"{alert_type}_{identifier}" if identifier else alert_type
        
        if priority == 'critical':
            if current_time - self.last_critical_alert >= self.critical_repeat_interval:
                self.last_critical_alert = current_time
                return True
            return False
        
        elif priority == 'important':
            cooldown = self.config['alerts']['important'].get('cooldown_seconds', 30)
            if key in self.cooldowns:
                if current_time - self.cooldowns[key] < cooldown:
                    return False
            self.cooldowns[key] = current_time
            return True
        
        elif priority == 'informational':
            cooldown = self.config['alerts']['informational'].get('cooldown_seconds', 10)
            if key in self.cooldowns:
                if current_time - self.cooldowns[key] < cooldown:
                    return False
            self.cooldowns[key] = current_time
            return True
        
        return False

    def format_alert_message(self, priority: str, content: str) -> str:
        if priority == 'critical':
            return f"WARNING: {content}"
        elif priority == 'important':
            return f"Alert: {content}"
        else:
            return content

    def add_to_history(self, priority: str, message: str, metadata: Dict = None):
        self.alert_history.append({
            'timestamp': time.time(),
            'priority': priority,
            'message': message,
            'metadata': metadata or {}
        })

    def get_recent_alerts(self, limit: int = 50) -> list:
        return list(self.alert_history)[-limit:]

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def clear_cooldowns(self):
        self.cooldowns.clear()

