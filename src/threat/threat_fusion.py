# ============================================================
# IBVAP - Threat Fusion Engine Module
# Multi-Signal Risk Scoring (0-100) & Categorization
# ============================================================

class ThreatFusionEngine:
    """Weighted Risk Engine fusing intrusion, night movement, loitering, and watchlist signals."""
    
    WEIGHTS = {
        'VIRTUAL_FENCE_INTRUSION': 40,
        'NIGHT_MOVEMENT': 20,
        'LOITERING': 15,
        'WATCHLIST_MATCH': 40,
        'CROSS_CAMERA_ANOMALY': 15
    }

    @staticmethod
    def calculate_risk(events: list):
        """
        Fuses event signals into a 0-100 risk score and level.
        Returns score, level, and list of contributing factors.
        """
        raw_score = 0
        factors = []
        
        for ev in events:
            etype = ev.get('type') or ev.get('event_type')
            explanation = ev.get('explanation') or ev.get('message') or etype
            boost = ThreatFusionEngine.WEIGHTS.get(etype, 10)
            raw_score += boost
            factors.append(f"{etype} (+{boost}): {explanation}")
            
        final_score = min(100, raw_score)
        
        if final_score >= 80:
            level = "CRITICAL"
        elif final_score >= 60:
            level = "HIGH"
        elif final_score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"
            
        return final_score, level, factors
