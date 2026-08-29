# ============================================================
# IBVAP - HOLLYWOOD-STYLE ADVANCED DASHBOARD
# "Like in US Headquarters Movies"
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
import requests
import json
import subprocess
import random
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

VIDEO_PATH = r"C:\Users\bhrit\Downloads\vidssave.com Top View Pedestrian Dataset Sample 1 720P.mp4"
MODEL_PATH = "C:/IBVAP-Demo/data/models/yolov8n.pt"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:latest"

# ============================================================
# CHECK GPU
# ============================================================

print("=" * 70)
print("🎬 IBVAP - HOLLYWOOD-STYLE ADVANCED DASHBOARD")
print("=" * 70)

if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    device = 'cuda'
else:
    device = 'cpu'
print(f"Using device: {device.upper()}")

# ============================================================
# CHECK OLLAMA
# ============================================================

def check_ollama():
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": "Hello",
            "stream": False
        }, timeout=5)
        if response.status_code == 200:
            print(f"✅ Ollama running with model: {OLLAMA_MODEL}")
            return True
    except:
        print("⚠️ Ollama not responding")
    return False

llm_available = check_ollama()

# ============================================================
# TRY EASYOCR
# ============================================================

try:
    import easyocr
    anpr_reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
    ANPR_AVAILABLE = True
    print("✅ ANPR (EasyOCR) loaded")
except:
    anpr_reader = None
    ANPR_AVAILABLE = False
    print("⚠️ ANPR not available")

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
model = YOLO(MODEL_PATH)
model.to(device)
print(f"✅ YOLO loaded on {device.upper()}")

# ============================================================
# GLOBAL STATE
# ============================================================

alerts = deque(maxlen=200)
stats = {
    'total_frames': 0,
    'total_people': 0,
    'total_vehicles': 0,
    'total_alerts': 0,
    'fps': 0,
    'timestamp': '',
    'device': device.upper(),
    'detections': 0,
    'llm_status': 'Ready' if llm_available else 'Not Available',
    'anpr_status': 'Active' if ANPR_AVAILABLE else 'Disabled',
    'plates_detected': 0,
    'current_people': 0,
    'current_vehicles': 0,
    'threat_level': 'LOW',
    'system_uptime': 0
}
history = deque(maxlen=200)
processing = True
start_time = time.time()

# ============================================================
# LLM FUNCTION
# ============================================================

def query_llm(prompt):
    if not llm_available:
        return "LLM not available"
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7}
        }, timeout=30)
        if response.status_code == 200:
            return response.json().get('response', 'No response')
        return f"Error: {response.status_code}"
    except:
        return "LLM request failed"

def analyze_scene_async(detection_data):
    global stats
    if not llm_available:
        return
    try:
        prompt = f"""You are IBVAP, an Intelligent Border Video Analytics Platform.
Analyze this border surveillance scene:

People detected: {detection_data.get('people', 0)}
Vehicles detected: {detection_data.get('vehicles', 0)}
License plates detected: {detection_data.get('plates', [])}
Total alerts: {detection_data.get('alerts', 0)}
Detections: {detection_data.get('detections', 0)}
Time: {detection_data.get('timestamp', 'now')}

Provide a brief situation description (max 30 words):"""
        response = query_llm(prompt)
        stats['llm_analysis'] = response
        stats['llm_status'] = 'Updated'
        socketio.emit('llm_update', {'analysis': response})
        print(f"🧠 LLM: {response}")
    except Exception as e:
        print(f"LLM Error: {e}")

# ============================================================
# ANPR FUNCTION
# ============================================================

def detect_plates(frame):
    if anpr_reader is None:
        return []
    plates = []
    try:
        results = anpr_reader.readtext(frame)
        for (bbox, text, confidence) in results:
            clean_text = ''.join(c for c in text if c.isalnum())
            if 4 <= len(clean_text) <= 10 and confidence > 0.5:
                plates.append({
                    'text': clean_text,
                    'confidence': confidence,
                    'bbox': bbox
                })
    except:
        pass
    return plates

