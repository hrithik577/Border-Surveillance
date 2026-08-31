import cv2
import torch
import numpy as np
from ultralytics import YOLO
from flask import Flask, Response, render_template, jsonify
from flask_socketio import SocketIO, emit
import time
from datetime import datetime
import threading
import os
from collections import deque
import json
import random

# ============================================================
# CONFIGURATION - TWO CAMERAS
# ============================================================

def resolve_path(candidates, default=""):
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return default

video1_path = resolve_path([
    "C:/IBVAP-Demo/data/videos/VIRAT_S_000001.mp4",
    "C:/Users/bhrit/Downloads/VIRAT_S_000001.mp4",
    "data/videos/VIRAT_S_000001.mp4",
    "VIRAT_S_000001.mp4"
], "VIRAT_S_000001.mp4")

video2_path = resolve_path([
    "C:/Users/bhrit/Downloads/09152008flight2tape1_1.mpg",
    video1_path
], video1_path)

model_path = resolve_path([
    "yolov8n.pt",
    "models/yolov8n.pt",
    "data/models/yolov8n.pt",
    "C:/IBVAP-Demo/models/yolov8n.pt"
], "yolov8n.pt")

CAMERAS = {
    'camera1': {
        'name': 'Border Camera 1',
        'path': video1_path,
        'fence_y': 540,
        'color': '#00d4ff',
        'active': True
    },
    'camera2': {
        'name': 'Border Camera 2',
        'path': video2_path,
        'fence_y': 360,
        'color': '#ff6b6b',
        'active': True
    }
}

MODEL_PATH = model_path
HISTORY_LENGTH = 200


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ============================================================
# GLOBAL STATE
# ============================================================

alert_log = deque(maxlen=HISTORY_LENGTH)
detections = {cam: [] for cam in CAMERAS}
stats = {cam: {
    'total_frames': 0,
    'total_people': 0,
    'total_vehicles': 0,
    'total_alerts': 0,
    'fps': 0,
    'timestamp': '',
    'people_per_frame': 0,
    'vehicles_per_frame': 0,
    'status': 'Disconnected'
} for cam in CAMERAS}

stats_history = deque(maxlen=300)
processing = True
start_time = time.time()

# ============================================================
# LOAD YOLO MODEL
# ============================================================

