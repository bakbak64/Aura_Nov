import pytesseract
import cv2
import numpy as np
from PIL import Image
from typing import Optional


class OCRReader:
    def __init__(self, config: dict):
        self.config = config
        self.language = config['ocr'].get('language', 'eng')
        self.preprocessing = config['ocr'].get('preprocessing', True)

    def read_text(self, image: np.ndarray) -> str:
        try:
            if self.preprocessing:
                processed_image = self._preprocess_image(image)
            else:
                processed_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            text = pytesseract.image_to_string(processed_image, lang=self.language)
            return text.strip()
        except Exception as e:
            print(f"OCR error: {e}")
            return ""

    def _preprocess_image(self, image: np.ndarray) -> Image.Image:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        contrast_factor = self.config['ocr'].get('contrast_factor', 1.5)
        gray = cv2.convertScaleAbs(gray, alpha=contrast_factor, beta=0)
        
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        kernel = np.ones((1, 1), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return Image.fromarray(binary)

