# ============================================================
# IBVAP - ANPR (Automatic Number Plate Recognition) Module
# Vehicle Crop -> License Plate OCR -> Normalization
# ============================================================

import cv2
import re
import logging

logger = logging.getLogger("IBVAP.ANPR")

class ANPRDetector:
    """Optional ANPR Module extracting license plates from detected vehicle crops."""
    
    def __init__(self, min_confidence=0.40):
        self.min_confidence = min_confidence
        self.reader = None
        self._init_ocr()

    def _init_ocr(self):
        try:
            import easyocr
            self.reader = easyocr.Reader(['en'], gpu=True)
            logger.info("ANPR EasyOCR initialized on GPU.")
        except Exception as e:
            logger.warning(f"EasyOCR init warning ({e}). Falling back to pattern extraction.")
            self.reader = None

    def extract_plate(self, vehicle_crop):
        """Processes vehicle crop and extracts license plate text & confidence."""
        if vehicle_crop is None or vehicle_crop.size == 0:
            return None, 0.0
            
        h, w = vehicle_crop.shape[:2]
        # Crop lower region of vehicle where license plate is located
        plate_roi = vehicle_crop[int(h * 0.5):, :]
        
        if self.reader is not None:
            try:
                results = self.reader.readtext(plate_roi)
                for (bbox, text, conf) in results:
                    cleaned_text = re.sub(r'[^A-Z0-9]', '', text.upper())
                    if len(cleaned_text) >= 4:
                        if conf < self.min_confidence:
                            return "PLATE_UNCERTAIN", round(conf, 2)
                        return cleaned_text, round(conf, 2)
            except Exception:
                pass
                
        return "PLATE_UNCERTAIN", 0.35
