import google.generativeai as genai
import os
import time
import base64
from typing import Optional, Dict
import cv2
import io
from PIL import Image


class SceneAI:
    def __init__(self, config: dict):
        self.config = config
        self.api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        self.model = None
        self.cache = {}
        self.cache_duration = config['gemini'].get('cache_duration_seconds', 10)
        self.rate_limit = config['gemini'].get('rate_limit_per_minute', 15)
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro-vision')
            except Exception as e:
                print(f"Gemini API initialization error: {e}")

    def describe_scene(self, frame, cache_key: Optional[str] = None) -> str:
        if not self.model:
            return "Scene description unavailable. Please check API configuration."
        
        if cache_key:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result
        
        if not self._check_rate_limit():
            return "Rate limit reached. Please wait a moment."
        
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            image_bytes = buffer.tobytes()
            image = Image.open(io.BytesIO(image_bytes))
            
            prompt = """Describe this scene for a blind person. Focus on:
- People and their actions
- Objects and their locations
- Potential hazards
- Spatial layout
Be concise (2-4 sentences)."""
            
            response = self.model.generate_content([prompt, image])
            description = response.text.strip()
            
            if cache_key:
                self._save_to_cache(cache_key, description)
            
            return description
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "Unable to analyze scene. Please try again."

    def detect_traffic_light(self, frame) -> Optional[str]:
        if not self.model:
            return None
        
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            image_bytes = buffer.tobytes()
            image = Image.open(io.BytesIO(image_bytes))
            
            prompt = "What color is the traffic light in this image? Answer only with: red, yellow, green, or none."
            
            response = self.model.generate_content([prompt, image])
            color = response.text.strip().lower()
            
            if color in ['red', 'yellow', 'green']:
                return color
            return None
        except Exception as e:
            print(f"Traffic light detection error: {e}")
            return None

    def _check_rate_limit(self) -> bool:
        current_time = time.time()
        
        if current_time - self.request_window_start > 60:
            self.request_window_start = current_time
            self.request_count = 0
        
        if self.request_count >= self.rate_limit:
            return False
        
        self.request_count += 1
        return True

    def _get_from_cache(self, key: str) -> Optional[str]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.cache_duration:
                return entry['value']
            else:
                del self.cache[key]
        return None

    def _save_to_cache(self, key: str, value: str):
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }

