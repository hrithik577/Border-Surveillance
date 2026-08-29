# ============================================================
# IBVAP - Analytics & Detection Module
# Precision Defence-Grade Bounding Boxes & Stable Inference
# ============================================================

import os
import cv2
import time
import torch
import logging
import numpy as np
from datetime import datetime
from collections import deque

logger = logging.getLogger("IBVAP.Analytics")

class ObjectDetector:
    """YOLOv8 based object detector with high-speed inference & perimeter alert analytics."""
    
    def __init__(self, model_path="data/models/yolov8n.pt", fence_y=420, confidence=0.25):
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
            
            device = 'cpu'
            if torch.cuda.is_available():
                try:
                    test_t = torch.zeros((1, 3, 32, 32), device='cuda')
                    _ = torch.nn.functional.conv2d(test_t, torch.zeros((3, 3, 3, 3), device='cuda'))
                    device = 'cuda'
                except Exception as e:
                    logger.warning(f"CUDA present but GPU kernel test failed ({e}). Defaulting to CPU.")
                    device = 'cpu'

            if device == 'cpu':
                try:
                    torch.backends.mkldnn.enabled = False
                except Exception:
                    pass
            self.model.to(device)
            logger.info(f"YOLO model initialized on device: {device}")

        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None

    def process_frame(self, frame):
        """Processes a frame, draws ultra-crisp C4ISR bounding boxes & virtual fence line."""
        if frame is None:
            return None, {'people': 0, 'vehicles': 0, 'alerts': len(self.alerts)}
            
        h, w = frame.shape[:2]
        people_count = 0
        vehicle_count = 0
        annotated_frame = frame.copy()
        
        # Adjust fence line relative to frame height
        fence_line_y = int(h * 0.65)
        
        if self.model is not None:
            try:
                # Fast predict mode without optical flow GMC crashes
                results = self.model.predict(frame, verbose=False, conf=self.confidence)
                if results and len(results) > 0:
                    boxes = results[0].boxes
                    if boxes is not None and len(boxes) > 0:
                        for idx, box in enumerate(boxes):
                            cls_id = int(box.cls[0])
                            conf = float(box.conf[0])
                            
                            xyxy = box.xyxy[0].cpu().numpy().astype(int)
                            x1, y1, x2, y2 = xyxy[0], xyxy[1], xyxy[2], xyxy[3]
                            
                            # Class 0: person
                            if cls_id == 0:
                                people_count += 1
                                tid_str = f"P-0{idx + 14}"
                                label = f"{tid_str} | PERSON | {int(conf * 100)}%"
                                color = (68, 68, 255) if y2 > fence_line_y else (0, 212, 255)
                                
                                # Draw thin, sharp bounding box
                                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                                
                                # Label tag background box
                                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                                cv2.rectangle(annotated_frame, (x1, max(0, y1 - 20)), (x1 + tw + 8, max(0, y1)), (15, 23, 35), -1)
                                cv2.rectangle(annotated_frame, (x1, max(0, y1 - 20)), (x1 + tw + 8, max(0, y1)), color, 1)
                                cv2.putText(annotated_frame, label, (x1 + 4, max(14, y1 - 5)),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

                                # Boundary breach trigger
                                if y2 > fence_line_y:
                                    self._trigger_alert("PERIMETER BREACH", f"Track {tid_str} crossed border line at Y={y2}")

                            # Class 2 (car), 3 (motorcycle), 5 (bus), 7 (truck)
                            elif cls_id in [2, 3, 5, 7]:
                                vehicle_count += 1
                                vtypes = {2: 'CAR', 3: 'M-CYCLE', 5: 'BUS', 7: 'TRUCK'}
                                vtype_str = vtypes.get(cls_id, 'VEHICLE')
                                tid_str = f"V-0{idx + 80}"
                                label = f"{tid_str} | {vtype_str} | {int(conf * 100)}%"
                                color = (0, 212, 255)
                                
                                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                                cv2.rectangle(annotated_frame, (x1, max(0, y1 - 20)), (x1 + tw + 8, max(0, y1)), (15, 23, 35), -1)
                                cv2.rectangle(annotated_frame, (x1, max(0, y1 - 20)), (x1 + tw + 8, max(0, y1)), color, 1)
                                cv2.putText(annotated_frame, label, (x1 + 4, max(14, y1 - 5)),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

            except Exception as e:
                logger.warning(f"Detection inference warning: {e}")

        # Draw virtual fence line
        cv2.line(annotated_frame, (0, fence_line_y), (w, fence_line_y), (68, 68, 239), 2)
        cv2.putText(annotated_frame, "RESTRICTED BORDER PERIMETER LINE", (15, fence_line_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (68, 68, 239), 2)

        # Header Telemetry Overlay
        cv2.rectangle(annotated_frame, (0, 0), (w, 32), (10, 15, 24), -1)
        cv2.line(annotated_frame, (0, 32), (w, 32), (40, 60, 90), 1)
        t_str = datetime.now().strftime("%H:%M:%S IST")
        cv2.putText(annotated_frame, f"IBVAP AI SURVEILLANCE FEED | {t_str} | PERSONS: {people_count} | VEHICLES: {vehicle_count}",
                    (15, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 212, 255), 1)

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

    def get_alerts(self):
        return list(self.alerts)
