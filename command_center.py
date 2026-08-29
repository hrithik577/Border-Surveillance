# ============================================================
# IBVAP - COMMAND CENTER DASHBOARD
# Full implementation of the master UI prompt
# ============================================================

import os
import cv2
import torch
import numpy as np
from ultralytics import YOLO
from flask import Flask, Response, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import time
import threading
from collections import deque
import json
import random
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION
# ============================================================

VIDEO_PATH = r"C:\Users\bhrit\Downloads\vidssave.com Top View Pedestrian Dataset Sample 1 720P.mp4"
MODEL_PATH = "C:/IBVAP-Demo/data/models/yolov8n.pt"

# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ============================================================
# CHECK GPU
# ============================================================

print("=" * 70)
print("🛡️ IBVAP - COMMAND CENTER")
print("=" * 70)

if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    device = 'cuda'
else:
    device = 'cpu'
print(f"Using device: {device.upper()}")

# ============================================================
# LOAD YOLO MODEL
# ============================================================

print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
model.to(device)
print(f"✅ YOLO loaded on {device.upper()}")

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
    'detections': 0,
    'system_uptime': 0,
    'gpu_util': 0,
    'confidence': 94.8,
    'cameras_online': 247,
    'cameras_offline': 8,
    'anpr_matches': 17,
    'intrusions': 6,
    'critical_alerts': 4
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
    
    print(f"✅ Video loaded")
    
    fps_start = time.time()
    fps_count = 0
    frame_count = 0
    
    while processing:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        frame = cv2.resize(frame, (1280, 720))
        frame_count += 1
        
        try:
            results = model(frame, conf=0.25, verbose=False)
            annotated = results[0].plot()
            
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
            
            stats['total_frames'] += 1
            stats['total_people'] += people_count
            stats['total_vehicles'] += vehicle_count
            stats['detections'] = det_count
            stats['timestamp'] = datetime.now().strftime('%H:%M:%S')
            stats['system_uptime'] = int(time.time() - start_time)
            
            # Generate random alerts for demo
            if frame_count % 50 == 0 and det_count > 0:
                alert_types = ['Human detected', 'Vehicle detected', 'Virtual fence breach', 
                              'ANPR match', 'Night movement detected', 'Suspicious loitering']
                alert = random.choice(alert_types)
                severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
                severity = random.choice(severities)
                
                alert_msg = f"[{severity}] {alert}"
                alerts.append(alert_msg)
                stats['total_alerts'] += 1
                if severity == 'CRITICAL':
                    stats['critical_alerts'] += 1
                socketio.emit('new_alert', {'message': alert_msg, 'severity': severity})
            
            # Emit stats
            socketio.emit('stats_update', {
                'total_frames': stats['total_frames'],
                'total_people': stats['total_people'],
                'total_vehicles': stats['total_vehicles'],
                'total_alerts': stats['total_alerts'],
                'fps': stats['fps'],
                'timestamp': stats['timestamp'],
                'device': device.upper(),
                'detections': det_count,
                'system_uptime': stats['system_uptime'],
                'gpu_util': random.randint(65, 85),
                'confidence': 94.8 + random.uniform(-1, 1),
                'cameras_online': 247 - random.randint(0, 5),
                'cameras_offline': 8 + random.randint(0, 3),
                'anpr_matches': stats['anpr_matches'] + random.randint(0, 2),
                'intrusions': stats['intrusions'] + random.randint(0, 1),
                'critical_alerts': stats['critical_alerts']
            })
            
        except Exception as e:
            print(f"Detection error: {e}")
            annotated = frame
        
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
    
    cap.release()

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template('command_center.html')

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

# ============================================================
# CREATE HTML TEMPLATE
# ============================================================

os.makedirs('templates', exist_ok=True)

