# 🛡️ IBVAP - Intelligent Border Video Analytics Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-000000.svg?style=flat)](https://github.com/ultralytics/ultralytics)
[![Flask](https://img.shields.io/badge/Flask-Web%20Dashboard-000000.svg?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SocketIO](https://img.shields.io/badge/SocketIO-Realtime%20Stream-010101.svg?style=flat&logo=socketdotio&logoColor=white)](https://flask-socketio.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📌 Overview

**IBVAP (Intelligent Border Video Analytics Platform)** is an enterprise-grade AI-powered computer vision platform designed for real-time surveillance, automated border perimeter breach detection, and video stream analytics.

By leveraging state-of-the-art deep learning vision models (**YOLOv8**, **MTCNN**, **EasyOCR**) alongside optional local LLM scene analysis (**Ollama/Mistral**), IBVAP transforms existing CCTV and RTSP security camera networks into intelligent, autonomous perimeter security systems.

---

## 🏗️ System Architecture

```text
+-----------------------------------------------------------------------+
|                     IBVAP Processing Architecture                     |
+-----------------------------------------------------------------------+
|                                                                       |
|  +------------------+     +------------------+    +-----------------+ |
|  | CCTV / RTSP Stream| --> | OpenCV Ingestion | -> | Object Detector | |
|  |  (RTSP/MP4/MPG)  |     | & Frame Buffers  |    |    (YOLOv8)     | |
|  +------------------+     +------------------+    +-----------------+ |
|                                                            |          |
|                                                            v          |
|  +------------------+     +------------------+    +-----------------+ |
|  |  Web Dashboard   | <-- |  Flask SocketIO  | <--| Breach Detection| |
|  |  (HTML5/JS UI)   |     | Stream Engine    |    |  & Alert Logic  | |
|  +------------------+     +------------------+    +-----------------+ |
|                                                            |          |
|                                                            v          |
|                                                   +-----------------+ |
|                                                   | Local LLM (Ollama)|
|                                                   |  Scene Analytics | |
|                                                   +-----------------+ |
+-----------------------------------------------------------------------+
```

---

## 📁 Repository Structure

```text
Border-Surveillance/
├── main.py                     # Primary platform entry point (Web Server)
├── run.py                      # Interactive Quick-Start CLI menu
├── requirements.txt            # Python package dependencies
├── .gitignore                  # Git repository exclusion rules
├── README.md                   # Project documentation
│
├── src/                        # Core modular application package
│   ├── __init__.py
│   ├── analytics/              # Vision analytics engine
│   │   ├── __init__.py
│   │   └── detector.py         # ObjectDetector (YOLOv8 tracking & alerts)
│   ├── dashboard/              # Web application backend
│   │   ├── __init__.py
│   │   └── app.py              # Flask & SocketIO streaming handlers
│   └── utils/                  # Utility & helper tools
│       ├── __init__.py
│       ├── helpers.py          # Logging configuration & path resolvers
│       └── llm_integration.py  # Ollama / Mistral AI scene analytics
│
├── scripts/                    # Scripts & standalone variants
│   ├── standalone/             # Standalone & specialized dashboards
│   │   ├── command_center.py   # High-density Command Center dashboard
│   │   ├── dashboard.py        # Single-camera legacy dashboard
│   │   ├── dashboard_dual.py   # Dual-camera legacy dashboard
│   │   ├── dashboard_gpu.py    # GPU accelerated dashboard
│   │   ├── dashboard_llm.py    # LLM-assisted dashboard
│   │   └── ibvap_direct.py     # Direct OpenCV video stream window
│   └── tests/                  # Test suites & diagnostic utilities
│       ├── detection_test.py   # YOLOv8 object detection benchmark
│       ├── test_llm.py         # Ollama LLM integration diagnostic
│       └── test_rtsp.py        # RTSP camera feed connectivity test
│
├── data/                       # Application data & model artifacts
│   ├── configs/                # Camera & platform JSON configurations
│   ├── logs/                   # System runtime logs (ibvap.log)
│   ├── models/                 # Neural network weights (yolov8n.pt)
│   ├── outputs/                # Processed video recordings
│   └── videos/                 # Input video recordings & test clips
│
└── templates/                  # Web dashboard HTML templates
    ├── dashboard.html          # Standard web dashboard
    ├── command_center.html     # Multi-camera command center layout
    └── redesigned.html         # Modernized telemetry interface
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: 3.9 or higher
- **GPU (Optional)**: NVIDIA GPU with CUDA support for accelerated inference
- **Ollama (Optional)**: For local AI scene descriptions (`ollama pull mistral`)

### 2. Environment Setup & Installation

Clone the repository and install dependencies:

```bash
# Clone the repository
git clone https://github.com/hrithik577/Border-Surveillance.git
cd Border-Surveillance

# Create and activate a virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Running IBVAP

#### Option A: Quick-Start Interactive Menu
Launch the interactive CLI menu to select from available dashboards and diagnostic tools:
```bash
python run.py
```

#### Option B: Primary Web Dashboard
Launch the primary web dashboard directly:
```bash
python main.py
```
Open your browser and navigate to **`http://127.0.0.1:5000`**.

---

## ✨ Key Features

- **Real-Time Object Tracking & Analytics**: Uses YOLOv8 to track pedestrians, vehicles, and unauthorized intrusions at high FPS.
- **Virtual Border Fence Alerts**: Configurable virtual boundary lines with instant alert triggering on perimeter breaches.
- **Multi-Camera & Dual Feed Support**: Stream multiple RTSP / MP4 camera feeds simultaneously via MJPEG and WebSockets.
- **AI Scene Summarization (LLM)**: Integrates with local Ollama/Mistral models to generate automated plain-text incident reports.
- **Modular & Extensible Layout**: Clean separation of core analytics (`src/analytics`), web server (`src/dashboard`), and standalone utilities (`scripts/`).

---

## 🛠️ API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Main Web Telemetry Dashboard |
| `/video_feed` | `GET` | Live MJPEG Video Stream with analytical overlays |
| `/api/stats` | `GET` | Real-time system stats, count metrics, and alert history |
| `/api/alerts` | `GET` | List of active breach alerts and timestamps |

---

## 🛡️ License

Copyright © 2026 IBVAP Security Systems. Released under the [MIT License](LICENSE).
