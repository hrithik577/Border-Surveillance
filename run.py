#!/usr/bin/env python
# ============================================================
# IBVAP - Interactive Quick Start Launcher
# ============================================================

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("🛡️ IBVAP - Quick Start Launcher")
    print("=" * 60)
    print("1. Launch Main Platform Dashboard (main.py)")
    print("2. Launch Single Camera Dashboard (dashboard.py)")
    print("3. Launch Dual Camera Dashboard (dashboard_dual.py)")
    print("4. Launch Direct Video Processing (ibvap_direct.py)")
    print("5. Exit")
    print("=" * 60)

    try:
        choice = input("Select option (1-5): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        return

    if choice == '1':
        os.system(f"{sys.executable} main.py")
    elif choice == '2':
        os.system(f"{sys.executable} dashboard.py")
    elif choice == '3':
        os.system(f"{sys.executable} dashboard_dual.py")
    elif choice == '4':
        os.system(f"{sys.executable} ibvap_direct.py")
    else:
        print("Exiting IBVAP Launcher...")

if __name__ == '__main__':
    main()
