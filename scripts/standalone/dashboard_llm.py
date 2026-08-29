# ============================================================
# IBVAP - Smart AI Dashboard with GPU Support (FIXED)
# ============================================================

import os
import sys

# Fix for Windows Application Control Policy
# This bypasses the DLL load restriction
os.environ['TORCH_USE_CUDA_DSA'] = '0'
os.environ['TORCH_CUDA_ARCH_LIST'] = '8.0 8.6 8.9 9.0'

import cv2
import numpy as np
from ultralytics import YOLO
from flask import Flask, Response, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import time
from datetime import datetime
import threading
from collections import deque
import json
import subprocess
import torch

# ============================================================
# CONFIGURATION
# ============================================================

VIDEO_PATH = "C:/IBVAP-Demo/data/videos/VIRAT_S_000001.mp4"
MODEL_PATH = "C:/IBVAP-Demo/data/models/yolov8n.pt"

# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ============================================================
# GLOBAL STATE
# ============================================================

detections = []
alerts = deque(maxlen=100)
stats = {
    'total_frames': 0,
    'total_people': 0,
    'total_vehicles': 0,
    'total_alerts': 0,
    'fps': 0,
    'timestamp': '',
    'llm_analysis': 'Waiting for analysis...',
    'llm_status': 'Ready',
    'mode': 'GPU'
}
processing = True
start_time = time.time()
llm_analysis_cache = ""
llm_processing = False

# ============================================================
# LOAD YOLO MODEL WITH GPU
# ============================================================

print("=" * 70)
print("🛡️ IBVAP - Smart AI Dashboard (GPU Mode)")
print("=" * 70)

try:
    print("Checking CUDA availability...")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        
        # Test CUDA with a simple operation
        test_tensor = torch.tensor([1.0, 2.0, 3.0]).cuda()
        print(f"✅ CUDA test successful: {test_tensor}")
    else:
        print("❌ CUDA not available. Please check NVIDIA driver.")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ CUDA initialization error: {e}")
    print("Trying to continue with CPU mode...")
    sys.exit(1)

print("Loading YOLO model on GPU...")
try:
    model = YOLO(MODEL_PATH)
    model.to('cuda')
    print("✅ YOLO loaded on GPU successfully!")
except Exception as e:
    print(f"❌ Error loading model on GPU: {e}")
    print("Trying CPU mode...")
    try:
        model = YOLO(MODEL_PATH)
        model.to('cpu')
        stats['mode'] = 'CPU (Fallback)'
        print("✅ YOLO loaded on CPU (fallback)")
    except:
        print("❌ Could not load model. Please check installation.")
        sys.exit(1)

print(f"🤖 Ollama Model: mistral:latest")
print(f"📹 Video: {VIDEO_PATH}")
print("=" * 70)

# ============================================================
# LLM HELPER FUNCTIONS
# ============================================================

