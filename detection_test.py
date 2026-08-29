# ============================================================
# IBVAP - Fixed Detection Dashboard
# ============================================================

import os
import cv2
import numpy as np
from ultralytics import YOLO
from flask import Flask, Response, render_template, jsonify
import time
import threading

# ============================================================
# CONFIGURATION
# ============================================================

VIDEO_PATH = "C:/IBVAP-Demo/data/videos/pedestrian_dataset.mp4"
MODEL_PATH = "C:/IBVAP-Demo/data/models/yolov8n.pt"

# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

# ============================================================
# LOAD YOLO MODEL
# ============================================================

print("=" * 70)
print("🛡️ IBVAP - Fixed Detection")
print("=" * 70)

print("Loading YOLO model...")
try:
    model = YOLO(MODEL_PATH)
    print("✅ YOLO loaded")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

print("Loading video...")
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"❌ Could not open video: {VIDEO_PATH}")
    exit()
print("✅ Video loaded successfully!")

# ============================================================
# VIDEO GENERATOR WITH FIXED DETECTION
# ============================================================

def generate_frames():
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        frame_count += 1
        
        # Ensure frame is valid
        if frame is None or frame.size == 0:
            continue
        
        try:
            # Convert to RGB if needed (YOLO expects RGB)
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # Frame is already BGR (OpenCV default)
                pass
            
            # Resize for better performance
            frame_resized = cv2.resize(frame, (640, 640))
            
            # Run YOLO detection with explicit parameters
            results = model(frame_resized, conf=0.25, iou=0.45, verbose=False)
            
            # Plot results
            annotated = results[0].plot()
            
            # Count detections
            detection_count = 0
            if results[0].boxes is not None:
                detection_count = len(results[0].boxes)
                
                # Add detection info
                cv2.putText(annotated, f"Detections: {detection_count}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Show class names
                if detection_count > 0:
                    classes = results[0].boxes.cls.cpu().numpy()
                    for i, cls in enumerate(classes):
                        class_name = model.names[int(cls)]
                        cv2.putText(annotated, f"{class_name}", (10, 60 + i*25), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            cv2.putText(annotated, f"Frame: {frame_count}", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Print status
            if frame_count % 30 == 0:
                print(f"Frame {frame_count}: {detection_count} detections")
                
        except Exception as e:
            print(f"Detection error at frame {frame_count}: {e}")
            annotated = frame
            cv2.putText(annotated, f"ERROR: {str(e)[:50]}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Encode frame
        ret, jpeg = cv2.imencode('.jpg', annotated)
        if not ret:
            continue
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + 
               jpeg.tobytes() + b'\r\n')

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>IBVAP - Detection Test</title>
        <style>
            body { background: #0a0e17; color: white; font-family: sans-serif; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { color: #00d4ff; }
            .video { width: 100%; background: #0d1520; border-radius: 12px; }
            .info { color: #8899aa; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ IBVAP - Detection Test</h1>
            <img class="video" src="/video_feed">
            <p class="info">Looking for pedestrians... Green boxes = detections</p>
        </div>
    </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("=" * 70)
    print("🌐 Detection Test: http://localhost:5002")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5002, debug=False)
