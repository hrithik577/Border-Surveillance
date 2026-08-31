# ============================================================
# IBVAP - Database Connection & Schema Initialization
# SQLite Storage for Videos, Detections, Incidents, & Feedback
# ============================================================

import os
import sqlite3
import logging

logger = logging.getLogger("IBVAP.Database")

class Database:
    """SQLite Database helper for storing surveillance telemetry, incidents, and feedback."""
    
    def __init__(self, db_path="data/ibvap_surveillance.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Videos table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                fps REAL,
                duration_sec REAL,
                total_frames INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            # Incidents table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                risk_score INTEGER,
                track_id INTEGER,
                timestamp TEXT,
                description TEXT,
                status TEXT DEFAULT 'NEW',
                feedback TEXT
            );
            """)
            
            # Feedback table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                notes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            conn.commit()
            logger.info(f"SQLite Surveillance Database initialized at: {self.db_path}")