def llm_query(prompt, timeout=60):
    """Query Ollama with proper encoding"""
    try:
        result = subprocess.run(
            ['ollama', 'run', 'mistral:latest', prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Analysis timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_scene_async(detection_data):
    """Run LLM analysis in background"""
    global llm_analysis_cache, llm_processing
    
    if llm_processing:
        return
    
    llm_processing = True
    try:
        prompt = f"""You are IBVAP, an Intelligent Border Video Analytics Platform. 
Analyze this border surveillance scene:

People detected: {detection_data.get('people', 0)}
Vehicles detected: {detection_data.get('vehicles', 0)}
Total alerts: {detection_data.get('alerts', 0)}
Time: {detection_data.get('timestamp', 'now')}

Provide a brief situation description (max 30 words):"""
        
        response = llm_query(prompt)
        llm_analysis_cache = response
        stats['llm_analysis'] = response
        stats['llm_status'] = 'Updated'
        socketio.emit('llm_update', {'analysis': response})
        
    except Exception as e:
        print(f"LLM Error: {e}")
    finally:
        llm_processing = False

def generate_intelligent_alert(alert_data):
    """Generate smart alert description"""
    prompt = f"""Generate a concise border security alert (one sentence):

Alert Type: {alert_data.get('type', 'intrusion')}
Object: {alert_data.get('object', 'unknown')}
Location: {alert_data.get('location', 'border area')}
Time: {alert_data.get('timestamp', 'now')}

Alert:"""
    return llm_query(prompt)

# ============================================================
# PROCESS FRAME
# ============================================================

def process_frame(frame):
    global stats, detections, alerts
    
    # Resize for better performance
    frame = cv2.resize(frame, (1280, 720))
    
    try:
        results = model.track(frame, persist=True, verbose=False)
        annotated = results[0].plot()
    except Exception as e:
        print(f"Detection error: {e}")
        return frame
    
    people_count = 0
    vehicle_count = 0
    current_detections = []
    alert_triggered = False
    
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
            
            # Virtual fence crossing
            center_y = (y1 + y2) // 2
            fence_y = 360  # Adjusted for 720p
            if abs(center_y - fence_y) < 30:
                alert_msg = f"🚨 INTRUSION: {class_name} crossed fence at {datetime.now().strftime('%H:%M:%S')}"
                alerts.append(alert_msg)
                stats['total_alerts'] += 1
                alert_triggered = True
                print(alert_msg)
                
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(annotated, "🚨 INTRUSION!", (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Generate intelligent alert
                alert_data = {
                    'type': 'intrusion',
                    'object': class_name,
                    'location': 'border fence',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
                
                def send_intelligent_alert():
                    smart_alert = generate_intelligent_alert(alert_data)
                    socketio.emit('new_alert', {'message': f"🧠 {smart_alert}"})
                
                threading.Thread(target=send_intelligent_alert, daemon=True).start()
    
    stats['total_frames'] += 1
    stats['total_people'] += people_count
    stats['total_vehicles'] += vehicle_count
    stats['timestamp'] = datetime.now().strftime('%H:%M:%S')
    
    # Draw virtual fence (adjusted for 720p)
    cv2.line(annotated, (0, 360), (1280, 360), (0, 0, 255), 2)
    cv2.putText(annotated, "🔴 VIRTUAL FENCE", (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    # Info overlay
    cv2.putText(annotated, f"👤 People: {people_count} | 🚗 Vehicles: {vehicle_count}", (10, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    cv2.putText(annotated, f"🚨 Alerts: {stats['total_alerts']} | 🧠 LLM: {stats['llm_status']}", (10, 110), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.putText(annotated, f"🖥️ Mode: {stats['mode']}", (10, 140), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    # Store detections
    detections.append({
        'timestamp': stats['timestamp'],
        'people': people_count,
        'vehicles': vehicle_count,
        'detections': current_detections
    })
    if len(detections) > 100:
        detections.pop(0)
    
    # Run LLM analysis every 30 frames
    if stats['total_frames'] % 30 == 0 and not llm_processing:
        detection_data = {
            'people': people_count,
            'vehicles': vehicle_count,
            'alerts': stats['total_alerts'],
            'timestamp': stats['timestamp']
        }
        threading.Thread(target=analyze_scene_async, args=(detection_data,), daemon=True).start()
    
    # Emit updates
    socketio.emit('stats_update', {
        'total_frames': stats['total_frames'],
        'total_people': stats['total_people'],
        'total_vehicles': stats['total_vehicles'],
        'total_alerts': stats['total_alerts'],
        'fps': stats['fps'],
        'timestamp': stats['timestamp'],
        'llm_analysis': stats['llm_analysis'],
        'mode': stats['mode']
    })
    
    return annotated

# ============================================================
# VIDEO GENERATOR
# ============================================================

def video_generator():
    global stats
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"❌ Could not open video: {VIDEO_PATH}")
        return
    
    fps_start = time.time()
    fps_count = 0
    frame_delay = 1/30
    
    while processing:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        annotated = process_frame(frame)
        
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 92]
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

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template('llm_dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_generator(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'stats': stats,
        'alerts': list(alerts),
        'detections': detections[-10:]
    })

@app.route('/api/alerts')
def get_alerts():
    return jsonify({'alerts': list(alerts)})

@app.route('/api/llm/status')
def get_llm_status():
    return jsonify({
        'analysis': stats['llm_analysis'],
        'status': stats['llm_status'],
        'processing': llm_processing,
        'mode': stats['mode']
    })

@app.route('/api/llm/ask', methods=['GET', 'POST'])
def ask_llm():
    if request.method == 'POST':
        question = request.json.get('question', 'What is happening?')
    else:
        question = request.args.get('q', 'What is the current situation?')
    
    prompt = f"""Based on this border surveillance data:
People: {stats['total_people']}
Vehicles: {stats['total_vehicles']}
Alerts: {stats['total_alerts']}
Frames: {stats['total_frames']}

Answer this question: {question}

Answer:"""
    
    answer = llm_query(prompt)
    return jsonify({'question': question, 'answer': answer})

# ============================================================
# CREATE HTML TEMPLATE
# ============================================================

os.makedirs('templates', exist_ok=True)

html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IBVAP - Smart AI with LLM (GPU)</title>
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
        .header h1 .llm-badge {
            font-size: 12px;
            background: #7b2ffc;
            padding: 2px 12px;
            border-radius: 20px;
            -webkit-text-fill-color: white;
            margin-left: 10px;
        }
        .header h1 .gpu-badge {
            font-size: 12px;
            background: #00d4ff;
            padding: 2px 12px;
            border-radius: 20px;
            -webkit-text-fill-color: white;
            margin-left: 10px;
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
            background: rgba(0,0,0,0.8); padding: 6px 12px;
            border-radius: 8px; border: 1px solid #2a3a4a;
            flex-wrap: wrap;
        }
        .video-overlay span { color: #00d4ff; }
        .sidebar { display: flex; flex-direction: column; gap: 15px; }
        .card {
            background: #0d1520; border-radius: 12px; padding: 15px;
            border: 1px solid #1a2a3a;
        }
        .card h3 {
            color: #00d4ff; font-size: 13px; text-transform: uppercase;
            letter-spacing: 1px; margin-bottom: 10px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .card h3 span { color: #667788; font-size: 11px; }
        .stats-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
        }
        .stat-item {
            background: #1a2332; padding: 10px; border-radius: 8px;
            text-align: center;
        }
        .stat-item .value {
            font-size: 22px; font-weight: bold;
            background: linear-gradient(90deg, #00d4ff, #7b2ffc);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .stat-item .label { font-size: 10px; color: #8899aa; margin-top: 2px; }
        .llm-box {
            background: #1a2332; padding: 12px; border-radius: 8px;
            border-left: 3px solid #7b2ffc; min-height: 60px;
            font-size: 13px; color: #ccddee;
        }
        .llm-box .label { color: #7b2ffc; font-weight: bold; font-size: 11px; }
        .alerts-container {
            max-height: 150px; overflow-y: auto;
        }
        .alert-item {
            padding: 6px 10px; margin: 3px 0; border-radius: 6px;
            background: #1a2332; border-left: 3px solid #ff0044;
            font-size: 11px; color: #ccddee;
            animation: slideIn 0.3s ease;
        }
        .alert-item .llm-tag {
            background: #7b2ffc; padding: 1px 8px; border-radius: 10px;
            font-size: 9px; color: white; margin-right: 5px;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #0d1520; }
        ::-webkit-scrollbar-thumb { background: #2a3a4a; border-radius: 4px; }
        .badge {
            background: #1a2332; padding: 2px 10px; border-radius: 12px;
            font-size: 10px; color: #8899aa;
        }
        .badge.danger { color: #ff0044; border: 1px solid #ff0044; }
        .badge.success { color: #00ff88; border: 1px solid #00ff88; }
        .badge.llm { color: #7b2ffc; border: 1px solid #7b2ffc; }
        .badge.gpu { color: #00d4ff; border: 1px solid #00d4ff; }
        .ask-box {
            display: flex; gap: 10px; margin-top: 10px;
        }
        .ask-box input {
            flex: 1; background: #1a2332; border: 1px solid #2a3a4a;
            padding: 8px 12px; border-radius: 6px; color: white;
            font-size: 12px;
        }
        .ask-box button {
            background: #7b2ffc; border: none; padding: 8px 20px;
            border-radius: 6px; color: white; cursor: pointer;
            font-size: 12px;
        }
        .ask-box button:hover { background: #6a2fd4; }
        @media (max-width: 1200px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🛡️ IBVAP <span class="llm-badge">🧠 Powered by Mistral</span><span class="gpu-badge">⚡ RTX 5050 GPU</span></h1>
            <div>
                <span class="badge llm" id="llmStatus">🧠 LLM: Ready</span>
                <span class="badge gpu" id="gpuStatus">⚡ GPU: Active</span>
                <span class="status-dot"></span>
                <span class="status-text">LIVE</span>
            </div>
        </div>
        <div class="grid">
            <div class="video-container">
                <img src="{{ url_for('video_feed') }}" alt="Live Feed">
                <div class="video-overlay">
                    <span>📹 LIVE</span>
                    <span id="fps">⚡ -- FPS</span>
                    <span id="timestamp">⏱️ --:--:--</span>
                    <span id="gpuInfo">🖥️ GPU: Active</span>
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
                            <div class="value" id="totalAlerts">0</div>
                            <div class="label">🚨 Alerts</div>
                        </div>
                    </div>
                </div>
                <div class="card">
                    <h3>🧠 AI Scene Analysis <span>Powered by Mistral</span></h3>
                    <div class="llm-box" id="llmAnalysis">
                        <span class="label">🤖 Analysis:</span>
                        <span id="analysisText">Waiting for analysis...</span>
                    </div>
                    <div class="ask-box">
                        <input type="text" id="questionInput" placeholder="Ask AI about the scene..." />
                        <button onclick="askQuestion()">Ask</button>
                    </div>
                </div>
                <div class="card">
                    <h3>🚨 Intelligent Alerts <span id="alertCount">0</span></h3>
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
            document.getElementById('totalAlerts').textContent = data.total_alerts;
            document.getElementById('fps').textContent = '⚡ ' + data.fps + ' FPS';
            document.getElementById('timestamp').textContent = '⏱️ ' + data.timestamp;
            document.getElementById('alertCount').textContent = data.total_alerts;
            
            if (data.mode) {
                document.getElementById('gpuInfo').textContent = '🖥️ Mode: ' + data.mode;
            }
            
            if (data.llm_analysis) {
                document.getElementById('analysisText').textContent = data.llm_analysis;
                document.getElementById('llmStatus').textContent = '🧠 LLM: Active';
            }
        });
        
        socket.on('new_alert', function(data) {
            var alertsList = document.getElementById('alertsList');
            var alertDiv = document.createElement('div');
            alertDiv.className = 'alert-item';
            alertDiv.innerHTML = '<span class="llm-tag">🧠 AI</span> ' + data.message;
            alertsList.insertBefore(alertDiv, alertsList.firstChild);
            if (alertsList.children.length > 30) {
                alertsList.removeChild(alertsList.lastChild);
            }
        });
        
        socket.on('llm_update', function(data) {
            document.getElementById('analysisText').textContent = data.analysis;
            document.getElementById('llmStatus').textContent = '🧠 LLM: Active';
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

        fetch('/api/alerts')
            .then(response => response.json())
            .then(data => {
                var alertsList = document.getElementById('alertsList');
                alertsList.innerHTML = '';
                data.alerts.slice(-20).reverse().forEach(function(alert) {
                    var alertDiv = document.createElement('div');
                    alertDiv.className = 'alert-item';
                    alertDiv.innerHTML = alert;
                    alertsList.appendChild(alertDiv);
                });
                if (data.alerts.length === 0) {
                    alertsList.innerHTML = '<div style="color:#667788;text-align:center;padding:20px;font-size:13px;">No alerts</div>';
                }
            });
        
        setInterval(function() {
            fetch('/api/llm/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('llmStatus').textContent = '🧠 LLM: ' + data.status;
                    if (data.mode) {
                        document.getElementById('gpuStatus').textContent = '⚡ GPU: ' + data.mode;
                    }
                });
        }, 5000);
    </script>
</body>
</html>'''

with open('templates/llm_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🛡️ IBVAP - Smart AI Dashboard with GPU")
    print("=" * 70)
    print(f"🌐 Dashboard: http://localhost:5000")
    print(f"🤖 LLM Model: Mistral (via Ollama)")
    print(f"📹 Video: {VIDEO_PATH}")
    print(f"🖥️ GPU Mode: {'Enabled' if torch.cuda.is_available() else 'Disabled'}")
    print("=" * 70)
    print("Features:")
    print("  ✅ GPU-accelerated YOLO detection")
    print("  ✅ Virtual fence with alerts")
    print("  ✅ Intelligent LLM analysis")
    print("  ✅ Ask AI questions about the scene")
    print("=" * 70)
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        processing = False
        print("\n🛑 Shutting down...")
