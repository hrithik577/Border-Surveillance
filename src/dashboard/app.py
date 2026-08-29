# ============================================================
# IBVAP - Dashboard Server Module
# ============================================================

import os
import cv2
import time
import logging
import numpy as np
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
    app.config['SECRET_KEY'] = 'ibvap-secret-key-2026'
    
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    actual_model_path = resolve_model_path(model_path)
    detector = ObjectDetector(model_path=actual_model_path)

    video1_source = resolve_video_path(video_source or "data/videos/VIRAT_S_000001.mp4")
    video2_source = resolve_video_path("C:/Users/bhrit/Downloads/09152008flight2tape1_1.mpg")
    if video2_source == video1_source or not os.path.exists(video2_source):
        video2_source = video1_source

    default_cameras = {
        'camera1': {
            'name': 'Border Camera 1',
            'path': video1_source,
            'fence_y': 540,
            'color': '#00d4ff',
            'active': True
        },
        'camera2': {
            'name': 'Border Camera 2',
            'path': video2_source,
            'fence_y': 360,
            'color': '#ff6b6b',
            'active': True
        }
    }

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
            'cameras': default_cameras,
            'alerts': detector.get_alerts()[:10],
            'history': []
        })

    @app.route('/api/alerts')
    def get_alerts():
        return jsonify({'alerts': [a.get('message', str(a)) for a in detector.get_alerts()]})

    @app.route('/api/detections')
    def get_detections():
        return jsonify({'detections': []})

    @app.route('/api/history')
    def get_history():
        return jsonify({'history': []})

    def generate_frames(path):
        use_file = path and (os.path.exists(path) or str(path).startswith("rtsp://") or str(path).isdigit())
        cap = cv2.VideoCapture(path) if use_file else None
        
        frame_idx = 0
        while True:
            frame = None
            if cap and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()
            
            if frame is None:
                # Generate synthetic simulated CCTV frame if video source unavailable
                frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                cv2.rectangle(frame, (0, 0), (1280, 720), (15, 23, 35), -1)
                for x in range(0, 1280, 80):
                    cv2.line(frame, (x, 0), (x, 720), (25, 38, 55), 1)
                for y in range(0, 720, 80):
                    cv2.line(frame, (0, y), (1280, y), (25, 38, 55), 1)
                
                # Draw simulated moving target
                px = int((frame_idx * 6) % 1200) + 40
                py = int(480 + 40 * np.sin(frame_idx * 0.08))
                cv2.rectangle(frame, (px, py), (px + 35, py + 80), (0, 212, 255), 2)
                cv2.putText(frame, "SIMULATED TARGET", (px, py - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 212, 255), 1)
                
                cv2.putText(frame, f"LIVE CCTV FEED | {time.strftime('%H:%M:%S')}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 212, 255), 2)
                frame_idx += 1

            annotated_frame, stats = detector.process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.04)

    @app.route('/video_feed')
    @app.route('/video_feed/<cam_id>')
    def video_feed(cam_id='camera1'):
        cam_info = default_cameras.get(cam_id, default_cameras['camera1'])
        return Response(generate_frames(cam_info['path']), mimetype='multipart/x-mixed-replace; boundary=frame')

    app.socketio = socketio
    return app
