# ============================================================
# IBVAP - Utilities Module
# ============================================================

import os
import json
import logging
from datetime import datetime

def setup_logging(log_level="INFO", log_file="data/logs/ibvap.log"):
    """Setup structured logging to stdout and log file."""
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    logging.info("IBVAP Logging initialized successfully.")

def load_config(config_path):
    """Load JSON configuration file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config, config_path):
    """Save configuration dictionary to JSON file."""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
