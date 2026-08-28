# 🛡️ IBVAP - Intelligent Border Video Analytics Platform

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-green.svg)](https://github.com/ultralytics/ultralytics)
[![Flask](https://img.shields.io/badge/Flask-Web%20Dashboard-orange.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

## Overview
**IBVAP (Intelligent Border Video Analytics Platform)** is an advanced AI-powered computer vision platform designed for real-time surveillance and border security monitoring. Utilizing deep learning models (YOLOv8, MTCNN, PyTorch) and existing CCTV infrastructure, IBVAP provides automated intrusion detection, vehicle tracking, facial analysis, and instant alert dispatching.

---

## 🏗️ Architecture Overview

```
+-----------------------------------------------------------------------+
|                     IBVAP Processing Architecture                      |
+-----------------------------------------------------------------------+
|                                                                       |
|  +------------------+     +------------------+    +-----------------+ |
|  |  CCTV / IP Stream| --> | OpenCV Ingestion | -> | Object Detector | |
|  |  (RTSP/MP4/MPG)  |     | & Frame Buffers  |    |    (YOLOv8)     | |
|  +------------------+     +------------------+    +-----------------+ |
|                                                            |          |
|                                                            v          |
|  +------------------+     +------------------+    +-----------------+ |
|  |  Web Dashboard   | <-- |  Flask SocketIO  | <--| Breach Detection| |
|  |  (HTML5/JS UI)   |     | Stream Engine    |    |  & Alert Logic  | |
|  +------------------+     +------------------+    +-----------------+ |
|                                                                       |
+-----------------------------------------------------------------------+
```

---

## 📁 Project Structure

```text
C:\IBVAP-Demo\
├── main.py                     # Primary platform entry point
├── run.py                      # Interactive Quick-Start CLI menu
├── dashboard.py                # Single-camera legacy dashboard
├── dashboard_dual.py           # Dual-camera legacy dashboard
├── requirements.txt            # Python package dependencies
├── .gitignore                  # Git repository exclusion rules
├── README.md                   # Project documentation
├── src/                        # Modular source code package
│   ├── __init__.py
│   ├── analytics/              # Vision analytics engine
│   │   ├── __init__.py
│   │   └── detector.py         # ObjectDetector (YOLOv8 tracking & alerts)
│   ├── dashboard/              # Web application backend
│   │   ├── __init__.py
│   │   └── app.py              # Flask app factory & streaming handlers
│   └── utils/                  # Utility & helper tools
│       ├── __init__.py
│       └── helpers.py          # Logging configuration & file helpers
├── data/                       # Application data storage
│   ├── videos/                 # Input video recordings & RTSP clips
│   ├── models/                 # Neural network weights (yolov8n.pt, etc.)
│   ├── configs/                # Camera & platform JSON configurations
│   ├── logs/                   # System runtime logs
│   ├── outputs/                # Processed video output files
│   └── alerts/                 # Saved alert snapshots & metadata
├── templates/                  # Web dashboard HTML templates
│   └── dashboard.html
├── static/                     # Web dashboard assets
│   ├── css/
│   ├── js/
│   └── images/
├── docs/                       # Project documentation & specs
└── tests/                      # Unit & integration test suites
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Dependencies
Ensure Python 3.9+ and CUDA (optional, for GPU acceleration) are installed.

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launching IBVAP
Launch the interactive quick-start menu:
```bash
python run.py
```
Or start the main application dashboard directly:
```bash
python main.py
```
Open your web browser and navigate to `http://localhost:5000` to view the live border analytics feed.

---

## 🛠️ Configuration & API Endpoints

- **Camera & Stream Config**: Configurable via `data/configs/camera_config.json`.
- **REST Stats Endpoint**: `GET /api/stats` returns system status and recent breach alerts.
- **MJPEG Live Stream**: `GET /video_feed` streams annotated video frames with real-time bounding boxes and fence breach line.

---

## 🛡️ License
Copyright © 2026 IBVAP Security Systems. All rights reserved.
