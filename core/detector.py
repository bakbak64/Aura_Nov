import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
import os
from pathlib import Path


class ObjectDetector:
    def __init__(self, config: dict):
        self.config = config
        self.model = None
        self.model_size = config['detection'].get('model_size', 'n')
        self.confidence_threshold = config['detection'].get('confidence_threshold', 0.25)
        self.classes = config['detection'].get('classes', [])
        self._load_model()

    def _load_model(self):
        try:
            model_name = f"yolov8{self.model_size}.pt"
            self.model = YOLO(model_name)
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            if 'WeightsUnpickler error' in str(e) or 'safe_globals' in str(e):
                print("\nThis error is due to an update in PyTorch (>=2.6) restricting pickling of globals when loading YOLO model files.\n" 
                      "To fix, ensure you trust the source of your model weights. To override this restriction, either:\n" 
                      "1. Use torch.serialization.safe_globals([ultralytics.nn.tasks.DetectionModel]) if coding directly (see https://pytorch.org/docs/stable/generated/torch.load.html).\n"
                      "2. Use an older version of PyTorch (<2.6) or wait for an update from Ultralytics that resolves this.\n" 
                      "3. If using a patched Ultralytics YOLO, upgrade the ultralytics/yolov8 package.\n")
            self.model = None

    def detect(self, frame: np.ndarray, frame_skip: int = 1) -> List[Dict]:
        if self.model is None:
            return []

        try:
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names[cls_id]
                    
                    if self.classes and cls_name not in self.classes:
                        continue
                    
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].cpu().numpy()]
                    
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    
                    width = float(x2 - x1)
                    height = float(y2 - y1)
                    
                    frame_center_x = frame.shape[1] / 2
                    frame_center_y = frame.shape[0] / 2
                    
                    rel_x = center_x - frame_center_x
                    rel_y = center_y - frame_center_y
                    
                    if abs(rel_x) > abs(rel_y):
                        direction = "left" if rel_x < 0 else "right"
                    else:
                        direction = "front" if rel_y < 0 else "behind"
                    
                    detections.append({
                        'class': cls_name,
                        'confidence': float(conf),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'center': (int(center_x), int(center_y)),
                        'size': (width, height),
                        'direction': direction,
                        'priority': self._get_priority(cls_name, height, frame.shape[0])
                    })
            
            return detections
        except Exception as e:
            print(f"Detection error: {e}")
            return []

    def _get_priority(self, class_name: str, bbox_height: float, frame_height: int) -> str:
        height_ratio = bbox_height / frame_height
        
        if class_name in ['fire', 'smoke'] or (class_name in ['car', 'truck', 'bus'] and height_ratio > 0.3):
            return 'critical'
        elif class_name == 'person' and height_ratio > 0.2:
            return 'important'
        else:
            return 'informational'

