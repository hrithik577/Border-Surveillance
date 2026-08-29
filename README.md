# 🛡️ IBVAP — Intelligent Border Video Analytics Platform

[![SIH26-26187](https://img.shields.io/badge/SIH26-26187-blue.svg?style=for-the-badge&logo=shield)](https://github.com/hrithik577/Border-Surveillance)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript%205-blue.svg?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Backend-Python%203.12-3776AB.svg?style=for-the-badge&logo=python)](https://python.org)
[![PyTorch](https://img.shields.io/badge/AI Engine-PyTorch%20%2B%20YOLOv8-EE4C2C.svg?style=for-the-badge&logo=pytorch)](https://pytorch.org)
[![MapLibre](https://img.shields.io/badge/GIS-MapLibre%20GL%20JS-FF6600.svg?style=for-the-badge&logo=maplibre)](https://maplibre.org)

> **SIH26-26187**: *AI-Based Intelligent Video Analytics Platform for Border Surveillance Using Existing CCTV Infrastructure.*

**IBVAP** is a defence-grade, production-quality C4ISR command-and-control operations platform designed to transform standard IP-based CCTV infrastructure into an intelligent border surveillance network. It combines real-time computer vision, geospatial intelligence (GIS), multi-camera tracking, behaviour analytics, ANPR, intrusion detection, night surveillance, and forensic incident management into a single, cohesive situational awareness console.

---

## 🎯 Core Value Proposition & Intelligence Pipeline

Instead of acting as a conventional passive CCTV viewer, IBVAP visually communicates an end-to-end intelligence pipeline:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  CCTV INPUT  │ ──> │ AI PERCEPT   │ ──> │   TRACKING   │ ──> │ SPATIAL CORRELATION │
│ Existing IP  │     │ YOLOv8 Model │     │  ByteTrack   │     │   GIS Coordinates   │
└──────────────┘     └──────────────┘     └──────────────┘     └─────────────────────┘
                                                                          │
┌──────────────┐     ┌──────────────┐     ┌──────────────┐                ▼
│   EVIDENCE   │ <── │   RESPONSE   │ <── │ ALERT ENGINE │ <── ┌─────────────────────┐
│ SHA-256 Vault│     │ Operator Cmd │     │ Threat > 90  │     │ BEHAVIOUR ANALYTICS │
└──────────────┘     └──────────────┘     └──────────────┘     │ Boundary Breach     │
                                                               └─────────────────────┘
```

---

## ⚡ Signature Features

### 1. 🛰️ Central Interactive GIS Situational Map
- **MapLibre GL JS Engine**: Dark vector/raster GIS basemap (CartoDB Dark Matter).
- **Tactical Overlays**: Dotted red national border perimeter line, Border Outposts (BOP Alpha-07, BOP Charlie-03, etc.), camera nodes with directional field-of-view (FOV) cones, virtual geofence polygons (Restricted Zone A), and patrol routes.
- **Cross-Camera Trajectory Tracing**: Real-time movement pathing for tracked subject **P-014** across camera sectors (`CAM-039` ➔ `CAM-041` ➔ `CAM-042` ➔ Restricted Zone A Breach).
- **Bidirectional GIS Interactivity**: Clicking a camera centers the map and displays stream stats; clicking an incident highlights spatial trajectory and opens the Critical Incident Decision Panel.

### 2. 🤖 AI Event Correlation Pipeline & Copilot Console
- **6-Step Signal Pipeline**: Visualizes correlation flow (`PERSON DETECTED` ➔ `TRACK ESTABLISHED` ➔ `GEOFENCE PROXIMITY` ➔ `BOUNDARY CROSSING` ➔ `CROSS-CAMERA CORRELATION` ➔ `THREAT SCORE 91` ➔ `CRITICAL ALERT`).
- **AI Surveillance Copilot**: Intelligence console outputting real-time security assessments and system recommendations (`TRACK`, `CORRELATE`, `ESCALATE`, `VIEW EVIDENCE`).

### 3. 📹 Dual Streaming & HD Video Engine
- **Direct HD MP4 Mode**: Serves uncompressed, crystal-clear 1080p/720p HD MP4 video streams directly to HTML5 video elements with high-precision SVG overlay bounding boxes.
- **AI MJPEG Overlay Mode**: Serves 98% high-definition JPEG streams encoded with OpenCV, featuring thin 1px/2px C4ISR bounding boxes, tracking labels (`P-014 | PERSON | 96%`), and virtual border line overlays.
- **Continuous Infinite Looping**: Automatic capture re-instantiation on EOF (End of File) ensuring video feeds run 24/7 without freezing.

### 4. ⚡ End-to-End Incident Simulation Mode
- Click the **`⚡ RUN SIMULATION MODE`** button in the header to execute an automated 12-second breach scenario:
  1. Map pans to Sector Alpha.
  2. Subject P-014 trajectory animates from `CAM-039` ➔ `CAM-041` ➔ `CAM-042`.
  3. Geofence boundary turns **RED** (`BREACH DETECTED`).
  4. Threat Score escalates to `95 / 100` (`CRITICAL ALERT #IBV-240184`).
  5. AI Copilot recommends immediate patrol dispatch.
  6. Operator clicks **ACKNOWLEDGE** ➔ Status transitions to `INVESTIGATING`.

### 5. 🎛️ Multi-Module Operations Suite
- **ANPR Intelligence**: License plate recognition log, vehicle classifications, and watchlist match alerts (`KA05XY7821`).
- **Facial Analytics**: Authorized vs. unknown subject counts and review triggers.
- **Behaviour Analytics**: Loitering detection, wrong-direction movement, and risk scoring.
- **Night IR Surveillance**: Low-light infrared telemetry and movement anomaly timeline.
- **Incident Center**: Full incident lifecycle management (`NEW` ➔ `ACKNOWLEDGED` ➔ `INVESTIGATING` ➔ `DISPATCHED` ➔ `RESOLVED`).
- **Forensic Evidence Vault**: Encrypted evidence package storage with SHA-256 cryptographic hashes and lock/export controls.
- **Camera Network & Infrastructure Topology**: Node status breakdown (`247 Online`, `4 Degraded`, `8 Offline`) and hardware telemetry.
- **Audit Logs**: Enterprise audit table tracking operator actions and resource modifications.

---

## 📂 Repository Directory Layout

```text
Border-Surveillance/
├── main.py                     # Entry point for Flask + SocketIO analytics backend
├── run.py                      # Interactive CLI launcher menu
├── requirements.txt            # Python dependencies
├── src/                        # Core Python backend modules
│   ├── analytics/
│   │   └── detector.py         # YOLOv8 object detector & precision bounding box engine
│   ├── dashboard/
│   │   └── app.py              # Flask app factory, REST endpoints, and video stream generators
│   └── utils/
│       ├── helpers.py          # Model and video path resolvers
│       └── llm_integration.py  # Local Ollama (Mistral) security report generator
├── templates/
│   └── dashboard.html          # Secondary Flask HTML dashboard template
├── frontend/                   # Standalone Next.js 14 C4ISR Operations Application
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx      # Root layout with IBM Plex & JetBrains Mono fonts
│   │   │   ├── page.tsx        # Main C4ISR Command Center Dashboard
│   │   │   └── globals.css     # Dark graphite visual theme styles
│   │   ├── components/
│   │   │   ├── layout/         # TopCommandBar.tsx, Sidebar.tsx
│   │   │   ├── map/            # BorderMap.tsx (MapLibre GL JS GIS Component)
│   │   │   ├── cctv/           # CameraWall.tsx (8-Channel Matrix Grid)
│   │   │   ├── incidents/      # IncidentPanel.tsx, ThreatFeed.tsx
│   │   │   ├── ai/             # AISurveillanceCopilot.tsx, AICorrelationFlow.tsx
│   │   │   ├── analytics/      # DetectionTrend.tsx (Recharts Line Chart)
│   │   │   └── views/          # SubModules.tsx (ANPR, Face, Behaviour, Evidence, Audit)
│   │   ├── types/
│   │   │   └── surveillance.ts # Strict TypeScript domain interfaces
│   │   ├── mock/
│   │   │   └── surveillanceData.ts # Synthetic GIS coordinates & telemetry mock data
│   │   └── services/
│   │       └── websocket.ts    # Typed WebSocket event emitter service
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
└── data/
    ├── models/                 # Model weights (yolov8n.pt)
    └── videos/                 # Sample CCTV footage (VIRAT_S_000001.mp4, top_view_pedestrian.mp4)
```

---

## 🚀 Quick Setup & Installation Guide

### Prerequisites
- **Python**: 3.12+
- **Node.js**: 18+ (npm 10+)
- **OS**: Windows / Linux / macOS

---

### Step 1: Environment Setup & Python Backend

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hrithik577/Border-Surveillance.git
   cd Border-Surveillance
   ```

2. **Create and activate a Python virtual environment**:
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Flask Analytics Server**:
   ```bash
   python main.py
   ```
   *The Flask backend server will run at `http://127.0.0.1:5000`*

---

### Step 2: Next.js C4ISR Frontend Setup

1. **Navigate to the `frontend/` directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Build and start the Next.js production server**:
   ```bash
   npm run build
   npm run start
   ```
   *The Next.js C4ISR Operations Dashboard will run at **[http://localhost:3000](http://localhost:3000)**.*

---

## 🌐 REST API Specifications

The Flask backend provides RESTful endpoints consumed by the command center interface:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/stats` | `GET` | Returns real-time system metrics, camera counts, and active alerts |
| `/api/alerts` | `GET` | Returns active security alerts and threat scores |
| `/api/anpr` | `GET` | Returns ANPR license plate detections and watchlist correlations |
| `/api/faces` | `GET` | Returns facial recognition log and authorization status |
| `/api/behaviour` | `GET` | Returns loitering, wrong-direction, and crowd formation events |
| `/api/evidence` | `GET` | Returns forensic evidence records and SHA-256 cryptographic hashes |
| `/api/audit` | `GET` | Returns system audit logs and operator action history |
| `/video_feed/<cam_id>` | `GET` | MJPEG video stream with high-definition 98% JPEG quality & YOLO annotations |
| `/direct_video/<cam_id>` | `GET` | Uncompressed direct MP4 video file stream for crystal-clear HD playback |

---

## 💻 Hardware & GPU Acceleration

IBVAP automatically detects available hardware acceleration:
- **NVIDIA CUDA**: Tested and compatible with PyTorch CUDA kernel acceleration (including NVIDIA GeForce RTX 50-series / 40-series / 30-series GPUs).
- **CPU Fallback**: Graceful fallback to CPU inference if CUDA kernels are unavailable, ensuring 100% execution stability across any environment.

---

## 📜 License & Project Metadata

- **SIH Problem Statement**: SIH26-26187
- **Repository**: [https://github.com/hrithik577/Border-Surveillance](https://github.com/hrithik577/Border-Surveillance)
- **License**: MIT License