# ============================================================
# VIDEO GENERATOR
# ============================================================

def generate_frames():
    global stats, history
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"❌ Could not open video: {VIDEO_PATH}")
        return
    
    print(f"✅ Video loaded: {VIDEO_PATH}")
    
    fps_start = time.time()
    fps_count = 0
    frame_count = 0
    
    while processing:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        # Process at 720p for performance
        frame = cv2.resize(frame, (1280, 720))
        frame_count += 1
        
        try:
            results = model(frame, conf=0.25, verbose=False)
            annotated = results[0].plot()
            
            people_count = 0
            vehicle_count = 0
            det_count = 0
            plates_detected = []
            
            if results[0].boxes is not None:
                classes = results[0].boxes.cls.cpu().numpy()
                det_count = len(classes)
                for cls in classes:
                    class_name = model.names[int(cls)]
                    if class_name == 'person':
                        people_count += 1
                    elif class_name in ['car', 'truck', 'bus', 'motorcycle', 'bicycle']:
                        vehicle_count += 1
            
            # ANPR
            if ANPR_AVAILABLE and frame_count % 10 == 0:
                plates = detect_plates(frame)
                for plate in plates:
                    plates_detected.append(plate['text'])
                    stats['plates_detected'] += 1
                    alert_msg = f"📋 PLATE: {plate['text']}"
                    alerts.append(alert_msg)
                    stats['total_alerts'] += 1
                    socketio.emit('new_alert', {'message': alert_msg, 'type': 'anpr'})
                    
                    # Draw plate
                    bbox = plate['bbox']
                    pts = np.array(bbox, np.int32)
                    cv2.polylines(annotated, [pts], True, (0, 255, 255), 2)
                    cv2.putText(annotated, f"PLATE: {plate['text']}", (bbox[0][0], bbox[0][1]-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Update stats
            stats['total_frames'] += 1
            stats['total_people'] += people_count
            stats['total_vehicles'] += vehicle_count
            stats['detections'] = det_count
            stats['current_people'] = people_count
            stats['current_vehicles'] = vehicle_count
            stats['timestamp'] = datetime.now().strftime('%H:%M:%S')
            stats['system_uptime'] = int(time.time() - start_time)
            
            # Threat level
            if people_count > 10 or vehicle_count > 5:
                stats['threat_level'] = 'CRITICAL'
            elif people_count > 5 or vehicle_count > 2:
                stats['threat_level'] = 'HIGH'
            elif people_count > 2 or vehicle_count > 0:
                stats['threat_level'] = 'MEDIUM'
            else:
                stats['threat_level'] = 'LOW'
            
            # Store history for charts
            history.append({
                'timestamp': stats['timestamp'],
                'people': people_count,
                'vehicles': vehicle_count,
                'alerts': stats['total_alerts']
            })
            
            # LLM analysis every 60 frames
            if frame_count % 60 == 0 and det_count > 0:
                detection_data = {
                    'people': people_count,
                    'vehicles': vehicle_count,
                    'plates': plates_detected,
                    'alerts': stats['total_alerts'],
                    'detections': det_count,
                    'timestamp': stats['timestamp']
                }
                threading.Thread(target=analyze_scene_async, args=(detection_data,), daemon=True).start()
            
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
                'llm_status': stats['llm_status'],
                'anpr_status': stats['anpr_status'],
                'plates_detected': stats['plates_detected'],
                'current_people': people_count,
                'current_vehicles': vehicle_count,
                'threat_level': stats['threat_level'],
                'system_uptime': stats['system_uptime']
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
    
    cap.release()

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template('hollywood_dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'stats': stats,
        'alerts': list(alerts),
        'history': list(history)
    })

@app.route('/api/alerts')
def get_alerts():
    return jsonify({'alerts': list(alerts)})

@app.route('/api/llm/ask', methods=['GET', 'POST'])
def ask_llm():
    if request.method == 'POST':
        question = request.json.get('question', 'What is happening?')
    else:
        question = request.args.get('q', 'What is the current situation?')
    
    prompt = f"""Based on this border surveillance data:
People: {stats['total_people']}
Vehicles: {stats['total_vehicles']}
License Plates: {stats['plates_detected']}
Alerts: {stats['total_alerts']}
Detections: {stats['detections']}
Frames: {stats['total_frames']}
Threat Level: {stats['threat_level']}

Answer this question: {question}

Answer:"""
    
    answer = query_llm(prompt)
    return jsonify({'question': question, 'answer': answer})

@app.route('/api/llm/status')
def get_llm_status():
    return jsonify({
        'status': stats['llm_status'],
        'available': llm_available
    })

# ============================================================
# CREATE HOLLYWOOD-STYLE HTML TEMPLATE
# ============================================================

os.makedirs('templates', exist_ok=True)

html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IBVAP - Advanced Border Surveillance</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Share Tech Mono', monospace;
            background: #0a0a12;
            color: #00ff88;
            min-height: 100vh;
            padding: 10px;
            overflow-x: hidden;
        }
        
        /* Scanning line effect */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ff88, transparent);
            animation: scanLine 3s linear infinite;
            z-index: 9999;
            box-shadow: 0 0 20px #00ff88;
        }
        
        @keyframes scanLine {
            0% { top: 0; opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { top: 100%; opacity: 0; }
        }
        
        .dashboard {
            max-width: 1920px;
            margin: 0 auto;
        }
        
        /* HEADER - Hollywood Style */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 25px;
            background: linear-gradient(135deg, rgba(0,20,40,0.95), rgba(0,10,20,0.98));
            border: 1px solid #00ff88;
            border-radius: 8px;
            margin-bottom: 10px;
            position: relative;
            box-shadow: 0 0 30px rgba(0,255,136,0.1);
        }
        
        .header::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 10%;
            width: 80%;
            height: 1px;
            background: linear-gradient(90deg, transparent, #00ff88, transparent);
            animation: pulseBorder 2s ease-in-out infinite;
        }
        
        @keyframes pulseBorder {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 1; }
        }
        
        .header h1 {
            font-family: 'Orbitron', monospace;
            font-size: 22px;
            font-weight: 900;
            background: linear-gradient(90deg, #00ff88, #00d4ff, #7b2ffc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: none;
            letter-spacing: 3px;
        }
        
        .header h1 small {
            font-family: 'Share Tech Mono', monospace;
            font-size: 11px;
            -webkit-text-fill-color: #667788;
            letter-spacing: 1px;
        }
        
        .header-status {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .status-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 11px;
            font-family: 'Orbitron', monospace;
            border: 1px solid #00ff88;
            color: #00ff88;
            background: rgba(0,255,136,0.05);
            letter-spacing: 1px;
        }
        
        .status-badge.critical {
            border-color: #ff0044;
            color: #ff0044;
            animation: blinkCritical 0.5s infinite;
        }
        
        @keyframes blinkCritical {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #00ff88;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
            box-shadow: 0 0 20px #00ff88;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.3; transform: scale(0.8); }
        }
        
        /* GRID LAYOUT */
        .grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 10px;
        }
        
        /* VIDEO CONTAINER */
        .video-container {
            background: rgba(0,10,20,0.95);
            border-radius: 8px;
            border: 1px solid rgba(0,255,136,0.2);
            overflow: hidden;
            position: relative;
            box-shadow: 0 0 40px rgba(0,255,136,0.05);
        }
        
        .video-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .video-overlay {
            position: absolute;
            top: 15px;
            left: 15px;
            display: flex;
            gap: 20px;
            font-size: 11px;
            font-family: 'Orbitron', monospace;
            background: rgba(0,0,0,0.85);
            padding: 8px 16px;
            border-radius: 4px;
            border: 1px solid rgba(0,255,136,0.3);
            letter-spacing: 1px;
            color: #00ff88;
        }
        
        .video-overlay .threat {
            color: #ff0044;
        }
        
        /* SIDEBAR */
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        /* CARDS */
        .card {
            background: rgba(0,10,20,0.95);
            border-radius: 8px;
            padding: 12px 15px;
            border: 1px solid rgba(0,255,136,0.15);
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 1px;
            background: linear-gradient(90deg, transparent, #00ff88, transparent);
            animation: pulseBorder 3s ease-in-out infinite;
        }
        
        .card h3 {
            font-family: 'Orbitron', monospace;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #667788;
            margin-bottom: 8px;
        }
        
        .card h3 .highlight {
            color: #00ff88;
        }
        
        /* STATS GRID */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 8px;
        }
        
        .stat-item {
            background: rgba(0,20,40,0.5);
            padding: 8px 10px;
            border-radius: 4px;
            text-align: center;
            border: 1px solid rgba(0,255,136,0.05);
            transition: all 0.3s;
        }
        
        .stat-item:hover {
            border-color: rgba(0,255,136,0.2);
            background: rgba(0,30,50,0.5);
        }
        
        .stat-item .value {
            font-family: 'Orbitron', monospace;
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(90deg, #00ff88, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-item .label {
            font-size: 9px;
            color: #667788;
            margin-top: 2px;
            letter-spacing: 1px;
        }
        
        .stat-item .sub {
            font-size: 8px;
            color: #445566;
        }
        
        /* THREAT LEVEL */
        .threat-display {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 10px;
            border-radius: 4px;
            background: rgba(0,0,0,0.3);
        }
        
        .threat-display .level {
            font-family: 'Orbitron', monospace;
            font-size: 18px;
            font-weight: 900;
            letter-spacing: 2px;
        }
        
        .threat-display .level.low { color: #00ff88; }
        .threat-display .level.medium { color: #ffd93d; }
        .threat-display .level.high { color: #ff6b35; }
        .threat-display .level.critical { color: #ff0044; animation: blinkCritical 0.5s infinite; }
        
        /* LLM BOX */
        .llm-box {
            background: rgba(0,20,40,0.3);
            padding: 10px 12px;
            border-radius: 4px;
            min-height: 45px;
            font-size: 12px;
            color: #88bbcc;
            border-left: 2px solid #7b2ffc;
            font-family: 'Share Tech Mono', monospace;
        }
        
        .llm-box .label {
            color: #7b2ffc;
            font-weight: bold;
            font-size: 10px;
        }
        
        /* ASK BOX */
        .ask-box {
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }
        
        .ask-box input {
            flex: 1;
            background: rgba(0,20,40,0.5);
            border: 1px solid rgba(0,255,136,0.2);
            padding: 6px 12px;
            border-radius: 4px;
            color: #00ff88;
            font-family: 'Share Tech Mono', monospace;
            font-size: 11px;
        }
        
        .ask-box input::placeholder {
            color: #445566;
        }
        
        .ask-box button {
            background: linear-gradient(135deg, #00ff88, #00d4ff);
            border: none;
            padding: 6px 18px;
            border-radius: 4px;
            color: #0a0a12;
            font-family: 'Orbitron', monospace;
            font-size: 10px;
            cursor: pointer;
            letter-spacing: 1px;
            transition: all 0.3s;
        }
        
        .ask-box button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(0,255,136,0.3);
        }
        
        /* ALERTS */
        .alerts-container {
            max-height: 80px;
            overflow-y: auto;
        }
        
        .alert-item {
            padding: 4px 10px;
            margin: 3px 0;
            border-radius: 3px;
            background: rgba(0,20,40,0.3);
            border-left: 2px solid #ff0044;
            font-size: 10px;
            color: #88bbcc;
            font-family: 'Share Tech Mono', monospace;
        }
        
        .alert-item.anpr {
            border-left-color: #ffd93d;
        }
        
        .alert-item .time {
            color: #445566;
            font-size: 9px;
        }
        
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: rgba(0,10,20,0.5); }
        ::-webkit-scrollbar-thumb { background: #00ff88; border-radius: 2px; }
        
        /* CHART */
        .chart-container {
            height: 70px;
            margin-top: 5px;
        }
        
        /* RESPONSIVE */
        @media (max-width: 1200px) {
            .grid { grid-template-columns: 1fr; }
            .stats-grid { grid-template-columns: 1fr 1fr; }
        }
        
        /* GLOW EFFECTS */
        .glow {
            box-shadow: 0 0 30px rgba(0,255,136,0.03);
        }
        
        .text-glow {
            text-shadow: 0 0 20px rgba(0,255,136,0.3);
        }
        
        /* CORNER BRACKETS */
        .corner-brackets {
            position: relative;
        }
        
        .corner-brackets::before,
        .corner-brackets::after {
            content: '';
            position: absolute;
            width: 15px;
            height: 15px;
            border-color: #00ff88;
            border-style: solid;
            opacity: 0.2;
        }
        
        .corner-brackets::before {
            top: 5px;
            left: 5px;
            border-width: 1px 0 0 1px;
        }
        
        .corner-brackets::after {
            bottom: 5px;
            right: 5px;
            border-width: 0 1px 1px 0;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- HEADER -->
        <div class="header">
            <h1>🛡️ IBVAP <small>Intelligent Border Video Analytics Platform</small></h1>
            <div class="header-status">
                <span class="status-badge" id="threatBadge">🟢 THREAT: LOW</span>
                <span class="status-badge">⚡ <span id="fpsHeader">0</span> FPS</span>
                <span class="status-badge">⏱️ <span id="uptime">00:00:00</span></span>
                <span class="status-dot"></span>
                <span style="color:#00ff88;font-size:11px;">LIVE</span>
            </div>
        </div>
        
        <!-- MAIN GRID -->
        <div class="grid">
            <!-- VIDEO -->
            <div class="video-container">
                <img src="{{ url_for('video_feed') }}" alt="Live Feed">
                <div class="video-overlay">
                    <span>📹 LIVE</span>
                    <span id="fpsOverlay">⚡ 0 FPS</span>
                    <span id="timeOverlay">⏱️ --:--:--</span>
                    <span id="detectionsOverlay">🎯 0</span>
                    <span class="threat" id="threatOverlay">🔴 LOW</span>
                </div>
            </div>
            
            <!-- SIDEBAR -->
            <div class="sidebar">
                <!-- STATS -->
                <div class="card">
                    <h3>📊 <span class="highlight">LIVE</span> STATISTICS</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="value" id="totalFrames">0</div>
                            <div class="label">TOTAL FRAMES</div>
                        </div>
                        <div class="stat-item">
                            <div class="value" id="totalPeople">0</div>
                            <div class="label">👤 PEOPLE</div>
                        </div>
                        <div class="stat-item">
                            <div class="value" id="totalVehicles">0</div>
                            <div class="label">🚗 VEHICLES</div>
                        </div>
                        <div class="stat-item">
                            <div class="value" id="totalPlates">0</div>
                            <div class="label">📋 PLATES</div>
                        </div>
                    </div>
                </div>
                
                <!-- THREAT LEVEL -->
                <div class="card">
                    <h3>🚨 <span class="highlight">THREAT</span> ASSESSMENT</h3>
                    <div class="threat-display">
                        <span style="font-size:10px;color:#667788;">CURRENT STATUS</span>
                        <span class="level" id="threatLevelDisplay">LOW</span>
                        <span style="font-size:10px;color:#667788;" id="threatDetails">Normal activity</span>
                    </div>
                </div>
                
                <!-- LLM ANALYSIS -->
                <div class="card">
                    <h3>🧠 <span class="highlight">AI</span> SCENE ANALYSIS</h3>
                    <div class="llm-box" id="llmAnalysis">
                        <span class="label">🤖 ANALYSIS:</span>
                        <span id="analysisText">Waiting for analysis...</span>
                    </div>
                    <div class="ask-box">
                        <input type="text" id="questionInput" placeholder="Ask AI about the scene..." />
                        <button onclick="askQuestion()">ASK</button>
                    </div>
                </div>
                
                <!-- ALERTS -->
                <div class="card">
                    <h3>🚨 <span class="highlight">REAL-TIME</span> ALERTS <span style="color:#667788;font-size:9px;" id="alertCount">0</span></h3>
                    <div class="alerts-container" id="alertsList">
                        <div style="color:#445566;text-align:center;padding:10px;font-size:11px;">NO ALERTS</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        
        socket.on('stats_update', function(data) {
            // Stats
            document.getElementById('totalFrames').textContent = data.total_frames;
            document.getElementById('totalPeople').textContent = data.total_people;
            document.getElementById('totalVehicles').textContent = data.total_vehicles;
            document.getElementById('totalPlates').textContent = data.plates_detected || 0;
            
            // FPS
            var fps = data.fps || 0;
            document.getElementById('fpsOverlay').textContent = '⚡ ' + fps + ' FPS';
            document.getElementById('fpsHeader').textContent = fps;
            
            // Time
            document.getElementById('timeOverlay').textContent = '⏱️ ' + data.timestamp;
            
            // Detections
            document.getElementById('detectionsOverlay').textContent = '🎯 ' + (data.detections || 0);
            
            // Threat Level
            var threat = data.threat_level || 'LOW';
            var threatDisplay = document.getElementById('threatLevelDisplay');
            threatDisplay.textContent = threat;
            threatDisplay.className = 'level ' + threat.toLowerCase();
            
            document.getElementById('threatOverlay').textContent = '🔴 ' + threat;
            document.getElementById('threatBadge').textContent = '🟢 THREAT: ' + threat;
            document.getElementById('threatBadge').className = 'status-badge ' + threat.toLowerCase();
            
            // Uptime
            var uptime = data.system_uptime || 0;
            var hours = Math.floor(uptime / 3600);
            var minutes = Math.floor((uptime % 3600) / 60);
            var seconds = uptime % 60;
            document.getElementById('uptime').textContent = 
                String(hours).padStart(2,'0') + ':' + 
                String(minutes).padStart(2,'0') + ':' + 
                String(seconds).padStart(2,'0');
            
            // Alert count
            document.getElementById('alertCount').textContent = data.total_alerts || 0;
        });
        
        socket.on('llm_update', function(data) {
            document.getElementById('analysisText').textContent = data.analysis;
        });
        
        socket.on('new_alert', function(data) {
            var alertsList = document.getElementById('alertsList');
            var alertDiv = document.createElement('div');
            alertDiv.className = 'alert-item' + (data.type === 'anpr' ? ' anpr' : '');
            var time = new Date().toLocaleTimeString();
            alertDiv.innerHTML = '🚨 ' + data.message + ' <span class="time">' + time + '</span>';
            alertsList.insertBefore(alertDiv, alertsList.firstChild);
            if (alertsList.children.length > 20) {
                alertsList.removeChild(alertsList.lastChild);
            }
        });

        function askQuestion() {
            var input = document.getElementById('questionInput');
            var question = input.value.trim();
            if (!question) return;
            
            document.getElementById('analysisText').textContent = '🤔 Thinking...';
            
            fetch('/api/llm/ask?q=' + encodeURIComponent(question))
                .then(response => response.json())
                .then(data => {
                    document.getElementById('analysisText').textContent = data.answer;
                })
                .catch(error => {
                    document.getElementById('analysisText').textContent = 'Error: ' + error;
                });
            
            input.value = '';
        }

        document.getElementById('questionInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askQuestion();
            }
        });
    </script>
</body>
</html>'''

with open('templates/hollywood_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🎬 IBVAP - HOLLYWOOD-STYLE DASHBOARD")
    print("=" * 70)
    print(f"🌐 Dashboard: http://localhost:5000")
    print(f"🎬 Style: Hollywood/US Headquarters Theme")
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
