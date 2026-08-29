import cv2
import torch
from ultralytics import YOLO

# Load YOLO model
model = YOLO('yolov8n.pt')

# Use the video file directly
video_path = 'VIRAT_S_000001.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    raise RuntimeError(f"Could not open video: {video_path}")

print(f"Processing video: {video_path}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Using GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Run YOLO inference
    results = model(frame)
    
    # Render results
    annotated_frame = results[0].plot()
    
    # Display
    cv2.imshow('YOLO Detection - IBVAP', annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Processing complete!")
