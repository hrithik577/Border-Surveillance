import cv2
import torch
from ultralytics import YOLO
import time
from datetime import datetime
import os

def resolve_path(candidates, default=""):
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return default

MODEL_PATH = resolve_path([
    "yolov8n.pt",
    "models/yolov8n.pt",
    "data/models/yolov8n.pt",
    "C:/IBVAP-Demo/models/yolov8n.pt"
], "yolov8n.pt")

VIDEO_PATH = resolve_path([
    "C:/IBVAP-Demo/data/videos/VIRAT_S_000001.mp4",
    "C:/Users/bhrit/Downloads/VIRAT_S_000001.mp4",
    "data/videos/VIRAT_S_000001.mp4",
    "VIRAT_S_000001.mp4"
], "VIRAT_S_000001.mp4")

try:
    from mtcnn import MTCNN
    face_detector = MTCNN()
    print("✅ Using MTCNN for face detection")
except ImportError:
    print("⚠️ MTCNN not installed. Face detection disabled.")
    face_detector = None

class IBVAP:
    def __init__(self, video_path):
        self.video_path = video_path
        
        actual_model_path = resolve_path([MODEL_PATH, "yolov8n.pt", "C:/IBVAP-Demo/models/yolov8n.pt"])
        if not os.path.exists(actual_model_path):
            raise FileNotFoundError(f"Model not found: {actual_model_path}")
        
        self.model = YOLO(actual_model_path)
        self.model.to('cuda' if torch.cuda.is_available() else 'cpu')

        
        self.alert_log = []
        self.frame_count = 0
        self.fps = 0
        
        # Virtual fence for 1080p
        self.fence_start = (0, 540)
        self.fence_end = (1920, 540)
        
        print(f"✅ IBVAP with Face Detection")
        print(f"✅ GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
        print(f"✅ Video: {video_path}")
        print(f"✅ Model: {MODEL_PATH}")
        print("=" * 50)

    def draw_virtual_fence(self, frame):
        cv2.line(frame, self.fence_start, self.fence_end, (0, 0, 255), 2)
        cv2.putText(frame, "🔴 VIRTUAL FENCE", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return frame

    def detect_faces_mtcnn(self, frame):
        if face_detector is None:
            return frame, 0
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_detector.detect_faces(rgb_frame)
        
        for face in faces:
            x, y, w, h = face['box']
            x, y = max(0, x), max(0, y)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"👤 FACE", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame, len(faces)

    def process_frame(self, frame):
        self.frame_count += 1
        
        # Run YOLO
        results = self.model.track(frame, persist=True, verbose=False)
        annotated_frame = results[0].plot()
        
        # Detect faces
        annotated_frame, face_count = self.detect_faces_mtcnn(annotated_frame)
        
        # Draw virtual fence
        annotated_frame = self.draw_virtual_fence(annotated_frame)
        
        # Check intrusions
        if hasattr(results[0], 'boxes') and results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy() if results[0].boxes.id is not None else None
            
            if track_ids is not None:
                for box, track_id in zip(boxes, track_ids):
                    x1, y1, x2, y2 = box
                    center_y = (y1 + y2) // 2
                    fence_y = self.fence_start[1]
                    
                    if abs(center_y - fence_y) < 30:
                        alert_msg = f"⚠️ ALERT: Track ID {track_id} crossed fence at {datetime.now()}"
                        self.alert_log.append(alert_msg)
                        print(alert_msg)
                        
                        x1, y1, x2, y2 = box.astype(int)
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        cv2.putText(annotated_frame, "🚨 INTRUSION!", (x1, y1-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        self.add_info_overlay(annotated_frame, face_count)
        return annotated_frame

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
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video: {self.video_path}")
        
        print("✅ Connected to video file")
        print("🔴 Press 'q' to quit")
        print("=" * 50)
        
        fps_start = time.time()
        fps_count = 0
        
        # Create display window
        cv2.namedWindow('IBVAP - Border Surveillance', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('IBVAP - Border Surveillance', 1920, 1080)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Use original quality - no resize!
            annotated_frame = self.process_frame(frame)
            
            fps_count += 1
            if time.time() - fps_start >= 1:
                self.fps = fps_count
                fps_count = 0
                fps_start = time.time()
            
            cv2.imshow('IBVAP - Border Surveillance', annotated_frame)
            
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
    ibvap = IBVAP(VIDEO_PATH)
    ibvap.run()
