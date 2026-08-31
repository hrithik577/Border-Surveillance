# ============================================================
# IBVAP - Behaviour Analysis Module
# Explainable Rule Engine (Loitering, Night Movement, Unusual Path)
# ============================================================

import time
import logging

logger = logging.getLogger("IBVAP.Behaviour")

class BehaviourEngine:
    """Explainable rule engine analyzing track dwell time, loitering, and nocturnal movement."""
    
    def __init__(self, loiter_threshold_sec=15.0, night_mode=False):
        self.loiter_threshold_sec = loiter_threshold_sec
        self.night_mode = night_mode
        self.loiter_alerts = set()

    def evaluate(self, tracked_subject, is_in_zone: bool):
        """
        Evaluates behavioral rules on a TrackedSubject.
        Returns list of event dicts with plain-text explanation.
        """
        events = []
        tid = tracked_subject.track_id
        cname = tracked_subject.class_name
        dwell_sec = tracked_subject.dwell_time_sec

        # 1. Loitering Rule
        if is_in_zone and dwell_sec >= self.loiter_threshold_sec:
            if tid not in self.loiter_alerts:
                self.loiter_alerts.add(tid)
                events.append({
                    'type': 'LOITERING',
                    'track_id': tid,
                    'explanation': f"{cname} #{tid} remained inside Restricted Zone A for {int(dwell_sec)} seconds.",
                    'score_boost': 15
                })

        # 2. Night Movement Rule
        current_hour = time.localtime().tm_hour
        is_night_time = self.night_mode or (current_hour >= 22 or current_hour < 5)
        if is_night_time and is_in_zone:
            events.append({
                'type': 'NIGHT_MOVEMENT',
                'track_id': tid,
                'explanation': f"Nocturnal movement detected for {cname} #{tid} in Sector Alpha during night hours.",
                'score_boost': 20
            })

        return events
