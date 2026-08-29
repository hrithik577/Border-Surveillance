# ============================================================
# IBVAP - GPU-Optimized Dashboard
# ============================================================

import os
import cv2
import torch
import numpy as np
from ultralytics import YOLO
from flask import Flask, Response, render_template, jsonify
from flask_socketio import SocketIO, emit
import time
import threading
from collections import deque

# ============================================================
# CONFIGURATION
# ============================================================

VIDEO_PATH = "C:/IBVAP-Demo/data/videos/pedestrian_dataset.mp4"
MODEL_PATH = "C:/IBVAP-Demo/data/models/yolov8n.pt"

# ============================================================
# CHECK GPU
# ============================================================

print("=" * 70)
print("🛡️ IBVAP - GPU Mode")
print("=" * 70)

print("Checking GPU...")
if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✅ CUDA Version: {torch.version.cuda}")
    device = 'cuda'
else:
    print("⚠️ GPU not available, using CPU")
    device = 'cpu'

print(f"Using device: {device.upper()}")

# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ============================================================
# LOAD YOLO MODEL
# ============================================================

print("Loading YOLO model...")
try:
    model = YOLO(MODEL_PATH)
    model.to(device)
    print(f"✅ YOLO loaded on {device.upper()}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# ============================================================
# GLOBAL STATE
# ============================================================

alerts = deque(maxlen=100)
stats = {
    'total_frames': 0,
    'total_people': 0,
    'total_vehicles': 0,
    'total_alerts': 0,
    'fps': 0,
    'timestamp': '',
    'device': device.upper(),
    'detections': 0
}
processing = True
start_time = time.time()

# ============================================================
# VIDEO GENERATOR
# ============================================================

def generate_frames():
    global stats
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"❌ Could not open video: {VIDEO_PATH}")
        return
    
    print(f"✅ Video loaded: {VIDEO_PATH}")
    
    fps_start = time.time()
    fps_count = 0
    frame_delay = 1/30
    
    while processing:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        # Process frame
        frame = cv2.resize(frame, (1280, 720))
        
        try:
            # Run YOLO with GPU
            results = model(frame, conf=0.25, verbose=False)
            annotated = results[0].plot()
            
            # Count people and vehicles
            people_count = 0
            vehicle_count = 0
            det_count = 0
            
            if results[0].boxes is not None:
                classes = results[0].boxes.cls.cpu().numpy()
                det_count = len(classes)
                for cls in classes:
                    class_name = model.names[int(cls)]
                    if class_name == 'person':
                        people_count += 1
                    elif class_name in ['car', 'truck', 'bus', 'motorcycle', 'bicycle']:
                        vehicle_count += 1
            
            # Update stats
            stats['total_frames'] += 1
            stats['total_people'] += people_count
            stats['total_vehicles'] += vehicle_count
            stats['detections'] = det_count
            stats['timestamp'] = time.strftime('%H:%M:%S')
            
            # Draw overlay
            cv2.putText(annotated, f"👤 People: {people_count} | 🚗 Vehicles: {vehicle_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cv2.putText(annotated, f"🎯 Detections: {det_count} | ⚡ {device.upper()}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.putText(annotated, f"📊 FPS: {stats['fps']}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Emit stats
            socketio.emit('stats_update', {
                'total_frames': stats['total_frames'],
                'total_people': stats['total_people'],
                'total_vehicles': stats['total_vehicles'],
                'total_alerts': stats['total_alerts'],
                'fps': stats['fps'],
                'timestamp': stats['timestamp'],
                'device': device.upper(),
                'detections': det_count
            })
            
        except Exception as e:
            print(f"Detection error: {e}")
            annotated = frame
        
        # Encode
        ret, jpeg = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
        
        fps_count += 1
        if time.time() - fps_start >= 1:
            stats['fps'] = fps_count
            fps_count = 0
            fps_start = time.time()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + 
               jpeg.tobytes() + b'\r\n')
        
        time.sleep(frame_delay)
    
    cap.release()

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template('gpu_dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'stats': stats,
        'alerts': list(alerts)
    })

@app.route('/api/alerts')
def get_alerts():
    return jsonify({'alerts': list(alerts)})

# ============================================================
# CREATE HTML TEMPLATE
# ============================================================

os.makedirs('templates', exist_ok=True)

