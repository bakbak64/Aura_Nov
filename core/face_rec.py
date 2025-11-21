import deepface
import numpy as np
import cv2
from typing import List, Tuple, Optional
import pickle
from pathlib import Path


class FaceRecognizer:
    def __init__(self, config: dict, database):
        self.config = config
        self.database = database
        self.tolerance = config['face_recognition'].get('tolerance', 0.6)
        self.model_name = config['face_recognition'].get('model_name', 'VGG-Face')
        self.known_faces = {}
        self.known_names = {}
        self.cooldowns = {}
        self.load_faces()

    def load_faces(self):
        faces = self.database.get_all_faces()
        self.known_faces = {}
        self.known_names = {}
        
        for face_data in faces:
            face_id = face_data['id']
            embedding = np.frombuffer(face_data['face_encoding'], dtype=np.float64)
            name = face_data['name']
            relationship = face_data['relationship']
            
            self.known_faces[face_id] = embedding
            self.known_names[face_id] = {'name': name, 'relationship': relationship}

    def add_face(self, image_path: str, name: str, relationship: str) -> Optional[int]:
        try:
            embedding_objs = deepface.DeepFace.represent(img_path=image_path, model_name=self.model_name, enforce_detection=True)
            if not embedding_objs:
                return None
            embedding = np.array(embedding_objs[0]['embedding'], dtype=np.float64)
            encoding_bytes = embedding.tobytes()
            
            face_id = self.database.add_face(name, relationship, encoding_bytes, image_path)
            
            if face_id:
                self.known_faces[face_id] = embedding
                self.known_names[face_id] = {'name': name, 'relationship': relationship}
            
            return face_id
        except Exception as e:
            print(f"Error adding face: {e}")
            return None

    def recognize(self, frame: np.ndarray, current_time: float) -> List[dict]:
        if not self.known_faces:
            return []

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detections = deepface.DeepFace.extract_faces(img_path=rgb_frame, target_size=(224, 224), detector_backend='opencv', enforce_detection=False)
            
            recognitions = []
            cooldown_seconds = self.config['face_recognition'].get('cooldown_seconds', 60)
            
            for detection in detections:
                face_img = detection['face']
                embedding_objs = deepface.DeepFace.represent(img_path=face_img, model_name=self.model_name, enforce_detection=False)
                if not embedding_objs:
                    continue
                embedding = np.array(embedding_objs[0]['embedding'], dtype=np.float64)
                best_match_id = None
                best_distance = float('inf')
                for kface_id, kembedding in self.known_faces.items():
                    dist = np.linalg.norm(kembedding - embedding)
                    if dist < best_distance:
                        best_distance = dist
                        best_match_id = kface_id
                if best_match_id is not None and best_distance < self.tolerance:
                    # bounding box for opencv detector: (x, y, w, h)
                    x, y, w, h = detection['facial_area'].values()
                    left = x
                    top = y
                    right = x + w
                    bottom = y + h
                    if self._check_cooldown(best_match_id, current_time, cooldown_seconds):
                        continue
                    frame_center_x = frame.shape[1] / 2
                    center_x = (left + right) / 2
                    rel_x = center_x - frame_center_x
                    if abs(rel_x) > frame.shape[1] * 0.15:
                        direction = "left" if rel_x < 0 else "right"
                    else:
                        direction = "front"
                    distance_feet = self._estimate_distance((bottom-top), frame.shape[0])
                    recognitions.append({
                        'face_id': best_match_id,
                        'name': self.known_names[best_match_id]['name'],
                        'relationship': self.known_names[best_match_id]['relationship'],
                        'confidence': float(1 - best_distance),
                        'bbox': [int(left), int(top), int(right), int(bottom)],
                        'direction': direction,
                        'distance_feet': float(distance_feet)
                    })
                    self.cooldowns[best_match_id] = current_time
            return recognitions
        except Exception as e:
            print(f"Face recognition error: {e}")
            return []

    def _check_cooldown(self, face_id: int, current_time: float, cooldown_seconds: int) -> bool:
        if face_id not in self.cooldowns:
            return False
        
        elapsed = current_time - self.cooldowns[face_id]
        return elapsed < cooldown_seconds

    def _estimate_distance(self, face_height: float, frame_height: int) -> float:
        ratio = face_height / frame_height
        if ratio > 0.15:
            return 3
        elif ratio > 0.08:
            return 5
        elif ratio > 0.05:
            return 8
        else:
            return 12

    def delete_face(self, face_id: int):
        if self.database.delete_face(face_id):
            self.known_faces.pop(face_id, None)
            self.known_names.pop(face_id, None)
            self.cooldowns.pop(face_id, None)
            return True
        return False

