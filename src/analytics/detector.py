# ============================================================
# IBVAP - Analytics & Detection Module
# Precision Defence-Grade Bounding Boxes & Tracking
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
    """YOLOv8 based object detector with tracking and fence breach analytics."""
    
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
        
        # Adjust default fence_y relative to frame height
        fence_line_y = int(h * 0.65)
        
        if self.model is not None:
            try:
                results = self.model.track(frame, persist=True, verbose=False, conf=self.confidence)
                if results and len(results) > 0:
                    boxes = results[0].boxes
                    if boxes is not None and len(boxes) > 0:
                        for box in boxes:
                            cls_id = int(box.cls[0])
                            conf = float(box.conf[0])
                            track_id = int(box.id[0]) if box.id is not None else None
                            
                            xyxy = box.xyxy[0].cpu().numpy().astype(int)
                            x1, y1, x2, y2 = xyxy[0], xyxy[1], xyxy[2], xyxy[3]
                            
                            # Class 0: person
                            if cls_id == 0:
                                people_count += 1
                                tid_str = f"P-0{track_id}" if track_id else f"P-014"
                                label = f"{tid_str} | PERSON | {int(conf * 100)}%"
                                color = (255, 68, 68) if y2 > fence_line_y else (255, 180, 0)
                                
                                # Draw thin, sharp 1px bounding box
                                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 1)
                                
                                # Draw top-left & bottom-right corner accents for high-tech look
                                corner_len = min(15, (x2 - x1) // 3, (y2 - y1) // 3)
                                if corner_len > 3:
                                    cv2.line(annotated_frame, (x1, y1), (x1 + corner_len, y1), color, 2)
                                    cv2.line(annotated_frame, (x1, y1), (x1, y1 + corner_len), color, 2)
                                    cv2.line(annotated_frame, (x2, y2), (x2 - corner_len, y2), color, 2)
                                    cv2.line(annotated_frame, (x2, y2), (x2, y2 - corner_len), color, 2)
                                
                                # Label tag background box
                                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                                cv2.rectangle(annotated_frame, (x1, max(0, y1 - 18)), (x1 + tw + 6, max(0, y1)), (15, 23, 35), -1)
                                cv2.rectangle(annotated_frame, (x1, max(0, y1 - 18)), (x1 + tw + 6, max(0, y1)), color, 1)
                                cv2.putText(annotated_frame, label, (x1 + 3, max(12, y1 - 4)),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

                                # Check boundary breach
                                if y2 > fence_line_y:
                                    self._trigger_alert("PERIMETER BREACH", f"Track {tid_str} crossed border line at Y={y2}")

                            # Class 2 (car), 3 (motorcycle), 5 (bus), 7 (truck)
                            elif cls_id in [2, 3, 5, 7]:
                                vehicle_count += 1
                                vtypes = {2: 'CAR', 3: 'M-CYCLE', 5: 'BUS', 7: 'TRUCK'}
                                vtype_str = vtypes.get(cls_id, 'VEHICLE')
                                tid_str = f"V-0{track_id}" if track_id else f"V-082"
                                label = f"{tid_str} | {vtype_str} | {int(conf * 100)}%"
                                color = (255, 212, 0)
                                
                                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 1)
                                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                                cv2.rectangle(annotated_frame, (x1, max(0, y1 - 18)), (x1 + tw + 6, max(0, y1)), (15, 23, 35), -1)
                                cv2.rectangle(annotated_frame, (x1, max(0, y1 - 18)), (x1 + tw + 6, max(0, y1)), color, 1)
                                cv2.putText(annotated_frame, label, (x1 + 3, max(12, y1 - 4)),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            except Exception as e:
                logger.warning(f"Detection inference warning: {e}")

        # Draw virtual fence line
        cv2.line(annotated_frame, (0, fence_line_y), (w, fence_line_y), (68, 68, 239), 2)
        cv2.putText(annotated_frame, "RESTRICTED BORDER PERIMETER LINE", (15, fence_line_y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (68, 68, 239), 2)

        # Header Telemetry Overlay
        cv2.rectangle(annotated_frame, (0, 0), (w, 32), (10, 15, 24), -1)
        cv2.line(annotated_frame, (0, 32), (w, 32), (40, 60, 90), 1)
        t_str = datetime.now().strftime("%H:%M:%S IST")
        cv2.putText(annotated_frame, f"IBVAP AI STREAM | {t_str} | PERSONS: {people_count} | VEHICLES: {vehicle_count}",
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
