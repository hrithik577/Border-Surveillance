import cv2
import numpy as np
from ultralytics import YOLO
import os

# ============================================================
# CONFIGURATION
# ============================================================

VIDEO_PATH = "C:/IBVAP-Demo/data/videos/pedestrian_dataset.mp4"
MODEL_PATH = "C:/IBVAP-Demo/data/models/yolov8n.pt"

print("=" * 70)
print("🛡️ IBVAP - Debug Detection")
print("=" * 70)

# ============================================================
# CHECK VIDEO
# ============================================================

print("1. Checking video...")
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("❌ Could not open video")
    exit()

print(f"✅ Video opened successfully")

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"   FPS: {fps}")
print(f"   Resolution: {width}x{height}")
print(f"   Total Frames: {frame_count}")

# ============================================================
# LOAD MODEL
# ============================================================

print("2. Loading YOLO model...")
try:
    model = YOLO(MODEL_PATH)
    print("✅ YOLO loaded successfully")
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

# ============================================================
# TEST DETECTION ON FIRST FRAME
# ============================================================

print("3. Testing detection on first frame...")

ret, frame = cap.read()
if not ret or frame is None:
    print("❌ Could not read first frame")
    exit()

print(f"   Frame shape: {frame.shape}")

# Save frame for inspection
cv2.imwrite("C:/IBVAP-Demo/debug_frame.jpg", frame)
print("   ✅ Frame saved as debug_frame.jpg")

# Run detection with different confidence thresholds
for conf in [0.1, 0.25, 0.5]:
    try:
        results = model(frame, conf=conf, verbose=False)
        boxes = results[0].boxes
        
        if boxes is not None and len(boxes) > 0:
            print(f"   ✅ Conf {conf}: Found {len(boxes)} detections")
            
            # Show class names
            classes = boxes.cls.cpu().numpy()
            for i, cls in enumerate(classes):
                class_name = model.names[int(cls)]
                confidence = boxes.conf[i].item()
                print(f"      - {class_name} ({confidence:.2f})")
        else:
            print(f"   ❌ Conf {conf}: No detections")
            
    except Exception as e:
        print(f"   ❌ Conf {conf}: Error - {e}")

# ============================================================
# TEST WITH RESIZED FRAME
# ============================================================

print("4. Testing with resized frame...")

for size in [320, 416, 512, 640]:
    try:
        resized = cv2.resize(frame, (size, size))
        results = model(resized, conf=0.25, verbose=False)
        boxes = results[0].boxes
        
        if boxes is not None and len(boxes) > 0:
            print(f"   ✅ Size {size}: Found {len(boxes)} detections")
        else:
            print(f"   ❌ Size {size}: No detections")
            
    except Exception as e:
        print(f"   ❌ Size {size}: Error - {e}")

# ============================================================
# CREATE ANNOTATED IMAGE
# ============================================================

print("5. Creating annotated image...")

try:
    results = model(frame, conf=0.25, verbose=False)
    annotated = results[0].plot()
    cv2.imwrite("C:/IBVAP-Demo/annotated_frame.jpg", annotated)
    print("   ✅ Annotated frame saved as annotated_frame.jpg")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("=" * 70)
print("✅ Debug complete!")
print("   Check debug_frame.jpg and annotated_frame.jpg")
print("   Also check if the video actually contains people")
print("=" * 70)

cap.release()
