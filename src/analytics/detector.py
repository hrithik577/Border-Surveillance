# ============================================================
# IBVAP - Analytics & Detection Module
# ============================================================

import os
import cv2
import time
import torch
import logging
from datetime import datetime
from collections import deque

logger = logging.getLogger("IBVAP.Analytics")

class ObjectDetector:
    """YOLOv8 based object detector with tracking and fence breach analytics."""
    
    def __init__(self, model_path="data/models/yolov8n.pt", fence_y=540, confidence=0.25):
        self.model_path = model_path
        self.fence_y = fence_y
        self.confidence = confidence
        self.alerts = deque(maxlen=200)
        self.model = None
        self._init_model()
        
    def _init_model(self):
        try:
            from ultralytics import YOLO
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
            else:
                logger.warning(f"Model path {self.model_path} not found. Loading fallback yolov8n.pt")
                self.model = YOLO("yolov8n.pt")
            
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model.to(device)
            logger.info(f"YOLO model initialized on device: {device}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None

    def process_frame(self, frame):
        """Processes a single frame, runs tracking, draws overlays, and evaluates alerts."""
        if frame is None:
            return None, {'people': 0, 'vehicles': 0, 'alerts': len(self.alerts)}
            
        people_count = 0
        vehicle_count = 0
        annotated_frame = frame.copy()
        
        if self.model is not None:
            results = self.model.track(frame, persist=True, verbose=False, conf=self.confidence)
            if results and len(results) > 0:
                annotated_frame = results[0].plot()
                boxes = results[0].boxes
                if boxes is not None:
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        # Class 0: person
                        if cls_id == 0:
                            people_count += 1
                            # Check fence breach
                            xyxy = box.xyxy[0].tolist()
                            bottom_y = xyxy[3]
                            if bottom_y > self.fence_y:
                                self._trigger_alert("FENCE BREACH", f"Person detected across border line (Y={int(bottom_y)})")
                        # Class 2 (car), 3 (motorcycle), 5 (bus), 7 (truck)
                        elif cls_id in [2, 3, 5, 7]:
                            vehicle_count += 1
                            
        # Draw virtual fence line
        h, w = annotated_frame.shape[:2]
        cv2.line(annotated_frame, (0, self.fence_y), (w, self.fence_y), (0, 0, 255), 2)
        cv2.putText(annotated_frame, "VIRTUAL BORDER FENCE", (10, self.fence_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
        stats = {
            'people': people_count,
            'vehicles': vehicle_count,
            'alerts': len(self.alerts)
        }
        return annotated_frame, stats

    def _trigger_alert(self, alert_type, message):
        alert_item = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': alert_type,
            'message': message
        }
        self.alerts.appendleft(alert_item)
        logger.warning(f"ALERT [{alert_type}]: {message}")

    def get_alerts(self):
        return list(self.alerts)