html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IBVAP - GPU Mode</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e17;
            color: #fff;
            min-height: 100vh;
            padding: 15px;
        }
        .dashboard { max-width: 1920px; margin: 0 auto; }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 25px;
            background: linear-gradient(135deg, #1a2332, #0d1520);
            border-radius: 12px;
            margin-bottom: 15px;
            border: 1px solid #2a3a4a;
        }
        .header h1 {
            font-size: 24px;
            background: linear-gradient(90deg, #00d4ff, #7b2ffc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .badge {
            background: #1a2332;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 12px;
            border: 1px solid #2a3a4a;
        }
        .badge.gpu { color: #00ff88; border-color: #00ff88; }
        .badge.cpu { color: #ffaa00; border-color: #ffaa00; }
        .status-dot {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #00ff88;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
            100% { opacity: 1; transform: scale(1); }
        }
        .grid { display: grid; grid-template-columns: 2fr 1fr; gap: 15px; }
        .video-container {
            background: #0d1520;
            border-radius: 12px;
            border: 1px solid #1a2a3a;
            overflow: hidden;
            position: relative;
        }
        .video-container img { width: 100%; height: auto; display: block; }
        .video-overlay {
            position: absolute; top: 15px; left: 15px;
            display: flex; gap: 15px; font-size: 11px;
            background: rgba(0,0,0,0.8);
            padding: 6px 12px;
            border-radius: 8px;
            border: 1px solid #2a3a4a;
            flex-wrap: wrap;
        }
        .video-overlay span { color: #00d4ff; }
        .sidebar { display: flex; flex-direction: column; gap: 15px; }
        .card {
            background: #0d1520;
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #1a2a3a;
        }
        .card h3 {
            color: #00d4ff;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        .stat-item {
            background: #1a2332;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-item .value {
            font-size: 22px;
            font-weight: bold;
            background: linear-gradient(90deg, #00d4ff, #7b2ffc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-item .label { font-size: 10px; color: #8899aa; margin-top: 2px; }
        .alerts-container {
            max-height: 150px;
            overflow-y: auto;
        }
        .alert-item {
            padding: 6px 10px;
            margin: 3px 0;
            border-radius: 6px;
            background: #1a2332;
            border-left: 3px solid #ff0044;
            font-size: 11px;
            color: #ccddee;
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #0d1520; }
        ::-webkit-scrollbar-thumb { background: #2a3a4a; border-radius: 4px; }
        @media (max-width: 1200px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🛡️ IBVAP <span style="font-size:14px;color:#667788;">GPU Accelerated</span></h1>
            <div>
                <span class="badge gpu" id="gpuStatus">⚡ GPU: Active</span>
                <span class="status-dot"></span>
                <span class="status-text" style="color:#00ff88;">LIVE</span>
            </div>
        </div>
        <div class="grid">
            <div class="video-container">
                <img src="{{ url_for('video_feed') }}" alt="Live Feed">
                <div class="video-overlay">
                    <span>📹 LIVE</span>
                    <span id="fps">⚡ 0 FPS</span>
                    <span id="timestamp">⏱️ --:--:--</span>
                    <span id="deviceInfo">🖥️ GPU</span>
                </div>
            </div>
            <div class="sidebar">
                <div class="card">
                    <h3>📊 Live Statistics</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="value" id="totalFrames">0</div>
                            <div class="label">Total Frames</div>
                        </div>
                        <div class="stat-item">
                            <div class="value" id="totalPeople">0</div>
                            <div class="label">👤 People</div>
                        </div>
                        <div class="stat-item">
                            <div class="value" id="totalVehicles">0</div>
                            <div class="label">🚗 Vehicles</div>
                        </div>
                        <div class="stat-item">
                            <div class="value" id="detections">0</div>
                            <div class="label">🎯 Detections</div>
                        </div>
                    </div>
                </div>
                <div class="card">
                    <h3>🚨 Alerts</h3>
                    <div class="alerts-container" id="alertsList">
                        <div style="color:#667788;text-align:center;padding:20px;font-size:13px;">No alerts</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        
        socket.on('stats_update', function(data) {
            document.getElementById('totalFrames').textContent = data.total_frames;
            document.getElementById('totalPeople').textContent = data.total_people;
            document.getElementById('totalVehicles').textContent = data.total_vehicles;
            document.getElementById('detections').textContent = data.detections || 0;
            document.getElementById('fps').textContent = '⚡ ' + (data.fps || 0) + ' FPS';
            document.getElementById('timestamp').textContent = '⏱️ ' + data.timestamp;
            if (data.device) {
                document.getElementById('deviceInfo').textContent = '🖥️ ' + data.device;
            }
        });
        
        socket.on('new_alert', function(data) {
            var alertsList = document.getElementById('alertsList');
            var alertDiv = document.createElement('div');
            alertDiv.className = 'alert-item';
            alertDiv.textContent = '🚨 ' + data.message;
            alertsList.insertBefore(alertDiv, alertsList.firstChild);
            if (alertsList.children.length > 20) {
                alertsList.removeChild(alertsList.lastChild);
            }
        });
    </script>
</body>
</html>'''

with open('templates/gpu_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🛡️ IBVAP - GPU Accelerated Dashboard")
    print("=" * 70)
    print(f"🌐 Dashboard: http://localhost:5000")
    print(f"🤖 GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
    print(f"📹 Video: {VIDEO_PATH}")
    print("=" * 70)
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        processing = False
        print("\n🛑 Shutting down...")