html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IBVAP - Command Center</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* ============================================================
           MASTER STYLES - IBVAP COMMAND CENTER
           ============================================================ */
        
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #0a0c12;
            --bg-secondary: #11161e;
            --bg-surface: #151d2a;
            --bg-card: #1a2332;
            --border-color: #2a3a4a;
            --border-subtle: #1a2a3a;
            --text-primary: #e8edf2;
            --text-secondary: #a0b4c8;
            --text-muted: #66788a;
            --accent-green: #00e676;
            --accent-amber: #ffd740;
            --accent-red: #ff1744;
            --accent-blue: #00b0ff;
            --accent-purple: #7c4dff;
            --font-sans: 'Inter', 'IBM Plex Sans', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }
        
        body {
            font-family: var(--font-sans);
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            padding: 12px;
        }
        
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: var(--bg-secondary); }
        ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 2px; }
        
        .dashboard { max-width: 1920px; margin: 0 auto; }
        
        /* ===== TOP COMMAND BAR ===== */
        .command-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            margin-bottom: 12px;
        }
        
        .command-bar .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .command-bar .brand .logo {
            width: 32px;
            height: 32px;
            border: 1.5px solid var(--accent-green);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 900;
            color: var(--accent-green);
            font-family: var(--font-mono);
        }
        
        .command-bar .brand .title {
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 1.5px;
            color: var(--text-primary);
        }
        
        .command-bar .brand .subtitle {
            font-size: 9px;
            color: var(--text-muted);
            letter-spacing: 1px;
            font-weight: 400;
        }
        
        .command-bar .status-center {
            display: flex;
            align-items: center;
            gap: 20px;
            font-size: 11px;
        }
        
        .command-bar .status-center .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 2s infinite;
        }
        
        .command-bar .status-center .dot.green { background: var(--accent-green); }
        .command-bar .status-center .dot.amber { background: var(--accent-amber); }
        .command-bar .status-center .dot.red { background: var(--accent-red); animation: pulse 0.5s infinite; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .command-bar .status-center .status-label {
            color: var(--accent-green);
            font-weight: 600;
            font-size: 10px;
            letter-spacing: 1px;
        }
        
        .command-bar .status-center .metric {
            color: var(--text-secondary);
            font-size: 10px;
        }
        
        .command-bar .status-center .metric .val {
            color: var(--text-primary);
            font-weight: 600;
            font-family: var(--font-mono);
        }
        
        .command-bar .status-right {
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 10px;
            color: var(--text-secondary);
        }
        
        .command-bar .status-right .secure-badge {
            background: rgba(0,230,118,0.1);
            border: 1px solid rgba(0,230,118,0.2);
            padding: 2px 10px;
            border-radius: 3px;
            color: var(--accent-green);
            font-size: 9px;
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        /* ===== LAYOUT: Sidebar + Main ===== */
        .main-layout {
            display: grid;
            grid-template-columns: 180px 1fr;
            gap: 12px;
        }
        
        /* ===== SIDEBAR ===== */
        .sidebar {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 12px 0;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: calc(100vh - 100px);
        }
        
        .sidebar .nav-items {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        
        .sidebar .nav-item {
            padding: 8px 16px;
            font-size: 11px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
            border-left: 2px solid transparent;
            font-weight: 500;
            letter-spacing: 0.3px;
        }
        
        .sidebar .nav-item:hover {
            background: rgba(255,255,255,0.03);
            color: var(--text-primary);
        }
        
        .sidebar .nav-item.active {
            color: var(--accent-green);
            border-left-color: var(--accent-green);
            background: rgba(0,230,118,0.05);
        }
        
        .sidebar .nav-item .icon { margin-right: 8px; opacity: 0.5; }
        .sidebar .nav-item.active .icon { opacity: 1; }
        
        .sidebar .nav-footer {
            padding: 12px 16px;
            border-top: 1px solid var(--border-subtle);
            font-size: 9px;
        }
        
        .sidebar .nav-footer .label { color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        .sidebar .nav-footer .value { color: var(--accent-green); font-weight: 600; }
        
        /* ===== MAIN CONTENT ===== */
        .main-content {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        /* ===== KPI ROW ===== */
        .kpi-row {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 10px;
        }
        
        .kpi-card {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            padding: 12px 14px;
            transition: all 0.2s;
        }
        
        .kpi-card:hover { border-color: var(--border-color); }
        
        .kpi-card .label {
            font-size: 9px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            font-weight: 600;
        }
        
        .kpi-card .value {
            font-size: 20px;
            font-weight: 700;
            font-family: var(--font-mono);
            margin-top: 4px;
            color: var(--text-primary);
        }
        
        .kpi-card .value .sub {
            font-size: 12px;
            font-weight: 400;
            color: var(--text-muted);
        }
        
        .kpi-card .trend {
            font-size: 9px;
            margin-top: 4px;
        }
        
        .kpi-card .trend.up { color: var(--accent-green); }
        .kpi-card .trend.down { color: var(--accent-red); }
        
        .kpi-card .mini-chart {
            margin-top: 6px;
            height: 20px;
            display: flex;
            align-items: flex-end;
            gap: 2px;
        }
        
        .kpi-card .mini-chart .bar {
            flex: 1;
            background: var(--accent-green);
            opacity: 0.3;
            border-radius: 1px;
            min-height: 2px;
            transition: height 0.5s;
        }
        
        .kpi-card .mini-chart .bar.active {
            opacity: 0.8;
        }
        
        /* ===== GRID: Video + Side Panels ===== */
        .grid-2col {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 12px;
        }
        
        /* ===== VIDEO CONTAINER ===== */
        .video-container {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }
        
        .video-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .video-container .overlay-top {
            position: absolute;
            top: 12px;
            left: 12px;
            display: flex;
            gap: 16px;
            font-size: 10px;
            font-family: var(--font-mono);
            color: var(--text-secondary);
            background: rgba(0,0,0,0.7);
            padding: 4px 12px;
            border-radius: 3px;
        }
        
        .video-container .overlay-top .val { color: var(--text-primary); }
        .video-container .overlay-top .threat { color: var(--accent-red); }
        
        /* ===== SIDE PANELS ===== */
        .side-panels {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .panel {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            padding: 12px 14px;
        }
        
        .panel .panel-title {
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 8px;
        }
        
        .panel .panel-title .highlight { color: var(--accent-green); }
        .panel .panel-title .highlight.amber { color: var(--accent-amber); }
        .panel .panel-title .highlight.red { color: var(--accent-red); }
        
        /* ===== THREAT INTELLIGENCE ===== */
        .threat-list {
            max-height: 180px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .threat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 8px;
            background: rgba(0,0,0,0.2);
            border-radius: 3px;
            font-size: 10px;
            border-left: 2px solid var(--text-muted);
        }
        
        .threat-item .severity { font-weight: 600; }
        .threat-item .severity.critical { color: var(--accent-red); }
        .threat-item .severity.high { color: var(--accent-amber); }
        .threat-item .severity.medium { color: #ffab40; }
        .threat-item .severity.low { color: var(--accent-green); }
        
        .threat-item .time { color: var(--text-muted); font-size: 9px; font-family: var(--font-mono); }
        .threat-item .action-btn {
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 1px 8px;
            border-radius: 2px;
            font-size: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .threat-item .action-btn:hover {
            background: var(--accent-green);
            color: var(--bg-primary);
            border-color: var(--accent-green);
        }
        
        /* ===== STATUS INDICATORS ===== */
        .status-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        
        .status-tag {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 10px;
            color: var(--text-secondary);
        }
        
        .status-tag .dot-sm {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
        }
        
        .status-tag .dot-sm.green { background: var(--accent-green); }
        .status-tag .dot-sm.amber { background: var(--accent-amber); }
        .status-tag .dot-sm.red { background: var(--accent-red); }
        
        /* ===== AI COPILOT ===== */
        .copilot-box {
            background: rgba(124,77,255,0.05);
            border: 1px solid rgba(124,77,255,0.2);
            border-radius: 4px;
            padding: 10px 12px;
            font-size: 12px;
            color: var(--text-secondary);
            font-style: italic;
        }
        
        .copilot-box .label {
            color: var(--accent-purple);
            font-style: normal;
            font-weight: 600;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .copilot-actions {
            display: flex;
            gap: 8px;
            margin-top: 8px;
            flex-wrap: wrap;
        }
        
        .copilot-actions .action {
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border-subtle);
            padding: 4px 12px;
            border-radius: 3px;
            font-size: 9px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .copilot-actions .action:hover {
            background: rgba(124,77,255,0.1);
            border-color: var(--accent-purple);
            color: var(--text-primary);
        }
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 1200px) {
            .kpi-row { grid-template-columns: repeat(4, 1fr); }
        }
        
        @media (max-width: 992px) {
            .main-layout { grid-template-columns: 1fr; }
            .sidebar { display: none; }
            .grid-2col { grid-template-columns: 1fr; }
        }
        
        @media (max-width: 768px) {
            .kpi-row { grid-template-columns: repeat(2, 1fr); }
            .command-bar { flex-wrap: wrap; gap: 6px; }
            .command-bar .status-center { flex-wrap: wrap; gap: 8px; }
        }
        
        /* ===== MISC ===== */
        .text-mono { font-family: var(--font-mono); }
        .text-muted { color: var(--text-muted); }
        .text-green { color: var(--accent-green); }
        .text-amber { color: var(--accent-amber); }
        .text-red { color: var(--accent-red); }
    </style>
</head>
<body>
    <div class="dashboard">
        
        <!-- ============================================================
        TOP COMMAND BAR
        ============================================================ -->
        <header class="command-bar">
            <div class="brand">
                <div class="logo">IBVAP</div>
                <div>
                    <div class="title">INTELLIGENT BORDER VIDEO ANALYTICS PLATFORM</div>
                    <div class="subtitle">AI-Powered Border Surveillance • Secure Operations</div>
                </div>
            </div>
            <div class="status-center">
                <span class="dot green"></span>
                <span class="status-label">SYSTEM OPERATIONAL</span>
                <span class="metric">Cameras <span class="val" id="camerasOnline">247</span></span>
                <span class="metric">AI <span class="val" id="aiStatus">ACTIVE</span></span>
                <span class="metric">FPS <span class="val" id="fpsMetric">0</span></span>
                <span class="metric">GPU <span class="val" id="gpuMetric">0%</span></span>
                <span class="metric" id="timeDisplay">--:--:--</span>
            </div>
            <div class="status-right">
                <span class="secure-badge">● SECURE OPERATIONS</span>
                <span>🔔</span>
                <span>⚙️</span>
                <span>👤</span>
            </div>
        </header>
        
        <!-- ============================================================
        MAIN LAYOUT
        ============================================================ -->
        <div class="main-layout">
            
            <!-- SIDEBAR -->
            <nav class="sidebar">
                <div class="nav-items">
                    <div class="nav-item active"><span class="icon">📊</span>Overview</div>
                    <div class="nav-item"><span class="icon">📹</span>Live Surveillance</div>
                    <div class="nav-item"><span class="icon">🤖</span>AI Detection</div>
                    <div class="nav-item"><span class="icon">🚨</span>Incident Center</div>
                    <div class="nav-item"><span class="icon">📋</span>ANPR</div>
                    <div class="nav-item"><span class="icon">👤</span>Face Intelligence</div>
                    <div class="nav-item"><span class="icon">🔒</span>Intrusion Detection</div>
                    <div class="nav-item"><span class="icon">🧠</span>Behaviour Analytics</div>
                    <div class="nav-item"><span class="icon">🌙</span>Night Surveillance</div>
                    <div class="nav-item"><span class="icon">📡</span>Camera Network</div>
                    <div class="nav-item"><span class="icon">🗺️</span>Geofencing</div>
                    <div class="nav-item"><span class="icon">📁</span>Evidence Vault</div>
                    <div class="nav-item"><span class="icon">📈</span>Analytics</div>
                    <div class="nav-item"><span class="icon">🖥️</span>System Health</div>
                    <div class="nav-item"><span class="icon">📜</span>Audit Logs</div>
                </div>
                <div class="nav-footer">
                    <div class="label">AI ENGINE</div>
                    <div class="value">● ONLINE</div>
                    <div style="margin-top:4px;"></div>
                    <div class="label">EDGE PROCESSING</div>
                    <div class="value">● ACTIVE</div>
                </div>
            </nav>
            
            <!-- MAIN CONTENT -->
            <main class="main-content">
                
                <!-- KPI ROW -->
                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="label">CAMERAS</div>
                        <div class="value"><span id="kpiCameras">247</span> <span class="sub">/<span id="kpiOffline">8</span> offline</span></div>
                        <div class="trend up">+12.4% vs 24h</div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">PERSONS DETECTED</div>
                        <div class="value" id="kpiPeople">0</div>
                        <div class="trend up">+8.2% vs 24h</div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">VEHICLES</div>
                        <div class="value" id="kpiVehicles">0</div>
                        <div class="trend up">+5.7% vs 24h</div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">SECURITY EVENTS</div>
                        <div class="value" id="kpiEvents">0</div>
                        <div class="trend up">+3.1% vs 24h</div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">CRITICAL ALERTS</div>
                        <div class="value" id="kpiCritical">0</div>
                        <div class="trend down">-2 from peak</div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">ANPR MATCHES</div>
                        <div class="value" id="kpiAnpr">0</div>
                        <div class="trend up">+12% vs 24h</div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">INTRUSIONS</div>
                        <div class="value" id="kpiIntrusions">0</div>
                        <div class="trend up">+2 vs 24h</div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">AI CONFIDENCE</div>
                        <div class="value" id="kpiConfidence">94.8%</div>
                        <div class="trend up">+0.3%</div>
                    </div>
                </div>
                
                <!-- GRID: Video + Side Panels -->
                <div class="grid-2col">
                    
                    <!-- VIDEO -->
                    <div class="video-container">
                        <img src="{{ url_for('video_feed') }}" alt="Live Feed">
                        <div class="overlay-top">
                            <span>📹 LIVE</span>
                            <span>FPS: <span class="val" id="fpsOverlay">0</span></span>
                            <span>🎯 <span class="val" id="detOverlay">0</span></span>
                            <span>👤 <span class="val" id="peopleOverlay">0</span></span>
                            <span>🚗 <span class="val" id="vehicleOverlay">0</span></span>
                            <span class="threat" id="threatOverlay">THREAT: LOW</span>
                        </div>
                    </div>
                    
                    <!-- SIDE PANELS -->
                    <div class="side-panels">
                        
                        <!-- THREAT INTELLIGENCE -->
                        <div class="panel">
                            <div class="panel-title">🚨 <span class="highlight red">THREAT INTELLIGENCE</span> <span style="color:var(--text-muted);font-size:9px;">REAL-TIME</span></div>
                            <div class="threat-list" id="threatList">
                                <div style="color:var(--text-muted);font-size:10px;text-align:center;padding:10px;">No threats detected</div>
                            </div>
                        </div>
                        
                        <!-- AI COPILOT -->
                        <div class="panel">
                            <div class="panel-title">🧠 <span class="highlight">AI SURVEILLANCE COPILOT</span></div>
                            <div class="copilot-box" id="copilotBox">
                                <span class="label">🤖 ANALYSIS:</span>
                                <span id="copilotText">System monitoring all sectors. No immediate threats detected.</span>
                            </div>
                            <div class="copilot-actions">
                                <span class="action">🔍 TRACK CAMERA</span>
                                <span class="action">📋 OPEN INCIDENT</span>
                                <span class="action">📡 CHECK NEARBY</span>
                                <span class="action">🚨 CREATE PATROL ALERT</span>
                            </div>
                        </div>
                        
                        <!-- STATUS INDICATORS -->
                        <div class="panel">
                            <div class="panel-title">📡 <span class="highlight">SYSTEM STATUS</span></div>
                            <div class="status-row">
                                <span class="status-tag"><span class="dot-sm green"></span> 247 Online</span>
                                <span class="status-tag"><span class="dot-sm amber"></span> 8 Offline</span>
                                <span class="status-tag"><span class="dot-sm red"></span> 4 Degraded</span>
                                <span class="status-tag">⚡ AI: <span id="aiStatusTag">ACTIVE</span></span>
                                <span class="status-tag">🖥️ GPU: <span id="gpuStatusTag">76%</span></span>
                                <span class="status-tag">⏱️ Uptime: <span id="uptimeTag">00:00:00</span></span>
                            </div>
                        </div>
                        
                    </div>
                </div>
            </main>
        </div>
    </div>
    
    <script>
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        
        socket.on('stats_update', function(data) {
            // KPI updates
            document.getElementById('kpiCameras').textContent = data.cameras_online || 247;
            document.getElementById('kpiOffline').textContent = data.cameras_offline || 8;
            document.getElementById('kpiPeople').textContent = data.total_people || 0;
            document.getElementById('kpiVehicles').textContent = data.total_vehicles || 0;
            document.getElementById('kpiEvents').textContent = data.total_alerts || 0;
            document.getElementById('kpiCritical').textContent = data.critical_alerts || 0;
            document.getElementById('kpiAnpr').textContent = data.anpr_matches || 0;
            document.getElementById('kpiIntrusions').textContent = data.intrusions || 0;
            document.getElementById('kpiConfidence').textContent = (data.confidence || 94.8).toFixed(1) + '%';
            
            // Metrics
            document.getElementById('fpsMetric').textContent = data.fps || 0;
            document.getElementById('fpsOverlay').textContent = data.fps || 0;
            document.getElementById('gpuMetric').textContent = (data.gpu_util || 0) + '%';
            document.getElementById('camerasOnline').textContent = data.cameras_online || 247;
            document.getElementById('gpuStatusTag').textContent = (data.gpu_util || 0) + '%';
            
            // Detections
            document.getElementById('detOverlay').textContent = data.detections || 0;
            document.getElementById('peopleOverlay').textContent = data.total_people || 0;
            document.getElementById('vehicleOverlay').textContent = data.total_vehicles || 0;
            
            // Time
            var date = new Date();
            document.getElementById('timeDisplay').textContent = date.toLocaleTimeString();
            
            // Uptime
            var uptime = data.system_uptime || 0;
            var hours = Math.floor(uptime / 3600);
            var minutes = Math.floor((uptime % 3600) / 60);
            var seconds = uptime % 60;
            document.getElementById('uptimeTag').textContent = 
                String(hours).padStart(2,'0') + ':' + 
                String(minutes).padStart(2,'0') + ':' + 
                String(seconds).padStart(2,'0');
            
            // AI Status
            document.getElementById('aiStatus').textContent = 'ACTIVE';
            document.getElementById('aiStatusTag').textContent = 'ACTIVE';
            
            // Threat level based on detections
            var threat = 'LOW';
            var detections = data.detections || 0;
            if (detections > 10) threat = 'CRITICAL';
            else if (detections > 5) threat = 'HIGH';
            else if (detections > 2) threat = 'MEDIUM';
            document.getElementById('threatOverlay').textContent = 'THREAT: ' + threat;
            document.getElementById('threatOverlay').style.color = 
                threat === 'CRITICAL' ? '#ff1744' :
                threat === 'HIGH' ? '#ffd740' :
                threat === 'MEDIUM' ? '#ffab40' : '#00e676';
        });
        
        socket.on('new_alert', function(data) {
            var list = document.getElementById('threatList');
            var item = document.createElement('div');
            item.className = 'threat-item';
            var severityClass = data.severity ? data.severity.toLowerCase() : 'low';
            var time = new Date().toLocaleTimeString();
            item.innerHTML = `
                <span class="severity ${severityClass}">${data.severity || 'LOW'}</span>
                <span>${data.message}</span>
                <span class="time">${time}</span>
                <button class="action-btn">VIEW</button>
            `;
            list.insertBefore(item, list.firstChild);
            if (list.children.length > 10) {
                list.removeChild(list.lastChild);
            }
        });
    </script>
</body>
</html>'''

with open('templates/command_center.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🛡️ IBVAP - COMMAND CENTER DASHBOARD")
    print("=" * 70)
    print(f"🌐 Dashboard: http://localhost:5000")
    print(f"🎬 Style: Command Center / Border Surveillance")
    print(f"🤖 GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
    print("=" * 70)
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        processing = False
        print("\n🛑 Shutting down...")
