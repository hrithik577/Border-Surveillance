#!/usr/bin/env python
# ============================================================
# IBVAP - Interactive Quick Start Launcher
# ============================================================

import subprocess
import sys
import os

def main():
    print("=" * 65)
    print("🛡️  IBVAP - Intelligent Border Video Analytics Platform Launcher")
    print("=" * 65)
    print(" 1. Launch Primary Web Dashboard (main.py)")
    print(" 2. Launch Command Center Dashboard (scripts/standalone/command_center.py)")
    print(" 3. Launch Single-Camera Dashboard (scripts/standalone/dashboard.py)")
    print(" 4. Launch Dual-Camera Dashboard (scripts/standalone/dashboard_dual.py)")
    print(" 5. Launch Direct Video Processing (scripts/standalone/ibvap_direct.py)")
    print(" 6. Run Detection Test Suite (scripts/tests/detection_test.py)")
    print(" 7. Exit")
    print("=" * 65)

    try:
        choice = input("Select option (1-7): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        return

    # Target Python 3.11 with PyTorch 2.11.0+cu128 CUDA 12.8
    py311_path = r"C:\Users\bhrit\AppData\Local\Programs\Python\Python311\python.exe"
    py_exec = py311_path if os.path.exists(py311_path) else sys.executable

    if choice == '1':
        os.system(f'"{py_exec}" main.py')
    elif choice == '2':
        os.system(f'"{py_exec}" scripts/standalone/command_center.py')
    elif choice == '3':
        os.system(f'"{py_exec}" scripts/standalone/dashboard.py')
    elif choice == '4':
        os.system(f'"{py_exec}" scripts/standalone/dashboard_dual.py')
    elif choice == '5':
        os.system(f'"{py_exec}" scripts/standalone/ibvap_direct.py')
    elif choice == '6':
        os.system(f'"{py_exec}" scripts/tests/detection_test.py')
    else:
        print("Exiting IBVAP Launcher...")


if __name__ == '__main__':
    main()
