import pyttsx3
import speech_recognition as sr
import threading
from typing import Optional, Callable
import queue


class VoiceSystem:
    def __init__(self, config: dict):
        self.config = config
        self.tts_engine = None
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.speaking = False
        self.speech_queue = queue.Queue()
        self.interrupt_flag = threading.Event()
        self._init_tts()
        self._init_microphone()

    def _init_tts(self):
        try:
            self.tts_engine = pyttsx3.init()
            rate = self.config['voice'].get('tts_rate', 150)
            volume = self.config['voice'].get('tts_volume', 0.8)
            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.setProperty('volume', volume)
            
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
        except Exception as e:
            print(f"TTS initialization error: {e}")

    def _init_microphone(self):
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Microphone initialization error: {e}")

    def speak(self, text: str, interrupt: bool = False):
        if interrupt:
            self.interrupt_speech()
        
        if self.tts_engine:
            self.speech_queue.put(text)
            if not self.speaking:
                threading.Thread(target=self._speak_thread, daemon=True).start()

    def _speak_thread(self):
        self.speaking = True
        while not self.speech_queue.empty() and not self.interrupt_flag.is_set():
            try:
                text = self.speech_queue.get(timeout=0.1)
                if not self.interrupt_flag.is_set():
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
            except queue.Empty:
                break
        
        self.interrupt_flag.clear()
        self.speaking = False

    def interrupt_speech(self):
        self.interrupt_flag.set()
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except:
                break

    def listen(self, callback: Optional[Callable] = None, timeout: int = 3, phrase_time_limit: int = 5) -> Optional[str]:
        if not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            text = self.recognizer.recognize_google(audio)
            
            if callback:
                callback(text)
            
            return text.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return None

    def set_volume(self, volume: float):
        if self.tts_engine and 0.0 <= volume <= 1.0:
            self.config['voice']['tts_volume'] = volume
            self.tts_engine.setProperty('volume', volume)

    def set_rate(self, rate: int):
        if self.tts_engine and 50 <= rate <= 300:
            self.config['voice']['tts_rate'] = rate
            self.tts_engine.setProperty('rate', rate)

