# ============================================================
# IBVAP - Evidence Vault Module
# Save incident snapshot, metadata JSON, and clip files
# ============================================================

import os
import cv2
import json
import logging

logger = logging.getLogger("IBVAP.Evidence")

class EvidenceManager:
    """Manages disk persistence of incident snapshots & structured metadata JSON."""
    
    def __init__(self, base_dir="data/evidence"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_evidence(self, incident_id: str, frame, metadata: dict):
        """Saves frame snapshot.jpg and metadata.json under data/evidence/INC-XXXXX/."""
        inc_dir = os.path.join(self.base_dir, incident_id)
        os.makedirs(inc_dir, exist_ok=True)
        
        snapshot_path = os.path.join(inc_dir, "snapshot.jpg")
        meta_path = os.path.join(inc_dir, "metadata.json")
        
        if frame is not None:
            cv2.imwrite(snapshot_path, frame)
            
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Saved Evidence Vault Record for {incident_id} -> {inc_dir}")
        return {
            'snapshot_path': snapshot_path,
            'metadata_path': meta_path
        }
