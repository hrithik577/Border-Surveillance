# ============================================================
# IBVAP - Incident Manager Module
# Incident Creation, Status Lifecycle, & Operator Feedback Log
# ============================================================

import time
from collections import deque

class IncidentManager:
    """Manages real incident records and human operator feedback."""
    
    def __init__(self, maxlen=100):
        self.incidents = deque(maxlen=maxlen)
        self.feedback_log = []
        self._counter = 1

    def create_incident(self, event_type: str, severity: str, risk_score: int, track_id: int, description: str, snapshot_path: str = None):
        incident_id = f"INC-{self._counter:05d}"
        self._counter += 1
        
        inc = {
            'incident_id': incident_id,
            'event_type': event_type,
            'severity': severity,
            'risk_score': risk_score,
            'track_id': track_id,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'description': description,
            'snapshot_path': snapshot_path,
            'video_reference': "DEMO_VIDEO",
            'status': "NEW",
            'feedback': None
        }
        self.incidents.appendleft(inc)
        return inc

    def update_status(self, incident_id: str, new_status: str):
        for inc in self.incidents:
            if inc['incident_id'] == incident_id:
                inc['status'] = new_status
                return inc
        return None

    def record_feedback(self, incident_id: str, feedback_type: str, notes: str = ""):
        """feedback_type: TRUE_POSITIVE or FALSE_POSITIVE"""
        for inc in self.incidents:
            if inc['incident_id'] == incident_id:
                inc['feedback'] = feedback_type
                if feedback_type == "FALSE_POSITIVE":
                    inc['status'] = "FALSE_POSITIVE"
                break
                
        entry = {
            'incident_id': incident_id,
            'feedback_type': feedback_type,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'notes': notes
        }
        self.feedback_log.append(entry)
        return entry

    def get_incidents(self):
        return list(self.incidents)
