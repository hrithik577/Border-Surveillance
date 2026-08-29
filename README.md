# 🛡️ IBVAP — Intelligent Border Video Analytics Platform

[![SIH26-26187](https://img.shields.io/badge/SIH26-26187-blue.svg)](https://github.com/hrithik577/Border-Surveillance)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Backend-Python%203.12-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/AI-PyTorch%20%2B%20YOLOv8-red.svg)](https://pytorch.org)
[![GIS](https://img.shields.io/badge/GIS-MapLibre%20GL%20JS-orange.svg)](https://maplibre.org)

**SIH26-26187**: *AI-Based Intelligent Video Analytics Platform for Border Surveillance using Existing CCTV Infrastructure.*

IBVAP transforms existing IP-based CCTV infrastructure into a coordinated, AI-powered border surveillance network using computer vision, geospatial intelligence, object tracking, behaviour analytics, ANPR, intrusion detection, and real-time incident management.

---

## 🌟 Core Perception & Decision Pipeline

```
EXISTING CCTV ➔ AI PERCEPTION ➔ TRACKING ➔ SPATIAL CORRELATION ➔ BEHAVIOUR ANALYSIS ➔ THREAT SCORING ➔ REAL-TIME ALERT ➔ RESPONSE ➔ EVIDENCE
```

---

## 📐 Repository Structure

```text
Border-Surveillance/
├── main.py                     # Primary Flask + SocketIO analytics server entrypoint
├── run.py                      # Interactive CLI launcher menu
├── requirements.txt            # Python dependencies
├── src/                        # Core Python application logic
│   ├── analytics/              # YOLOv8 object detector & tracking engine
│   ├── dashboard/              # Flask application factory & REST endpoints
│   └── utils/                  # Path resolvers, logging, and LLM integrations
├── templates/                  # Flask HTML template (dashboard.html)
├── frontend/                   # Standalone Next.js 14 + TypeScript C4ISR Operations App
│   ├── src/
│   │   ├── app/                # Next.js App Router (layout.tsx, page.tsx)
│   │   ├── components/         # C4ISR UI components (Map, CCTV Wall, Copilot, Correlation)
│   │   ├── types/              # Strict TypeScript domain interfaces
│   │   └── mock/               # Synthetic GIS nodes, cameras, and incident telemetry
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
├── data/
│   ├── models/                 # Neural network model weights (yolov8n.pt)
│   └── videos/                 # CCTV sample video feeds
└── scripts/                    # Standalone & diagnostic test scripts
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: 3.12+
- **Node.js**: 18+ (for Next.js frontend)
- **Virtual Environment**: `.venv`

### 2. Launch the AI Analytics Server (Flask Backend)
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Launch Flask Web Server
python main.py
```
*Server runs at `http://127.0.0.1:5000`*

### 3. Launch the Next.js C4ISR Operations Dashboard (Frontend)
```powershell
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Run Next.js production server
npm run build
npm run start
```
*C4ISR Command Center runs at `http://localhost:3000`*

---

## 🛡️ Feature Overview

- **MapLibre GL JS GIS Engine**: Interactive dark GIS basemap rendering tactical border lines, border outposts (BOPs), virtual geofences, camera FOV cones, and live subject **P-014** movement trajectories.
- **AI Event Correlation Pipeline**: 6-step signal pipeline linking raw YOLO detections to spatial pathing, boundary breaches, and threat score calculations.
- **AI Surveillance Copilot**: Intelligence console outputting real-time security assessments and system action recommendations (`TRACK`, `CORRELATE`, `ESCALATE`).
- **High-Density CCTV Wall**: 8-channel live video feed matrix with thin bounding box telemetry overlays.
- **Interactive Simulation Mode**: Header button executing an automated 12-second incident breach scenario across the map, camera wall, copilot, and evidence vault simultaneously.
- **Multi-Module Navigation**: Dedicated views for ANPR watchlist intelligence, Face analytics, Behaviour analytics, Night IR surveillance, Incident center, Forensic Evidence Vault (SHA-256 integrity hashes), Camera Network, System Health, and Audit Logs.

---

## 📄 License
MIT License. Developed for SIH26-26187.
