# ============================================================
# IBVAP - Dashboard Server Module
# ============================================================

import os
import cv2
import time
import logging
from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO
from analytics.detector import ObjectDetector

logger = logging.getLogger("IBVAP.Dashboard")

def create_app(video_source="data/videos/VIRAT_S_000001.mp4", model_path="data/models/yolov8n.pt"):
    """Flask & SocketIO Application Factory."""
    app = Flask(__name__,
                template_folder=os.path.abspath("templates"),
                static_folder=os.path.abspath("static"))
    app.config['SECRET_KEY'] = 'ibvap-secret-key-2026'
    
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    detector = ObjectDetector(model_path=model_path)
    
    @app.route('/')
    def index():
        return render_template('dashboard.html')
        
    @app.route('/api/stats')
    def get_stats():
        return jsonify({
            'status': 'online',
            'video_source': video_source,
            'alerts': detector.get_alerts()[:10]
        })

    def generate_frames():
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            logger.error(f"Cannot open video source: {video_source}")
            return
            
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
                
            annotated_frame, stats = detector.process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03)

    @app.route('/video_feed')
    def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
    app.socketio = socketio
    return app
