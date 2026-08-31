# ============================================================
# IBVAP - Video Pipeline Processor (Controller)
# Orchestrates Direct Video File Processing & AI Pipeline
# ============================================================

import os
import cv2
import time
import logging
from threading import Lock

from video.video_reader import FileVideoSource
from tracking.tracker import ObjectTracker
from face.face_detector import FaceDetector
from anpr.plate_detector import ANPRDetector
from zones.virtual_fence import VirtualFenceZone
from behaviour.behaviour_engine import BehaviourEngine
from threat.threat_fusion import ThreatFusionEngine
from incidents.incident_manager import IncidentManager
from evidence.evidence_manager import EvidenceManager
from database.database import Database

logger = logging.getLogger("IBVAP.Processor")

class VideoPipelineProcessor:
    """Master Controller processing direct video files through the modular AI pipeline."""
    
    def __init__(self, detector, video_path="data/videos/top_view_pedestrian.mp4"):
        self.lock = Lock()
        self.detector = detector
        self.video_path = video_path
        self.source = FileVideoSource(video_path)
        self.tracker = ObjectTracker()
        self.face_detector = FaceDetector(blur_enabled=True)
        self.anpr_detector = ANPRDetector()
        self.virtual_fence = VirtualFenceZone(zone_id="Zone A")
        self.behaviour_engine = BehaviourEngine(loiter_threshold_sec=15.0)
        self.incident_manager = IncidentManager()
        self.evidence_manager = EvidenceManager()
        self.db = Database()
        
        # State Controls
        self.state = "PLAYING" # PLAYING, PAUSED, STOPPED
        self.process_every_n_frames = 1
        self.frame_counter = 0
        self.latest_stats = {
            'people': 0,
            'vehicles': 0,
            'fps': 30.0,
            'latency_ms': 10.0,
            'active_alerts': 0,
            'risk_score': 0,
            'risk_level': 'LOW',
            'state': self.state
        }

    def change_video(self, new_path: str):
        with self.lock:
            if not os.path.exists(new_path):
                logger.error(f"Cannot change video. Path not found: {new_path}")
                return False
            self.source.release()
            self.video_path = new_path
            self.source = FileVideoSource(new_path)
            self.tracker = ObjectTracker()
            self.state = "PLAYING"
            logger.info(f"Video changed to: {new_path}")
            return True

    def play(self):
        with self.lock:
            self.state = "PLAYING"

    def pause(self):
        with self.lock:
            self.state = "PAUSED"

    def resume(self):
        with self.lock:
            self.state = "PLAYING"

    def stop(self):
        with self.lock:
            self.state = "STOPPED"

    def restart(self):
        with self.lock:
            if self.source:
                self.source.seek(0)
            self.state = "PLAYING"

    def set_process_every_n_frames(self, n: int):
        with self.lock:
            self.process_every_n_frames = max(1, n)

    def process_next_frame(self):
        """Reads and processes next frame through full AI pipeline."""
        with self.lock:
            if self.state == "STOPPED" or not self.source or not self.source.is_opened():
                return None, self.latest_stats

            ret, frame = self.source.read_frame()
            if not ret or frame is None:
                return None, self.latest_stats

            self.frame_counter += 1
            
            # Frame skipping optimization if process_every_n_frames > 1
            if self.frame_counter % self.process_every_n_frames != 0:
                annotated_frame = self.virtual_fence.draw_zone(frame)
                return annotated_frame, self.latest_stats

            # 1. YOLO Object Detection & Tracking
            annotated_frame, det_stats = self.detector.process_frame(frame, draw_boxes=True)

            # 2. Face Privacy Blur & Telemetry
            annotated_frame, face_count = self.face_detector.process_faces(annotated_frame)

            # 3. Draw Virtual Fence Zone
            annotated_frame = self.virtual_fence.draw_zone(annotated_frame)

            # Update Latest Metrics
            self.latest_stats.update(det_stats)
            self.latest_stats['face_stats'] = self.face_detector.get_stats()
            self.latest_stats['state'] = self.state

            return annotated_frame, self.latest_stats
