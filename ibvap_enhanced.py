import cv2
import torch
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime
import os

class IBVAP:
    def __init__(self, rtsp_url, model_path='models/yolov8n.pt'):
        self.rtsp_url = rtsp_url
        self.model = YOLO(model_path)
        self.model.to('cuda')
        
        self.tracking_history = {}
        self.alert_log = []
        self.frame_count = 0
        
        # Virtual fence for 1080p
        self.fence_start = (0, 540)
        self.fence_end = (1920, 540)
        
        print(f"✅ IBVAP Initialized")
        print(f"✅ Model: {model_path}")
        print(f"✅ GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
        print(f"✅ RTSP: {rtsp_url}")
        print("=" * 50)

    def draw_virtual_fence(self, frame):
        cv2.line(frame, self.fence_start, self.fence_end, (0, 0, 255), 2)
        cv2.putText(frame, "🔴 VIRTUAL FENCE", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return frame

    def check_intrusion(self, box, track_id):
        x1, y1, x2, y2 = box
        center_y = (y1 + y2) // 2
        fence_y = self.fence_start[1]
        
        if abs(center_y - fence_y) < 30:
            alert_msg = f"⚠️ ALERT: Track ID {track_id} crossed the fence at {datetime.now()}"
            self.alert_log.append(alert_msg)
            print(alert_msg)
            return True
        return False

    def process_frame(self, frame):
        self.frame_count += 1
        
        results = self.model.track(frame, persist=True, verbose=False)
        
        annotated_frame = results[0].plot()
        annotated_frame = self.draw_virtual_fence(annotated_frame)
        
        if hasattr(results[0], 'boxes') and results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy() if results[0].boxes.id is not None else None
            
            if track_ids is not None:
                for box, track_id in zip(boxes, track_ids):
                    intruded = self.check_intrusion(box, track_id)
                    if intruded:
                        x1, y1, x2, y2 = box.astype(int)
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        
        self.add_info_overlay(annotated_frame)
        return annotated_frame

    def add_info_overlay(self, frame):
        h, w = frame.shape[:2]
        
        fps_text = f"FPS: {self.fps:.1f}" if hasattr(self, 'fps') else "FPS: --"
        cv2.putText(frame, fps_text, (w - 200, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Frame: {self.frame_count}", (w - 200, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Alerts: {len(self.alert_log)}", (w - 200, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def run(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        
        if not cap.isOpened():
            raise RuntimeError(f"Could not connect to RTSP stream: {self.rtsp_url}")
        
        print("✅ Connected to RTSP stream")
        print("🔴 Press 'q' to quit")
        print("=" * 50)
        
        fps_start = time.time()
        fps_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Failed to read frame")
                break
            
            # NO RESIZE - full quality!
            frame = cv2.resize(frame, (1600, 900))  # REMOVED
            
            annotated_frame = self.process_frame(frame)
            
            fps_count += 1
            if time.time() - fps_start >= 1:
                self.fps = fps_count
                fps_count = 0
                fps_start = time.time()
            
            cv2.imshow('IBVAP - Intelligent Border Video Analytics Platform', annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print("=" * 50)
        print("📊 SESSION SUMMARY")
        print(f"Total frames processed: {self.frame_count}")
        print(f"Total alerts generated: {len(self.alert_log)}")
        if self.alert_log:
            print("\n🔴 ALERT LOG:")
            for alert in self.alert_log[-10:]:
                print(f"  {alert}")
        print("=" * 50)

if __name__ == "__main__":
    RTSP_URL = "rtsp://127.0.0.1:8554/border"
    ibvap = IBVAP(RTSP_URL)
    ibvap.run()

