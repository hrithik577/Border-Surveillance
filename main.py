import sys
sys.stdout.reconfigure(encoding='utf-8')
#!/usr/bin/env python
# ============================================================
# IBVAP - Intelligent Border Video Analytics Platform
# Main Entry Point
# ============================================================

import sys
import os

# Add src directory to python module resolution path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from analytics.detector import ObjectDetector
from dashboard.app import create_app
from utils.helpers import setup_logging

def main():
    print("=" * 70)
    print("🛡️ IBVAP - Intelligent Border Video Analytics Platform")
    print("=" * 70)
    
    # Setup structured logging
    setup_logging()
    
    # Create and run web dashboard server
    app = create_app()
    print("🚀 Starting Web Dashboard at http://127.0.0.1:5000")
    app.socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()
