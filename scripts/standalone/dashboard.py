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

def resolve_path(candidates, default=""):
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return default

# Configuration
VIDEO_PATH = resolve_path([
    "C:/IBVAP-Demo/data/videos/VIRAT_S_000001.mp4",
    "C:/Users/bhrit/Downloads/VIRAT_S_000001.mp4",
    "data/videos/VIRAT_S_000001.mp4",
    "VIRAT_S_000001.mp4"
], "VIRAT_S_000001.mp4")

MODEL_PATH = resolve_path([
    "yolov8n.pt",
    "models/yolov8n.pt",
    "data/models/yolov8n.pt",
    "C:/IBVAP-Demo/models/yolov8n.pt"
], "yolov8n.pt")

HISTORY_LENGTH = 200


# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
detections = []
alerts = deque(maxlen=HISTORY_LENGTH)
stats_history = deque(maxlen=300)  # For charts
stats = {
    'total_frames': 0,
    'total_people': 0,
    'total_vehicles': 0,
    'total_alerts': 0,
    'fps': 0,
    'timestamp': '',
    'people_per_frame': 0,
    'vehicles_per_frame': 0
}
current_frame = None
lock = threading.Lock()
processing = True
start_time = time.time()

# Load model
print("=" * 60)
print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
model.to('cuda')
print(f"Model loaded on GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
print(f"Video source: {VIDEO_PATH}")
print("=" * 60)

def process_frame(frame):
    """Process frame with YOLO detection and tracking"""
    global stats, alerts, stats_history
    
    results = model.track(frame, persist=True, verbose=False)
    annotated = results[0].plot()
    
    people_count = 0
    vehicle_count = 0
    current_detections = []
    
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
            elif class_name in ['car', 'truck', 'bus', 'motorcycle', 'bicycle']:
                vehicle_count += 1
            
            current_detections.append({
                'class': class_name,
                'confidence': confidence,
                'track_id': track_id
            })
            
            # Virtual fence intrusion
            center_y = (y1 + y2) // 2
            fence_y = 540
            if abs(center_y - fence_y) < 30:
                alert_msg = f"🚨 INTRUSION: {class_name} (ID: {track_id}) at {datetime.now().strftime('%H:%M:%S')}"
                alerts.append(alert_msg)
                stats['total_alerts'] += 1
                print(alert_msg)
                
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(annotated, "🚨 INTRUSION!", (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                socketio.emit('new_alert', {'message': alert_msg, 'timestamp': stats['timestamp']})
    
    stats['total_frames'] += 1
    stats['total_people'] += people_count
    stats['total_vehicles'] += vehicle_count
    stats['people_per_frame'] = people_count
    stats['vehicles_per_frame'] = vehicle_count
    stats['timestamp'] = datetime.now().strftime('%H:%M:%S')
    
    # Store history for charts
    stats_history.append({
        'timestamp': stats['timestamp'],
        'people': people_count,
        'vehicles': vehicle_count,
        'alerts': len(alerts),
        'fps': stats['fps']
    })
    
    # Draw virtual fence
    cv2.line(annotated, (0, 540), (1920, 540), (0, 0, 255), 3)
    cv2.putText(annotated, "🔴 VIRTUAL FENCE", (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    cv2.putText(annotated, f"👤 People: {people_count} | 🚗 Vehicles: {vehicle_count}", (10, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Detection count badge
    cv2.putText(annotated, f"Detections: {len(current_detections)}", (10, 110), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    detections.append({
        'timestamp': stats['timestamp'],
        'people': people_count,
        'vehicles': vehicle_count,
        'detections': current_detections
    })
    if len(detections) > HISTORY_LENGTH:
        detections.pop(0)
    
    socketio.emit('stats_update', {
        'total_frames': stats['total_frames'],
        'total_people': stats['total_people'],
        'total_vehicles': stats['total_vehicles'],
        'total_alerts': stats['total_alerts'],
        'fps': stats['fps'],
        'timestamp': stats['timestamp'],
        'people_per_frame': people_count,
        'vehicles_per_frame': vehicle_count,
        'uptime': int(time.time() - start_time)
    })
    
    return annotated

def video_generator():
    """Generate video frames with high quality"""
    global current_frame, stats
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    if not cap.isOpened():
        print(f"ERROR: Could not open video file: {VIDEO_PATH}")
        return
    
    print(f"Connected to video file: {VIDEO_PATH}")
    
    fps_start = time.time()
    fps_count = 0
    frame_delay = 1/30
    
    while processing:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        with lock:
            annotated = process_frame(frame)
            current_frame = annotated
        
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        ret, jpeg = cv2.imencode('.jpg', annotated, encode_param)
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

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_generator(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'stats': stats,
        'alerts': list(alerts),
        'detections': detections[-10:],
        'history': list(stats_history)[-100:],
        'uptime': int(time.time() - start_time)
    })

@app.route('/api/alerts')
def get_alerts():
    return jsonify({'alerts': list(alerts)})

@app.route('/api/detections')
def get_detections():
    return jsonify({'detections': detections[-20:]})

@app.route('/api/history')
def get_history():
    return jsonify({'history': list(stats_history)[-100:]})

# Create templates folder
os.makedirs('templates', exist_ok=True)

# Create advanced HTML template with charts
html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IBVAP - Advanced Border Surveillance</title>
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
            font-size: 26px;
            background: linear-gradient(90deg, #00d4ff, #7b2ffc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
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
        
        /* Main Grid */
        .grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 15px;
        }
        
        /* Video */
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
            gap: 20px;
            font-size: 12px;
            background: rgba(0,0,0,0.8);
            padding: 8px 15px;
            border-radius: 8px;
            border: 1px solid #2a3a4a;
        }
        .video-overlay span { color: #00d4ff; }
        
        /* Sidebar */
        .sidebar { display: flex; flex-direction: column; gap: 15px; }
        .card {
            background: #0d1520;
            border-radius: 12px;
            padding: 18px;
            border: 1px solid #1a2a3a;
        }
        .card h3 {
            color: #00d4ff;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .card h3 span { color: #667788; font-size: 11px; }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .stat-item {
            background: #1a2332;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid transparent;
            transition: all 0.3s;
        }
        .stat-item:hover { border-color: #2a3a4a; }
        .stat-item .value {
            font-size: 26px;
            font-weight: bold;
            background: linear-gradient(90deg, #00d4ff, #7b2ffc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-item .label { font-size: 11px; color: #8899aa; margin-top: 3px; }
        .stat-item .change {
            font-size: 10px;
            margin-top: 2px;
            color: #00ff88;
        }
        
        /* Alerts */
        .alerts-container {
            max-height: 150px;
            overflow-y: auto;
        }
        .alert-item {
            padding: 8px 12px;
            margin: 4px 0;
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
        .alert-item.warning { border-left-color: #ffaa00; }
        
        /* Detections */
        .detection-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 10px;
            margin: 3px 0;
            background: #1a2332;
            border-radius: 4px;
            font-size: 12px;
        }
        .detection-item .class { color: #00d4ff; }
        .detection-item .conf { color: #88dd88; }
        .detection-item .id { color: #667788; font-size: 10px; }
        
        /* Chart container */
        .chart-container {
            position: relative;
            height: 80px;
            margin-top: 5px;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #0d1520; }
        ::-webkit-scrollbar-thumb { background: #2a3a4a; border-radius: 4px; }
        
        /* Responsive */
        @media (max-width: 1200px) { .grid { grid-template-columns: 1fr; } }
        
        .badge {
            background: #1a2332;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            color: #8899aa;
        }
        .badge.danger { color: #ff0044; border: 1px solid #ff0044; }
        .badge.success { color: #00ff88; border: 1px solid #00ff88; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🛡️ IBVAP - Border Surveillance</h1>
            <div class="header-right">
                <span class="badge success" id="uptime">Uptime: 0s</span>
                <span class="status-dot"></span>
                <span class="status-text">LIVE</span>
            </div>
        </div>
        
        <div class="grid">
            <!-- Video -->
            <div class="video-container">
                <img src="{{ url_for('video_feed') }}" alt="Live Feed">
                <div class="video-overlay">
                    <span>📹 LIVE</span>
                    <span id="fps">⚡ -- FPS</span>
                    <span id="timestamp">⏱️ --:--:--</span>
                </div>
            </div>
            
            <!-- Sidebar -->
            <div class="sidebar">
                <!-- Stats -->
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
                            <div class="value" id="totalAlerts">0</div>
                            <div class="label">🚨 Alerts</div>
                            <div class="change" id="alertRate">--</div>
                        </div>
                    </div>
                </div>
                
                <!-- Chart -->
                <div class="card">
                    <h3>📈 Activity Chart <span>Last 60s</span></h3>
                    <div class="chart-container">
                        <canvas id="activityChart"></canvas>
                    </div>
                </div>
                
                <!-- Alerts -->
                <div class="card">
                    <h3>🚨 Recent Alerts <span id="alertCount">0</span></h3>
                    <div class="alerts-container" id="alertsList">
                        <div style="color:#667788;text-align:center;padding:20px;font-size:13px;">No alerts detected</div>
                    </div>
                </div>
                
                <!-- Detections -->
                <div class="card">
                    <h3>🎯 Current Detections <span id="detectionCount">0</span></h3>
                    <div class="alerts-container" id="detectionsList" style="max-height:120px;">
                        <div style="color:#667788;text-align:center;padding:20px;font-size:13px;">No detections</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Chart setup
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
                        borderColor: '#7b2ffc',
                        backgroundColor: 'rgba(123, 47, 252, 0.1)',
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
                        labels: {
                            color: '#8899aa',
                            font: { size: 9 },
                            boxWidth: 10,
                            padding: 5
                        }
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

        // Socket connection
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        
        socket.on('stats_update', function(data) {
            document.getElementById('totalFrames').textContent = data.total_frames;
            document.getElementById('totalPeople').textContent = data.total_people;
            document.getElementById('totalVehicles').textContent = data.total_vehicles;
            document.getElementById('totalAlerts').textContent = data.total_alerts;
            document.getElementById('fps').textContent = '⚡ ' + data.fps + ' FPS';
            document.getElementById('timestamp').textContent = '⏱️ ' + data.timestamp;
            document.getElementById('uptime').textContent = '⏱️ ' + formatUptime(data.uptime);
            document.getElementById('alertCount').textContent = data.total_alerts;
            
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
            alertDiv.innerHTML = '<strong>🚨</strong> ' + data.message + ' <span class="time">' + data.timestamp + '</span>';
            alertsList.insertBefore(alertDiv, alertsList.firstChild);
            if (alertsList.children.length > 20) {
                alertsList.removeChild(alertsList.lastChild);
            }
        });

        function formatUptime(seconds) {
            var mins = Math.floor(seconds / 60);
            var secs = seconds % 60;
            return mins + 'm ' + secs + 's';
        }

        // Initial load
        fetch('/api/alerts')
            .then(response => response.json())
            .then(data => {
                var alertsList = document.getElementById('alertsList');
                alertsList.innerHTML = '';
                data.alerts.forEach(function(alert) {
                    var alertDiv = document.createElement('div');
                    alertDiv.className = 'alert-item warning';
                    alertDiv.innerHTML = alert;
                    alertsList.appendChild(alertDiv);
                });
                if (data.alerts.length === 0) {
                    alertsList.innerHTML = '<div style="color:#667788;text-align:center;padding:20px;font-size:13px;">No alerts detected</div>';
                }
            });
        
        setInterval(function() {
            fetch('/api/detections')
                .then(response => response.json())
                .then(data => {
                    var list = document.getElementById('detectionsList');
                    list.innerHTML = '';
                    var dets = data.detections.slice(-5).reverse();
                    var hasDetections = false;
                    var count = 0;
                    dets.forEach(function(frame) {
                        frame.detections.forEach(function(det) {
                            hasDetections = true;
                            count++;
                            var div = document.createElement('div');
                            div.className = 'detection-item';
                            div.innerHTML = '<span class="class">' + det.class + '</span>' +
                                          '<span><span class="conf">' + (det.confidence * 100).toFixed(0) + '%</span> <span class="id">#' + det.track_id + '</span></span>';
                            list.appendChild(div);
                        });
                    });
                    document.getElementById('detectionCount').textContent = count;
                    if (!hasDetections) {
                        list.innerHTML = '<div style="color:#667788;text-align:center;padding:20px;font-size:13px;">No detections</div>';
                        document.getElementById('detectionCount').textContent = '0';
                    }
                });
        }, 1000);

        // Fetch history for chart
        fetch('/api/history')
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

if __name__ == '__main__':
    print("=" * 60)
    print("🛡️ IBVAP Advanced Dashboard Starting...")
    print("=" * 60)
    print(f"🌐 Dashboard URL: http://localhost:5000")
    print(f"📹 Video Source: {VIDEO_PATH}")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        processing = False
        print("\nShutting down...")
