import cv2
import torch
from ultralytics import YOLO
import time
from datetime import datetime

class IBVAP:
    def __init__(self, rtsp_url, model_path='models/yolov8n.pt'):
        self.rtsp_url = rtsp_url
        
        # Object detection model
        self.model = YOLO(model_path)
        self.model.to('cuda')
        
        # Face detection using OpenCV's CascadeClassifier
        # Use cv2.face or try the correct path
        try:
            # Try the standard path
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            print(f"✅ Face cascade loaded from: {cascade_path}")
        except Exception as e:
            print(f"⚠️ Could not load face cascade: {e}")
            self.face_cascade = None
        
        self.alert_log = []
        self.frame_count = 0
        self.fps = 0
        
        # Virtual fence
        self.fence_start = (0, 540)
        self.fence_end = (1920, 540)
        
        print(f"✅ IBVAP with Face Detection")
        print(f"✅ GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
        print("=" * 50)

    def draw_virtual_fence(self, frame):
        cv2.line(frame, self.fence_start, self.fence_end, (0, 0, 255), 2)
        cv2.putText(frame, "🔴 VIRTUAL FENCE", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return frame

    def detect_faces(self, frame):
        """Detect faces using OpenCV Haar Cascade"""
        if self.face_cascade is None:
            return frame, 0
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "👤 FACE", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame, len(faces)

    def process_frame(self, frame):
        self.frame_count += 1
        
        # Run YOLO with tracking
        results = self.model.track(frame, persist=True, verbose=False)
        
        # Check if results has boxes
        if results and len(results) > 0:
            annotated_frame = results[0].plot()
        else:
            annotated_frame = frame.copy()
        
        # Detect faces (works even if YOLO fails)
        annotated_frame, face_count = self.detect_faces(annotated_frame)
        
        # Draw virtual fence
        annotated_frame = self.draw_virtual_fence(annotated_frame)
        
        # Check intrusions
        if results and len(results) > 0:
            if hasattr(results[0], 'boxes') and results[0].boxes is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.cpu().numpy() if results[0].boxes.id is not None else None
                
                if track_ids is not None:
                    for box, track_id in zip(boxes, track_ids):
                        self.check_intrusion(box, track_id)
        
        # Add overlay with face count
        self.add_info_overlay(annotated_frame, face_count)
        return annotated_frame

    def check_intrusion(self, box, track_id):
        x1, y1, x2, y2 = box
        center_y = (y1 + y2) // 2
        fence_y = self.fence_start[1]
        
        if abs(center_y - fence_y) < 30:
            alert_msg = f"⚠️ ALERT: Track ID {track_id} crossed fence at {datetime.now()}"
            self.alert_log.append(alert_msg)
            print(alert_msg)
            return True
        return False

    def add_info_overlay(self, frame, face_count):
        h, w = frame.shape[:2]
        
        # Background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (w-280, 10), (w-10, 130), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        fps_text = f"FPS: {self.fps:.1f}" if self.fps else "FPS: --"
        cv2.putText(frame, fps_text, (w-270, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Frame: {self.frame_count}", (w-270, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Alerts: {len(self.alert_log)}", (w-270, 85), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Faces: {face_count}", (w-270, 110), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

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
                break
            
            # Process at full resolution
            frame = cv2.resize(frame, (1920, 1080))
            annotated_frame = self.process_frame(frame)
            
            fps_count += 1
            if time.time() - fps_start >= 1:
                self.fps = fps_count
                fps_count = 0
                fps_start = time.time()
            
            cv2.imshow('IBVAP - Face Detection + Border Surveillance', annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print("=" * 50)
        print("📊 SESSION SUMMARY")
        print(f"Total frames: {self.frame_count}")
        print(f"Total alerts: {len(self.alert_log)}")
        if self.alert_log:
            print("\n🔴 ALERT LOG:")
            for alert in self.alert_log[-5:]:
                print(f"  {alert}")

if __name__ == "__main__":
    ibvap = IBVAP("rtsp://127.0.0.1:8554/border")
    ibvap.run()
