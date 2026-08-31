# ============================================================
# IBVAP - Virtual Fence Zone Module
# Operator-Defined Polygonal Restricted Zone Intrusion Analytics
# ============================================================

import cv2
import time
import numpy as np
import logging

logger = logging.getLogger("IBVAP.VirtualFence")

class VirtualFenceZone:
    """Polygonal Restricted Zone with debounce/cooldown logic."""
    
    def __init__(self, zone_id="Zone A", polygon=None, cooldown_sec=10.0):
        self.zone_id = zone_id
        self.cooldown_sec = cooldown_sec
        # Default polygon relative to 1280x720 frame: bottom border zone
        self.polygon = polygon if polygon is not None else np.array([
            [100, 480], [1180, 480], [1200, 700], [80, 700]
        ], dtype=np.int32)
        self.alert_history = {} # track_id -> timestamp

    def check_intrusion(self, track_id: int, class_name: str, center_pt: tuple, frame_w=1280, frame_h=720):
        """
        Checks if center_pt (x, y) falls inside the polygon zone.
        Returns intrusion dict if valid non-debounced alert, else None.
        """
        # Adjust polygon scale if frame dimensions differ
        poly_scaled = self.polygon
        if frame_w != 1280 or frame_h != 720:
            scale_x = frame_w / 1280.0
            scale_y = frame_h / 720.0
            poly_scaled = (self.polygon * [scale_x, scale_y]).astype(np.int32)
            
        # Point polygon test: > 0 inside, == 0 edge, < 0 outside
        dist = cv2.pointPolygonTest(poly_scaled, (float(center_pt[0]), float(center_pt[1])), False)
        if dist >= 0:
            now = time.time()
            last_alert_time = self.alert_history.get(track_id, 0)
            if now - last_alert_time >= self.cooldown_sec:
                self.alert_history[track_id] = now
                return {
                    'event_type': 'VIRTUAL_FENCE_INTRUSION',
                    'zone_id': self.zone_id,
                    'track_id': track_id,
                    'class_name': class_name,
                    'center': center_pt,
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                }
        return None

    def draw_zone(self, frame):
        """Draws translucent virtual fence polygon overlay on frame."""
        if frame is None:
            return frame
            
        h, w = frame.shape[:2]
        poly_scaled = self.polygon
        if w != 1280 or h != 720:
            poly_scaled = (self.polygon * [w / 1280.0, h / 720.0]).astype(np.int32)
            
        overlay = frame.copy()
        cv2.fillPoly(overlay, [poly_scaled], (0, 0, 180)) # red tint
        cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)
        cv2.polylines(frame, [poly_scaled], isClosed=True, color=(68, 68, 239), thickness=2)
        
        # Zone Label
        text_pt = (poly_scaled[0][0] + 10, poly_scaled[0][1] + 25)
        cv2.putText(frame, f"RESTRICTED ZONE ({self.zone_id})", text_pt,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        return frame
