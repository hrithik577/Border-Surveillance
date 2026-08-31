# ============================================================
# IBVAP - Object Tracker Module
# ByteTrack / BoT-SORT Persistent Target Tracking & Trajectories
# ============================================================

import time
import numpy as np
from collections import defaultdict, deque

class TrackedSubject:
    """Represents a single persistent tracked entity across video frames."""
    def __init__(self, track_id: int, class_name: str, bbox: list, confidence: float):
        self.track_id = track_id
        self.class_name = class_name
        self.bbox = bbox # [x1, y1, x2, y2]
        self.confidence = confidence
        self.center = (int((bbox[0] + bbox[2]) / 2), int((bbox[1] + bbox[3]) / 2))
        self.first_seen = time.time()
        self.last_seen = time.time()
        self.total_frames = 1
        self.trajectory = deque(maxlen=30)
        self.trajectory.append(self.center)
        
    def update(self, bbox: list, confidence: float):
        self.bbox = bbox
        self.confidence = confidence
        self.center = (int((bbox[0] + bbox[2]) / 2), int((bbox[1] + bbox[3]) / 2))
        self.last_seen = time.time()
        self.total_frames += 1
        self.trajectory.append(self.center)

    @property
    def dwell_time_sec(self):
        return round(self.last_seen - self.first_seen, 1)

class ObjectTracker:
    """Manages persistent track states, trajectories, and unique count statistics."""
    def __init__(self):
        self.tracks = {}
        self.total_unique_persons = set()
        self.total_unique_vehicles = set()
        
    def update_tracks(self, current_detections: list):
        """
        current_detections: list of dicts:
        {'track_id': int, 'class_name': str, 'bbox': [x1,y1,x2,y2], 'confidence': float}
        """
        active_ids = set()
        for det in current_detections:
            tid = det['track_id']
            cname = det['class_name']
            bbox = det['bbox']
            conf = det['confidence']
            active_ids.add(tid)
            
            if cname.upper() in ['PERSON', 'PEDESTRIAN']:
                self.total_unique_persons.add(tid)
            elif cname.upper() in ['CAR', 'TRUCK', 'BUS', 'MOTORCYCLE', 'VEHICLE']:
                self.total_unique_vehicles.add(tid)
                
            if tid in self.tracks:
                self.tracks[tid].update(bbox, conf)
            else:
                self.tracks[tid] = TrackedSubject(tid, cname, bbox, conf)
                
        return [self.tracks[tid] for tid in active_ids if tid in self.tracks]

    def get_stats(self):
        return {
            'active_tracks_count': len(self.tracks),
            'total_unique_persons': len(self.total_unique_persons),
            'total_unique_vehicles': len(self.total_unique_vehicles)
        }
