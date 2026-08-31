import sys
import os
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

# Target Python 3.11 with PyTorch 2.11.0+cu128 CUDA 12.8 (RTX 5050)
target_python = r"C:\Users\bhrit\AppData\Local\Programs\Python\Python311\python.exe"
if os.path.exists(target_python) and not os.environ.get("IBVAP_PY311_ACTIVE"):
    if os.path.normcase(os.path.realpath(sys.executable)) != os.path.normcase(os.path.realpath(target_python)):
        os.environ["IBVAP_PY311_ACTIVE"] = "1"
        os.execv(target_python, [target_python] + sys.argv)

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
