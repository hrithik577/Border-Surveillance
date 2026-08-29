# 🛡️ IBVAP — Intelligent Border Video Analytics Platform

[![SIH26-26187](https://img.shields.io/badge/SIH26-26187-blue.svg?style=for-the-badge&logo=shield)](https://github.com/hrithik577/Border-Surveillance)
[![Ollama LLM](https://img.shields.io/badge/Ollama-Mistral%20LLM-purple.svg?style=for-the-badge&logo=ollama)](https://ollama.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript%205-blue.svg?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org)
[![PyTorch](https://img.shields.io/badge/AI Engine-PyTorch%20%2B%20YOLOv8-EE4C2C.svg?style=for-the-badge&logo=pytorch)](https://pytorch.org)
[![MapLibre](https://img.shields.io/badge/GIS-MapLibre%20GL%20JS-FF6600.svg?style=for-the-badge&logo=maplibre)](https://maplibre.org)

> **SIH26-26187**: *AI-Based Intelligent Video Analytics Platform for Border Surveillance Using Existing CCTV Infrastructure.*

**IBVAP** is a world-class, defence-grade C4ISR command-and-control platform designed to transform standard IP-based CCTV infrastructure into an intelligent, autonomous border surveillance network. Powered by local **Ollama (Mistral LLM)**, real-time YOLOv8 computer vision, geospatial intelligence (GIS), and multi-camera tracking, IBVAP provides real-time threat intelligence and automated incident response.

---

## 🛰️ IP Camera & RTSP Infrastructure Integration — *Why IP Cameras Make IBVAP Advanced & Scalable*

IBVAP is built natively to ingest live **RTSP (Real-Time Streaming Protocol)** video streams from existing security CCTV networks (`rtsp://admin:pass@ip:port/stream`):

```text
┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│ EXISTING IP CCTV CAMERA │ ───> │ EDGE AI COMPUTE NODE    │ ───> │ C4ISR COMMAND CENTER    │
│ RTSP H.264 / H.265 Feed │      │ PyTorch + YOLOv8 + LLM  │      │ Next.js MapLibre Dashboard│
└─────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

### Key Advantages of IP Camera Integration:
- **Zero New Hardware Costs**: Leverages thousands of pre-deployed border IP cameras and checkpost surveillance units without requiring expensive proprietary hardware overhauls.
- **ONVIF & PTZ Auto-Tracking**: Supports ONVIF protocols for automated Pan-Tilt-Zoom (PTZ) optical camera alignment upon boundary breach detection.
- **Edge Compute Scalability**: Decoupled architecture allows edge AI nodes (NVIDIA Jetson / RTX edge servers) to process multi-channel RTSP streams locally before relaying threat events to the central C4ISR command center.
- **High-Definition Stream Stability**: Hardware H.264/H.265 video decoding guarantees 1080p 60FPS uncompressed video transmission with minimal network latency (< 31 ms).

---

## 🧠 Local Ollama Mistral LLM Intelligence Copilot

IBVAP integrates a local **Ollama Mistral LLM** (`mistral:latest`) intelligence engine that processes real-time scene detections, spatial pathing, and threat scores to generate natural-language security assessments and tactical recommendations:

```json
{
  "camera": "CAM-042 (Sector Alpha Perimeter)",
  "threat_score": 95,
  "copilot_summary": "CRITICAL ALERT: Subject P-014 crossed Restricted Zone A border perimeter line. High breach probability. Recommend immediate patrol team dispatch to BOP Alpha-07."
}
```

---

## 📹 Dual Primary CCTV Video Channels

For maximum clarity and performance during operation and demonstration, IBVAP features 2 primary high-definition CCTV video channels with instant **Direct HD MP4 Mode** and **AI MJPEG Overlay Mode**:

1. **`CAM-042` — BOP ALPHA-07 Perimeter Feed**: Real-time border perimeter surveillance with virtual border line breach tracking (`VIRAT_S_000001.mp4`).
2. **`CAM-071` — Top-View Pedestrian Surveillance**: Overhead tactical pedestrian movement and crowd density analytics (`top_view_pedestrian.mp4`).

---

## ⚡ Quick Setup & Running Guide

### 1. Start the Flask Backend & Ollama Intelligence Server
```powershell
# Activate Python Virtual Environment
.\.venv\Scripts\Activate.ps1

# Launch Backend Server with Ollama LLM API
python main.py
```
*Backend runs at `http://127.0.0.1:5000`*

### 2. Start the Next.js C4ISR Operations Dashboard
```powershell
cd frontend
npm run build
npm run start
```
*C4ISR Dashboard runs at **[http://localhost:3000](http://localhost:3000)**.*

---

## 📜 License
MIT License. Developed for SIH26-26187.
