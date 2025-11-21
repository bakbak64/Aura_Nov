import cv2
import threading
import time
from typing import Optional, Tuple


class Camera:
    def __init__(self, config: dict):
        self.config = config
        self.cap = None
        self.running = False
        self.frame = None
        self.lock = threading.Lock()
        self.thread = None
        self.fps = config['camera'].get('fps', 20)

    def start(self) -> bool:
        if self.running:
            return True
        
        try:
            self.cap = cv2.VideoCapture(self.config['camera']['device_id'])
            if not self.cap.isOpened():
                return False
            
            width = self.config['camera']['resolution_width']
            height = self.config['camera']['resolution_height']
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            return True
        except Exception as e:
            print(f"Camera error: {e}")
            return False

    def _capture_loop(self):
        frame_time = 1.0 / self.fps
        while self.running:
            start_time = time.time()
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame.copy()
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)

    def get_frame(self) -> Optional[Tuple[bytes, bytes]]:
        with self.lock:
            if self.frame is None:
                return None
            frame_copy = self.frame.copy()
        
        ret, buffer = cv2.imencode('.jpg', frame_copy, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            return None
        
        ret_png, buffer_png = cv2.imencode('.png', frame_copy)
        if not ret_png:
            return None
        
        return buffer.tobytes(), buffer_png.tobytes()

    def get_raw_frame(self) -> Optional[bytes]:
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
        self.frame = None

    def is_running(self) -> bool:
        return self.running

