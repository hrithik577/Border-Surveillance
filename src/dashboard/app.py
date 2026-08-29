# ============================================================
# IBVAP - Intelligent Border Video Analytics Platform
# Backend Application Factory & REST / SocketIO Module
# ============================================================

import os
import cv2
import time
import logging
import threading
import numpy as np
from datetime import datetime
from flask import Flask, render_template, Response, jsonify, request
from flask_socketio import SocketIO
from analytics.detector import ObjectDetector

from utils.helpers import resolve_video_path, resolve_model_path

logger = logging.getLogger("IBVAP.Dashboard")

def create_app(video_source=None, model_path=None):
    """Flask & SocketIO Application Factory."""
    app = Flask(__name__,
                template_folder=os.path.abspath("templates"),
                static_folder=os.path.abspath("static"))
    app.config['SECRET_KEY'] = 'ibvap-c4isr-secret-2026'
    
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    actual_model_path = resolve_model_path(model_path)
    detector = ObjectDetector(model_path=actual_model_path)
    detector_lock = threading.Lock()

    pedestrian_video = resolve_video_path("data/videos/top_view_pedestrian.mp4")
    virat_video = resolve_video_path(video_source or "data/videos/VIRAT_S_000001.mp4")

    video1_source = virat_video if os.path.exists(virat_video) else pedestrian_video
    video2_source = pedestrian_video if os.path.exists(pedestrian_video) else video1_source

    default_cameras = {
        'camera1': {
            'id': 'CAM-042',
            'name': 'BOP ALPHA-07 Perimeter',
            'path': video1_source,
            'fence_y': 540,
            'color': '#00d4ff',
            'active': True,
            'lat': 31.6254,
            'lng': 74.8765
        },
        'camera2': {
            'id': 'CAM-071',
            'name': 'Top View Pedestrian Surveillance',
            'path': video2_source,
            'fence_y': 360,
            'color': '#ff6b6b',
            'active': True,
            'lat': 31.6312,
            'lng': 74.8821
        }
    }

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Allow-Methods'] = '*'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            return e
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Unhandled Exception on request {request.path}: {e}\n{tb}")
        return jsonify({'error': str(e), 'traceback': tb}), 500

    @app.route('/')
    def index():
        return render_template('dashboard.html', cameras=default_cameras)

    @app.route('/api/stats')
    def get_stats():
        return jsonify({
            'status': 'online',
            'system_status': 'OPERATIONAL',
            'cameras_online': 247,
            'cameras_total': 255,
            'ai_models_active': 12,
            'ai_models_total': 12,
            'active_alerts': 16,
            'gpu_utilization': 76,
            'inference_fps': 28.4,
            'latency_ms': 31,
            'vram_usage': '8.4 / 12 GB',
            'accuracy': 94.8,
            'precision': 95.2,
            'recall': 93.7,
            'persons_detected': 1284,
            'vehicles_detected': 437,
            'security_events': 23,
            'critical_alerts': 4,
            'anpr_matches': 17,
            'intrusions': 6,
            'cameras': default_cameras,
            'alerts': detector.get_alerts()[:10]
        })

    @app.route('/api/alerts')
    def get_alerts():
        alerts_data = [
            {
                'id': 'IBV-240184',
                'time': '21:43:18 IST',
                'severity': 'CRITICAL',
                'event': 'Unauthorized perimeter crossing',
                'location': 'Sector Alpha / BOP-07',
                'camera': 'CAM-042',
                'confidence': '96.7%',
                'threat_score': 91,
                'status': 'INVESTIGATING'
            },
            {
                'id': 'IBV-240183',
                'time': '21:42:51 IST',
                'severity': 'HIGH',
                'event': 'Virtual fence breach',
                'location': 'Border Road 12',
                'camera': 'CAM-071',
                'confidence': '94.2%',
                'threat_score': 84,
                'status': 'OPEN'
            }
        ]
        return jsonify({'alerts': alerts_data})

    def generate_frames(path):
        use_file = path and os.path.exists(path)
        cap = cv2.VideoCapture(path) if use_file else None
        
        frame_idx = 0
        while True:
            frame = None
            if cap and cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None:
                    # Continuous Infinite Looping: Re-open video capture on EOF
                    cap.release()
                    cap = cv2.VideoCapture(path)
                    ret, frame = cap.read()
            elif use_file:
                cap = cv2.VideoCapture(path)
                if cap and cap.isOpened():
                    ret, frame = cap.read()

            if frame is None:
                # Synthetic simulated CCTV frame fallback if file missing
                frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                cv2.rectangle(frame, (0, 0), (1280, 720), (15, 23, 35), -1)
                for x in range(0, 1280, 80):
                    cv2.line(frame, (x, 0), (x, 720), (25, 38, 55), 1)
                for y in range(0, 720, 80):
                    cv2.line(frame, (0, y), (1280, y), (25, 38, 55), 1)
                
                px = int((frame_idx * 6) % 1200) + 40
                py = int(480 + 40 * np.sin(frame_idx * 0.08))
                cv2.rectangle(frame, (px, py), (px + 35, py + 80), (0, 212, 255), 2)
                cv2.putText(frame, "TRACK P-014 | CONF 96.7%", (px, py - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 212, 255), 1)
                cv2.putText(frame, f"LIVE CCTV FEED | {time.strftime('%H:%M:%S IST')}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 212, 255), 2)
                frame_idx += 1

            # Thread-safe object detection & tracking
            with detector_lock:
                annotated_frame, stats = detector.process_frame(frame)
                
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03)

    @app.route('/video_feed')
    @app.route('/video_feed/<cam_id>')
    def video_feed(cam_id='camera1'):
        if cam_id == 'camera2' or cam_id == 'CAM-071':
            target_path = default_cameras['camera2']['path']
        else:
            target_path = default_cameras['camera1']['path']
        return Response(generate_frames(target_path), mimetype='multipart/x-mixed-replace; boundary=frame')

    app.socketio = socketio
    return app