print("=" * 70)
print("🛡️ IBVAP - Dual Camera Smart AI Surveillance")
print("=" * 70)
print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
model.to('cuda')
print(f"✅ Model loaded on GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
print("=" * 70)
print("📹 Camera Configuration:")
for cam_id, cam in CAMERAS.items():
    print(f"  {cam['name']}: {cam['path']}")
    print(f"    → Fence Y: {cam['fence_y']}")
print("=" * 70)

# ============================================================
# PROCESS FRAME FUNCTION
# ============================================================

def process_frame(frame, cam_id):
    """Process frame for a specific camera"""
    global stats, alert_log
    
    cam = CAMERAS[cam_id]
    results = model.track(frame, persist=True, verbose=False)
    annotated = results[0].plot()
    
    people_count = 0
    vehicle_count = 0
    current_detections = []
    intrusion_alerts = []
    
    if hasattr(results[0], 'boxes') and results[0].boxes is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()
        track_ids = results[0].boxes.id.cpu().numpy() if results[0].boxes.id is not None else None
        
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)
            class_name = model.names[int(classes[i])]
            confidence = float(confidences[i])
            track_id = int(track_ids[i]) if track_ids is not None else i
            
            if class_name == 'person':
                people_count += 1
            elif class_name in ['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'airplane', 'helicopter']:
                vehicle_count += 1
            
            current_detections.append({
                'class': class_name,
                'confidence': confidence,
                'track_id': track_id
            })
            
            # Virtual fence intrusion detection and bright green bounding box
            center_y = (y1 + y2) // 2
            fence_y = cam['fence_y']
            is_intrusion = abs(center_y - fence_y) < 30
            color = (0, 0, 255) if is_intrusion else (0, 255, 0)
            
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            if is_intrusion:
                alert_msg = f"🚨 INTRUSION: {class_name} (ID: {track_id}) on {cam['name']} at {datetime.now().strftime('%H:%M:%S')}"
                alert_log.append(alert_msg)
                stats[cam_id]['total_alerts'] += 1
                intrusion_alerts.append(alert_msg)
                print(f"[{cam['name']}] {alert_msg}")
                
                cv2.putText(annotated, f"🚨 INTRUSION! {class_name}", (x1, max(15, y1-10)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(annotated, f"{class_name.upper()} ID:{track_id} {int(confidence*100)}%", (x1, max(15, y1-10)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Update stats
    stats[cam_id]['total_frames'] += 1
    stats[cam_id]['total_people'] += people_count
    stats[cam_id]['total_vehicles'] += vehicle_count
    stats[cam_id]['people_per_frame'] = people_count
    stats[cam_id]['vehicles_per_frame'] = vehicle_count
    stats[cam_id]['timestamp'] = datetime.now().strftime('%H:%M:%S')
    stats[cam_id]['status'] = 'Active'
    
    # Draw virtual fence with camera label
    cv2.line(annotated, (0, cam['fence_y']), (1920, cam['fence_y']), 
             (0, 0, 255) if cam_id == 'camera1' else (255, 0, 0), 3)
    cv2.putText(annotated, f"🔴 {cam['name']} - VIRTUAL FENCE", (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255) if cam_id == 'camera1' else (255, 0, 0), 2)
    
    cv2.putText(annotated, f"👤 People: {people_count} | 🚗 Vehicles: {vehicle_count}", (10, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Store detections
    detections[cam_id].append({
        'timestamp': stats[cam_id]['timestamp'],
        'people': people_count,
        'vehicles': vehicle_count,
        'detections': current_detections
    })
    if len(detections[cam_id]) > HISTORY_LENGTH:
        detections[cam_id].pop(0)
    
    # Store history for charts
    stats_history.append({
        'timestamp': stats[cam_id]['timestamp'],
        'camera': cam['name'],
        'people': people_count,
        'vehicles': vehicle_count,
        'total_alerts': len(alert_log)
    })
    
    # Emit updates
    socketio.emit('stats_update', {
        'camera': cam_id,
        'camera_name': cam['name'],
        'total_frames': stats[cam_id]['total_frames'],
        'total_people': stats[cam_id]['total_people'],
        'total_vehicles': stats[cam_id]['total_vehicles'],
        'total_alerts': stats[cam_id]['total_alerts'],
        'fps': stats[cam_id]['fps'],
        'timestamp': stats[cam_id]['timestamp'],
        'people_per_frame': people_count,
        'vehicles_per_frame': vehicle_count,
        'status': 'Active',
        'uptime': int(time.time() - start_time)
    })
    
    # Send individual alerts
    for alert in intrusion_alerts:
        socketio.emit('new_alert', {
            'message': alert,
            'camera': cam['name'],
            'timestamp': stats[cam_id]['timestamp']
        })
    
    return annotated

# ============================================================
# VIDEO GENERATOR FOR EACH CAMERA
# ============================================================

def video_generator(cam_id):
    """Generate video frames from camera source"""
    global stats
    
    cam = CAMERAS[cam_id]
    cap = cv2.VideoCapture(cam['path'])
    
    if not cap.isOpened():
        print(f"❌ Could not open video: {cam['path']}")
        stats[cam_id]['status'] = 'Error'
        return
    
    print(f"✅ {cam['name']} connected: {cam['path']}")
    stats[cam_id]['status'] = 'Active'
    
    fps_start = time.time()
    fps_count = 0
    frame_delay = 1/30
    
    while processing:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        # Resize for consistency
        frame = cv2.resize(frame, (1280, 720))
        annotated = process_frame(frame, cam_id)
        
        # High quality JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 92]
        ret, jpeg = cv2.imencode('.jpg', annotated, encode_param)
        if not ret:
            continue
        
        fps_count += 1
        if time.time() - fps_start >= 1:
            stats[cam_id]['fps'] = fps_count
            fps_count = 0
            fps_start = time.time()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + 
               jpeg.tobytes() + b'\r\n')
        
        time.sleep(frame_delay)
    
    cap.release()

# ============================================================
# FLASK ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template('dashboard.html', cameras=CAMERAS)

@app.route('/video_feed/<cam_id>')
def video_feed(cam_id):
    if cam_id not in CAMERAS:
        return "Camera not found", 404
    return Response(video_generator(cam_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'cameras': {cam_id: stats[cam_id] for cam_id in CAMERAS},
        'alerts': list(alert_log),
        'detections': {cam_id: detections[cam_id][-10:] for cam_id in CAMERAS},
        'history': list(stats_history)[-100:],
        'uptime': int(time.time() - start_time),
        'total_alerts': len(alert_log)
    })

@app.route('/api/alerts')
def get_alerts():
    return jsonify({'alerts': list(alert_log)})

# ============================================================
# CREATE TEMPLATES FOLDER AND HTML
# ============================================================

os.makedirs('templates', exist_ok=True)

html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IBVAP - Dual Camera Smart AI Surveillance</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        
        /* Header */
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
        .header h1 small {
            font-size: 14px;
            color: #667788;
            -webkit-text-fill-color: #667788;
        }
        .header-right {
            display: flex;
            align-items: center;
            gap: 20px;
        }
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
        .status-text { color: #00ff88; font-size: 14px; margin-left: 8px; }
        .uptime { color: #8899aa; font-size: 13px; }
        
        /* Camera Grid */
        .camera-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }
        .video-container {
            background: #0d1520;
            border-radius: 12px;
            border: 1px solid #1a2a3a;
            overflow: hidden;
            position: relative;
        }
        .video-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        .video-overlay {
            position: absolute;
            top: 15px; left: 15px;
            display: flex;
            gap: 15px;
            font-size: 11px;
            background: rgba(0,0,0,0.8);
            padding: 6px 12px;
            border-radius: 8px;
            border: 1px solid #2a3a4a;
            flex-wrap: wrap;
        }
        .video-overlay .cam-name { color: #00d4ff; font-weight: bold; }
        .video-overlay .cam-status { color: #00ff88; }
        .video-overlay .cam-fps { color: #ffd93d; }
        .video-overlay .cam-stats { color: #ffffff; }
        
        /* Stats Bar */
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }
        .stat-item {
            background: #0d1520;
            padding: 12px 15px;
            border-radius: 10px;
            border: 1px solid #1a2a3a;
            text-align: center;
        }
        .stat-item .value {
            font-size: 22px;
            font-weight: bold;
            background: linear-gradient(90deg, #00d4ff, #7b2ffc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-item .label { font-size: 11px; color: #8899aa; margin-top: 2px; }
        .stat-item .sub { font-size: 10px; color: #667788; }
        
        /* Bottom Section */
        .bottom-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 15px;
        }
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
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .card h3 span { color: #667788; font-size: 11px; }
        
        .chart-container {
            position: relative;
            height: 100px;
        }
        
        /* Alerts */
        .alerts-container {
            max-height: 200px;
            overflow-y: auto;
        }
        .alert-item {
            padding: 6px 10px;
            margin: 3px 0;
            border-radius: 6px;
            background: #1a2332;
            border-left: 3px solid #ff0044;
            font-size: 12px;
            color: #ccddee;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .alert-item .time { color: #667788; font-size: 10px; }
        .alert-item .cam { color: #00d4ff; font-weight: bold; }
        .alert-item.warning { border-left-color: #ffaa00; }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #0d1520; }
        ::-webkit-scrollbar-thumb { background: #2a3a4a; border-radius: 4px; }
        
        /* Responsive */
        @media (max-width: 1200px) {
            .camera-grid { grid-template-columns: 1fr; }
            .bottom-grid { grid-template-columns: 1fr; }
            .stats-bar { grid-template-columns: repeat(2, 1fr); }
        }
        .badge {
            background: #1a2332;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 10px;
            color: #8899aa;
        }
        .badge.danger { color: #ff0044; border: 1px solid #ff0044; }
        .badge.success { color: #00ff88; border: 1px solid #00ff88; }
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Header -->
        <div class="header">
            <h1>🛡️ IBVAP <small>Dual Camera Smart AI Surveillance</small></h1>
            <div class="header-right">
                <span class="badge success" id="uptime">⏱️ Uptime: 0s</span>
                <span class="badge" id="totalAlertsBadge">🚨 Alerts: 0</span>
                <span class="status-dot"></span>
                <span class="status-text">LIVE</span>
            </div>
        </div>
        
        <!-- Camera Grid -->
        <div class="camera-grid">
            {% if cameras is defined and cameras %}
            {% for cam_id, cam in cameras.items() %}
            <div class="video-container">
                <img src="{{ url_for('video_feed', cam_id=cam_id) }}" alt="{{ cam.name }}">
                <div class="video-overlay">
                    <span class="cam-name">{{ cam.name }}</span>
                    <span class="cam-status" id="status_{{ cam_id }}">🟢 LIVE</span>
                    <span class="cam-fps" id="fps_{{ cam_id }}">⚡ -- FPS</span>
                    <span class="cam-stats" id="stats_{{ cam_id }}">👤 0 🚗 0</span>
                </div>
            </div>
            {% endfor %}
            {% else %}
            <div class="video-container">
                <img src="{{ url_for('video_feed') }}" alt="Live Feed">
                <div class="video-overlay">
                    <span class="cam-name">Border Camera</span>
                    <span class="cam-status" id="status_camera1">🟢 LIVE</span>
                    <span class="cam-fps" id="fps_camera1">⚡ -- FPS</span>
                    <span class="cam-stats" id="stats_camera1">👤 0 🚗 0</span>
                </div>
            </div>
            {% endif %}
        </div>

        
        <!-- Stats Bar -->
        <div class="stats-bar">
            <div class="stat-item">
                <div class="value" id="totalFrames">0</div>
                <div class="label">Total Frames</div>
            </div>
            <div class="stat-item">
                <div class="value" id="totalPeople">0</div>
                <div class="label">👤 Total People</div>
            </div>
            <div class="stat-item">
                <div class="value" id="totalVehicles">0</div>
                <div class="label">🚗 Total Vehicles</div>
            </div>
            <div class="stat-item">
                <div class="value" id="totalAlerts">0</div>
                <div class="label">🚨 Total Alerts</div>
                <div class="sub" id="alertRate">--</div>
            </div>
        </div>
        
        <!-- Bottom Grid -->
        <div class="bottom-grid">
            <!-- Chart -->
            <div class="card">
                <h3>📈 Activity Chart <span>Real-time</span></h3>
                <div class="chart-container">
                    <canvas id="activityChart"></canvas>
                </div>
            </div>
            
            <!-- Alerts -->
            <div class="card">
                <h3>🚨 Live Alerts <span id="alertCount">0</span></h3>
                <div class="alerts-container" id="alertsList">
                    <div style="color:#667788;text-align:center;padding:20px;font-size:13px;">No alerts detected</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Chart
        const ctx = document.getElementById('activityChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'People',
                        data: [],
                        borderColor: '#00d4ff',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        borderWidth: 2
                    },
                    {
                        label: 'Vehicles',
                        data: [],
                        borderColor: '#ff6b6b',
                        backgroundColor: 'rgba(255, 107, 107, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#8899aa', font: { size: 9 }, boxWidth: 10, padding: 5 }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#667788', font: { size: 8 }, maxTicksLimit: 10 },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    },
                    y: {
                        ticks: { color: '#667788', font: { size: 8 }, stepSize: 1 },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        beginAtZero: true
                    }
                },
                animation: { duration: 300 }
            }
        });

        // Socket
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        var totalStats = { frames: 0, people: 0, vehicles: 0, alerts: 0 };
        
        socket.on('stats_update', function(data) {
            // Update per-camera overlays
            document.getElementById('fps_' + data.camera).textContent = '⚡ ' + data.fps + ' FPS';
            document.getElementById('stats_' + data.camera).textContent = '👤 ' + data.people_per_frame + ' 🚗 ' + data.vehicles_per_frame;
            
            // Update total stats
            totalStats.frames += data.total_frames;
            totalStats.people += data.total_people;
            totalStats.vehicles += data.total_vehicles;
            totalStats.alerts += data.total_alerts;
            
            document.getElementById('totalFrames').textContent = totalStats.frames;
            document.getElementById('totalPeople').textContent = totalStats.people;
            document.getElementById('totalVehicles').textContent = totalStats.vehicles;
            document.getElementById('totalAlerts').textContent = totalStats.alerts;
            document.getElementById('totalAlertsBadge').textContent = '🚨 Alerts: ' + totalStats.alerts;
            document.getElementById('alertCount').textContent = totalStats.alerts;
            document.getElementById('uptime').textContent = '⏱️ Uptime: ' + formatUptime(data.uptime);
            
            // Update chart
            if (chart.data.labels.length > 60) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
                chart.data.datasets[1].data.shift();
            }
            chart.data.labels.push(data.timestamp);
            chart.data.datasets[0].data.push(data.people_per_frame);
            chart.data.datasets[1].data.push(data.vehicles_per_frame);
            chart.update('none');
        });
        
        socket.on('new_alert', function(data) {
            var alertsList = document.getElementById('alertsList');
            var alertDiv = document.createElement('div');
            alertDiv.className = 'alert-item warning';
            alertDiv.innerHTML = '<span class="cam">[' + data.camera + ']</span> ' + data.message + ' <span class="time">' + data.timestamp + '</span>';
            alertsList.insertBefore(alertDiv, alertsList.firstChild);
            if (alertsList.children.length > 30) {
                alertsList.removeChild(alertsList.lastChild);
            }
            // Update alert count
            document.getElementById('alertCount').textContent = document.querySelectorAll('#alertsList .alert-item').length;
        });

        function formatUptime(seconds) {
            var mins = Math.floor(seconds / 60);
            var secs = seconds % 60;
            if (mins > 60) {
                var hrs = Math.floor(mins / 60);
                mins = mins % 60;
                return hrs + 'h ' + mins + 'm ' + secs + 's';
            }
            return mins + 'm ' + secs + 's';
        }

        // Initial load
        fetch('/api/alerts')
            .then(response => response.json())
            .then(data => {
                var alertsList = document.getElementById('alertsList');
                alertsList.innerHTML = '';
                data.alerts.slice(-20).reverse().forEach(function(alert) {
                    var alertDiv = document.createElement('div');
                    alertDiv.className = 'alert-item warning';
                    alertDiv.innerHTML = alert;
                    alertsList.appendChild(alertDiv);
                });
                if (data.alerts.length === 0) {
                    alertsList.innerHTML = '<div style="color:#667788;text-align:center;padding:20px;font-size:13px;">No alerts detected</div>';
                }
                document.getElementById('alertCount').textContent = data.alerts.length;
            });
        
        // Fetch history
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                data.history.forEach(function(item) {
                    chart.data.labels.push(item.timestamp);
                    chart.data.datasets[0].data.push(item.people);
                    chart.data.datasets[1].data.push(item.vehicles);
                });
                chart.update('none');
            });
    </script>
</body>
</html>'''

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

# ============================================================
# RUN THE APPLICATION
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🛡️ IBVAP - Dual Camera Smart AI Surveillance")
    print("=" * 70)
    print(f"🌐 Dashboard URL: http://localhost:5000")
    print("=" * 70)
    print("📹 Camera 1: Border Camera 1 (VIRAT_S_000001.mp4)")
    print("📹 Camera 2: Border Camera 2 (09152008flight2tape1_1.mpg)")
    print("=" * 70)
    print("🔴 Press Ctrl+C to stop")
    print("=" * 70)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        processing = False
        print("\n🛑 Shutting down...")
