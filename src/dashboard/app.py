# ============================================================
# IBVAP - Intelligent Border Video Analytics Platform
# Backend Application Factory & REST / SocketIO Module
# ============================================================

import os
import cv2
import time
import logging
import random
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

    video1_source = resolve_video_path(video_source or "data/videos/VIRAT_S_000001.mp4")
    video2_source = resolve_video_path("C:/Users/bhrit/Downloads/09152008flight2tape1_1.mpg")
    if video2_source == video1_source or not os.path.exists(video2_source):
        video2_source = video1_source

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
            'name': 'Border Road 12 Junction',
            'path': video2_source,
            'fence_y': 360,
            'color': '#ff6b6b',
            'active': True,
            'lat': 31.6312,
            'lng': 74.8821
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
            },
            {
                'id': 'IBV-240180',
                'time': '21:41:07 IST',
                'severity': 'MEDIUM',
                'event': 'Unknown vehicle loitering',
                'location': 'Border Road 6',
                'camera': 'CAM-032',
                'confidence': '88.6%',
                'threat_score': 62,
                'status': 'MONITORING'
            },
            {
                'id': 'IBV-240177',
                'time': '21:38:22 IST',
                'severity': 'LOW',
                'event': 'ANPR watchlist correlation',
                'location': 'Gate 04 Checkpost',
                'camera': 'CAM-013',
                'confidence': '98.4%',
                'threat_score': 45,
                'status': 'ACKNOWLEDGED'
            }
        ]
        return jsonify({'alerts': alerts_data})

    @app.route('/api/anpr')
    def get_anpr():
        anpr_data = [
            {'plate': 'KA05XY7821', 'type': 'SUV', 'camera': 'CAM-032', 'location': 'Gate 04', 'time': '21:37 IST', 'confidence': '96.8%', 'status': 'REVIEW REQUIRED', 'flagged': True},
            {'plate': 'KA01AB1234', 'type': 'SEDAN', 'camera': 'CAM-013', 'location': 'Checkpost 02', 'time': '21:34 IST', 'confidence': '98.4%', 'status': 'CLEAR', 'flagged': False},
            {'plate': 'DL03CC9081', 'type': 'TRUCK', 'camera': 'CAM-056', 'location': 'Freight Gate', 'time': '21:28 IST', 'confidence': '94.1%', 'status': 'CLEAR', 'flagged': False},
            {'plate': 'HR26DQ4411', 'type': 'PICKUP', 'camera': 'CAM-091', 'location': 'Sector Bravo', 'time': '21:15 IST', 'confidence': '97.2%', 'status': 'CLEAR', 'flagged': False}
        ]
        return jsonify({'anpr': anpr_data})

    @app.route('/api/faces')
    def get_faces():
        faces_data = {
            'total_detected': 142,
            'authorized': 126,
            'unknown': 16,
            'review_required': 3,
            'recent': [
                {'id': 'FACE-1092', 'camera': 'CAM-042', 'time': '21:43 IST', 'confidence': '96.7%', 'status': 'UNKNOWN PERSON', 'flagged': True},
                {'id': 'FACE-1088', 'camera': 'CAM-013', 'time': '21:39 IST', 'confidence': '99.1%', 'status': 'AUTHORIZED PERSONNEL', 'flagged': False},
                {'id': 'FACE-1085', 'camera': 'CAM-032', 'time': '21:35 IST', 'confidence': '94.5%', 'status': 'UNKNOWN PERSON', 'flagged': True}
            ]
        }
        return jsonify(faces_data)

    @app.route('/api/behaviour')
    def get_behaviour():
        behaviour_events = [
            {'event': 'LOITERING EVENT', 'risk_score': 78, 'confidence': '91.4%', 'camera': 'CAM-013', 'duration': '04:18', 'status': 'ACTIVE'},
            {'event': 'WRONG-DIRECTION MOVEMENT', 'risk_score': 65, 'confidence': '89.2%', 'camera': 'CAM-056', 'duration': '01:45', 'status': 'MONITORING'},
            {'event': 'GROUP FORMATION NEAR FENCE', 'risk_score': 82, 'confidence': '93.7%', 'camera': 'CAM-042', 'duration': '03:10', 'status': 'REVIEW'}
        ]
        return jsonify({'behaviour': behaviour_events})

    @app.route('/api/evidence')
    def get_evidence():
        evidence_records = [
            {'id': 'EV-9941', 'incident_id': 'IBV-240184', 'camera': 'CAM-042', 'location': 'Sector Alpha / BOP-07', 'time': '21:43:18 IST', 'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'status': 'LOCKED'},
            {'id': 'EV-9940', 'incident_id': 'IBV-240183', 'camera': 'CAM-071', 'location': 'Border Road 12', 'time': '21:42:51 IST', 'hash': '8f4e9112423985a218d6e9871f9273c509748239081230491823940192834019', 'status': 'ARCHIVED'}
        ]
        return jsonify({'evidence': evidence_records})

    @app.route('/api/audit')
    def get_audit():
        audit_logs = [
            {'time': '21:43:23 IST', 'operator': 'OP-014', 'action': 'Incident acknowledged', 'resource': 'IBV-240184', 'status': 'SUCCESS'},
            {'time': '21:44:01 IST', 'operator': 'OP-014', 'action': 'Evidence locked', 'resource': 'EV-9941', 'status': 'SUCCESS'},
            {'time': '21:45:12 IST', 'operator': 'OP-014', 'action': 'Patrol alert dispatched', 'resource': 'SECTOR ALPHA / BOP-07', 'status': 'SUCCESS'}
        ]
        return jsonify({'audit': audit_logs})

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
                cv2.putText(frame, "TRACK P-014 | CONF 96.7%", (px, py - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 212, 255), 1)
                
                cv2.putText(frame, f"LIVE CCTV FEED | {time.strftime('%H:%M:%S IST')}", (20, 40),
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
