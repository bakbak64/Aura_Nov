import os
import vosk
import json
import pyaudio
import threading
from typing import Optional, Callable


class WakeWordDetector:
    def __init__(self, config: dict):
        self.config = config
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "vosk-model-small-en-us-0.15")
        if not os.path.exists(self.model_path):
            self.model_path = "models/vosk-model-small-en-us-0.15"
        self.wake_word = config['voice'].get('wake_word', 'hey aura').lower()
        self.model = None
        self.rec = None
        self.is_listening = False
        self.callback = None
        self.thread = None
        
    def _load_model(self) -> bool:
        try:
            self.model = vosk.Model(self.model_path)
            self.rec = vosk.KaldiRecognizer(self.model, 16000)
            return True
        except Exception as e:
            print(f"Wake word model loading error: {e}")
            return False

    def start_listening(self, callback: Callable):
        if self.is_listening:
            return
        
        if not self.model:
            if not self._load_model():
                return
        
        self.callback = callback
        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def _listen_loop(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
        
        buffer = ""
        
        while self.is_listening:
            data = stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result())
                text = result.get('text', '').lower()
                if text:
                    buffer += " " + text
                    
                    if self.wake_word in buffer:
                        if self.callback:
                            self.callback()
                        buffer = ""
            else:
                partial = json.loads(self.rec.PartialResult())
                text = partial.get('partial', '').lower()
                if self.wake_word in text:
                    if self.callback:
                        self.callback()
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop_listening(self):
        self.is_listening = False
        if self.thread:
            self.thread.join(timeout=2)

