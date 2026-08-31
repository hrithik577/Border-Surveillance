'use client';

import React, { useState, useEffect } from 'react';
import {
  mockANPR,
  mockFaces,
  mockBehaviour,
  mockEvidence,
  mockAuditLogs
} from '@/mock/surveillanceData';
import { Car, UserCheck, Activity, Moon, AlertTriangle, Lock, Network, Cpu, FileText, Settings, X } from 'lucide-react';

export const ANPRModule: React.FC = () => (
  <div className="p-4 space-y-4">
    <div className="flex items-center gap-2 text-sm font-bold text-slate-100 uppercase tracking-wider">
      <Car className="w-4 h-4 text-amber-400" /> ANPR INTELLIGENCE & WATCHLIST MATCHES
    </div>
    <div className="bg-surface border border-border rounded overflow-hidden">
      <table className="w-full text-left text-xs">
        <thead className="bg-surfaceElevated text-[10px] uppercase text-slate-400 border-b border-border font-mono">
          <tr>
            <th className="p-2.5">Plate Number</th>
            <th className="p-2.5">Vehicle</th>
            <th className="p-2.5">Camera</th>
            <th className="p-2.5">Location</th>
            <th className="p-2.5">Timestamp</th>
            <th className="p-2.5">Confidence</th>
            <th className="p-2.5">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/60 font-mono text-slate-300">
          {mockANPR.map(item => (
            <tr key={item.id} className="hover:bg-surfaceElevated transition-all">
              <td className={`p-2.5 font-bold ${item.flagged ? 'text-amber-400' : 'text-slate-100'}`}>
                {item.plate}
              </td>
              <td className="p-2.5">{item.vehicleType}</td>
              <td className="p-2.5 text-sky-400">{item.camera}</td>
              <td className="p-2.5 text-slate-400">{item.location}</td>
              <td className="p-2.5 text-slate-400">{item.timestamp}</td>
              <td className="p-2.5 text-emerald-400">{item.confidence}%</td>
              <td className="p-2.5">
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    item.flagged
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                      : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                  }`}
                >
                  {item.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export const FaceModule: React.FC = () => {
  const [faceStats, setFaceStats] = useState({
    total_faces_detected: 0,
    current_faces_in_frame: 0,
    captured_faces: [] as any[],
    events: [] as any[]
  });

  useEffect(() => {
    const fetchFaces = async () => {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/faces');
        if (res.ok) {
          const data = await res.json();
          setFaceStats(data);
        }
      } catch (e) {
        // quiet fallback
      }
    };
    fetchFaces();
    const interval = setInterval(fetchFaces, 2000);
    return () => clearInterval(interval);
  }, []);

  const facesList = faceStats.captured_faces && faceStats.captured_faces.length > 0
    ? faceStats.captured_faces
    : [
        {
          face_id: 'FACE-016',
          track_id: 'P-016',
          photo_url: 'http://127.0.0.1:5000/static/faces/FACE-016.jpg',
          confidence: '96%',
          camera: 'CAM-071',
          timestamp: '20:51:32 IST',
          status: 'UNIDENTIFIED'
        },
        {
          face_id: 'FACE-010',
          track_id: 'P-010',
          photo_url: 'http://127.0.0.1:5000/static/faces/FACE-010.jpg',
          confidence: '94%',
          camera: 'CAM-071',
          timestamp: '20:51:30 IST',
          status: 'AUTHORIZED'
        }
      ];

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-bold text-slate-100 uppercase tracking-wider">
          <UserCheck className="w-4 h-4 text-purple-400" /> LIVE FACE INTELLIGENCE & PHOTO CAPTURE VAULT
        </div>
        <span className="px-2.5 py-1 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
          AUTOMATIC PHOTO CAPTURE ACTIVE
        </span>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <div className="bg-surface border border-border p-3 rounded">
          <div className="text-[10px] uppercase text-slate-400 font-bold">TOTAL FACES CAPTURED</div>
          <div className="text-xl font-mono font-bold text-slate-100 mt-1">{faceStats.total_faces_detected || facesList.length}</div>
        </div>
        <div className="bg-surface border border-border p-3 rounded">
          <div className="text-[10px] uppercase text-slate-400 font-bold">FACES IN LIVE FRAME</div>
          <div className="text-xl font-mono font-bold text-purple-400 mt-1">{faceStats.current_faces_in_frame}</div>
        </div>
        <div className="bg-surface border border-border p-3 rounded">
          <div className="text-[10px] uppercase text-slate-400 font-bold">SAVED FACE SNAPSHOTS</div>
          <div className="text-xl font-mono font-bold text-sky-400 mt-1">{facesList.length} PHOTOS</div>
        </div>
        <div className="bg-surface border border-border p-3 rounded">
          <div className="text-[10px] uppercase text-slate-400 font-bold">FACE BLUR STATUS</div>
          <div className="text-xl font-mono font-bold text-emerald-400 mt-1">DISABLED (CLEAR)</div>
        </div>
      </div>

      {/* Captured Face Photo Gallery Cards */}
      <div className="space-y-2">
        <div className="text-[11px] font-bold font-mono text-slate-200 uppercase tracking-wider flex items-center gap-2">
          📸 RECENTLY CAPTURED FACE SNAPSHOTS (REALTIME DISK VAULT)
        </div>
        <div className="grid grid-cols-4 gap-3">
          {facesList.map((item: any) => (
            <div key={item.face_id} className="bg-surface border border-border hover:border-purple-500/60 rounded p-2.5 space-y-2 transition-all group">
              <div className="relative aspect-square bg-black/80 rounded overflow-hidden border border-border flex items-center justify-center">
                <img
                  src={item.photo_url}
                  alt={item.face_id}
                  className="w-full h-full object-cover group-hover:scale-105 transition-all"
                  onError={(e: any) => {
                    e.target.style.display = 'none';
                  }}
                />
                <div className="absolute top-1.5 left-1.5 bg-black/80 text-[9px] font-mono text-purple-300 px-1.5 py-0.5 rounded border border-purple-500/40 font-bold">
                  {item.face_id}
                </div>
                <div className="absolute bottom-1.5 right-1.5 bg-black/80 text-[9px] font-mono text-emerald-400 px-1.5 py-0.5 rounded border border-border font-bold">
                  {item.confidence}
                </div>
              </div>
              <div className="flex items-center justify-between text-[10px] font-mono">
                <span className="text-slate-300 font-bold">{item.track_id}</span>
                <span className="text-slate-400">{item.timestamp}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold border ${
                  item.status === 'AUTHORIZED'
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                    : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                }`}>
                  {item.status}
                </span>
                <span className="text-[9px] font-mono text-slate-400">{item.camera}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Real Face Detection Events Log Table */}
      <div className="bg-surface border border-border rounded overflow-hidden">
        <div className="p-2.5 bg-surfaceElevated border-b border-border text-[11px] font-bold text-slate-200 uppercase font-mono">
          👁️ CAPTURED FACE DATABASE LOG
        </div>
        <table className="w-full text-left text-xs">
          <thead className="bg-base text-[10px] uppercase text-slate-400 border-b border-border font-mono">
            <tr>
              <th className="p-2.5">Face Photo</th>
              <th className="p-2.5">Face ID</th>
              <th className="p-2.5">Subject Track</th>
              <th className="p-2.5">Camera Source</th>
              <th className="p-2.5">Confidence</th>
              <th className="p-2.5">Timestamp</th>
              <th className="p-2.5">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60 font-mono text-slate-300">
            {facesList.map((item: any) => (
              <tr key={item.face_id}>
                <td className="p-2">
                  <img src={item.photo_url} alt={item.face_id} className="w-9 h-9 object-cover rounded border border-purple-500/40" />
                </td>
                <td className="p-2.5 font-bold text-purple-400">{item.face_id}</td>
                <td className="p-2.5 text-slate-200 font-bold">{item.track_id}</td>
                <td className="p-2.5 text-slate-300">{item.camera}</td>
                <td className="p-2.5 text-emerald-400 font-bold">{item.confidence}</td>
                <td className="p-2.5 text-slate-400">{item.timestamp}</td>
                <td className="p-2.5">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                    CAPTURED & SAVED
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const BehaviourModule: React.FC = () => (
  <div className="p-4 space-y-4">
    <div className="flex items-center gap-2 text-sm font-bold text-slate-100 uppercase tracking-wider">
      <Activity className="w-4 h-4 text-purple-400" /> BEHAVIOURAL ANALYTICS & THREAT SCORING
    </div>
    <div className="bg-surface border border-border rounded overflow-hidden">
      <table className="w-full text-left text-xs">
        <thead className="bg-surfaceElevated text-[10px] uppercase text-slate-400 border-b border-border font-mono">
          <tr>
            <th className="p-2.5">Behaviour Event</th>
            <th className="p-2.5">Risk Score</th>
            <th className="p-2.5">Confidence</th>
            <th className="p-2.5">Camera</th>
            <th className="p-2.5">Duration</th>
            <th className="p-2.5">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/60 font-mono text-slate-300">
          {mockBehaviour.map(item => (
            <tr key={item.id}>
              <td className="p-2.5 font-bold font-sans text-slate-200">{item.event}</td>
              <td className="p-2.5">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  {item.riskScore} / 100
                </span>
              </td>
              <td className="p-2.5 text-emerald-400">{item.confidence}%</td>
              <td className="p-2.5 text-sky-400">{item.camera}</td>
              <td className="p-2.5 text-slate-400">{item.duration}</td>
              <td className="p-2.5">
                <button className="px-2 py-1 bg-blue-600/30 text-blue-300 rounded text-[10px] font-bold hover:bg-blue-600/50">
                  REVIEW
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export const EvidenceVaultModule: React.FC = () => (
  <div className="p-4 space-y-4">
    <div className="flex items-center gap-2 text-sm font-bold text-slate-100 uppercase tracking-wider">
      <Lock className="w-4 h-4 text-emerald-400" /> FORENSIC EVIDENCE VAULT & CRYPTOGRAPHIC HASHES
    </div>
    <div className="bg-surface border border-border rounded overflow-hidden">
      <table className="w-full text-left text-xs">
        <thead className="bg-surfaceElevated text-[10px] uppercase text-slate-400 border-b border-border font-mono">
          <tr>
            <th className="p-2.5">Evidence ID</th>
            <th className="p-2.5">Incident ID</th>
            <th className="p-2.5">Camera</th>
            <th className="p-2.5">Location</th>
            <th className="p-2.5">Timestamp</th>
            <th className="p-2.5">SHA-256 Hash</th>
            <th className="p-2.5">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/60 font-mono text-slate-300">
          {mockEvidence.map(item => (
            <tr key={item.id}>
              <td className="p-2.5 text-cyan-400 font-bold">{item.id}</td>
              <td className="p-2.5 text-rose-400">{item.incidentId}</td>
              <td className="p-2.5">{item.camera}</td>
              <td className="p-2.5 text-slate-400">{item.location}</td>
              <td className="p-2.5 text-slate-400">{item.timestamp}</td>
              <td className="p-2.5 text-[10px] text-slate-500 font-mono">{item.hash}</td>
              <td className="p-2.5">
                <button
                  onClick={() => alert(`Exporting signed evidence package for ${item.id}`)}
                  className="px-2 py-1 bg-sky-600/30 text-sky-300 rounded text-[10px] font-bold hover:bg-sky-600/50"
                >
                  EXPORT PKG
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export const CameraNetworkModule: React.FC = () => (
  <div className="p-4 space-y-4">
    <div className="flex items-center gap-2 text-sm font-bold text-slate-100 uppercase tracking-wider">
      <Network className="w-4 h-4 text-sky-400" /> CCTV NETWORK TOPOLOGY & HEALTH
    </div>
    <div className="bg-surface border border-border p-4 rounded space-y-3">
      <div className="flex justify-between font-mono text-xs">
        <span>CAMERAS ONLINE: <strong className="text-emerald-400">247</strong></span>
        <span>DEGRADED: <strong className="text-amber-400">4</strong></span>
        <span>OFFLINE: <strong className="text-rose-400">8</strong></span>
      </div>
      <div className="p-3 bg-base border border-border rounded text-xs text-slate-400 font-mono">
        RTSP Streams ➔ Video Ingestion Gateway ➔ Central AI Perception ➔ Threat Fusion Engine ➔ Ollama LLM ➔ Command Center
      </div>
    </div>
  </div>
);

import { SystemArchitectureFlow } from '@/components/ai/SystemArchitectureFlow';

export const ArchitectureFlowModule: React.FC = () => (
  <div className="h-full">
    <SystemArchitectureFlow />
  </div>
);

export const AuditLogsModule: React.FC = () => (
  <div className="p-4 space-y-4">
    <div className="flex items-center gap-2 text-sm font-bold text-slate-100 uppercase tracking-wider">
      <FileText className="w-4 h-4 text-slate-400" /> ENTERPRISE AUDIT LOGS
    </div>
    <div className="bg-surface border border-border rounded overflow-hidden">
      <table className="w-full text-left text-xs">
        <thead className="bg-surfaceElevated text-[10px] uppercase text-slate-400 border-b border-border font-mono">
          <tr>
            <th className="p-2.5">Timestamp</th>
            <th className="p-2.5">Operator</th>
            <th className="p-2.5">Action</th>
            <th className="p-2.5">Resource</th>
            <th className="p-2.5">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/60 font-mono text-slate-300">
          {mockAuditLogs.map(log => (
            <tr key={log.id}>
              <td className="p-2.5 text-slate-400">{log.timestamp}</td>
              <td className="p-2.5 text-cyan-400 font-bold">{log.operator}</td>
              <td className="p-2.5 font-sans">{log.action}</td>
              <td className="p-2.5 text-slate-300">{log.resource}</td>
              <td className="p-2.5">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  {log.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export const SearchModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose
}) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-surface border border-border rounded-md w-full max-w-lg p-4 space-y-3 shadow-2xl">
        <div className="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-slate-100">
          <span>🔍 GLOBAL COMMAND SEARCH</span>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
        <input
          type="text"
          placeholder="Search Camera ID, Border Post, Incident ID, License Plate..."
          className="w-full bg-base border border-border p-2.5 rounded text-xs text-white focus:outline-none focus:border-sky-500 font-mono"
          autoFocus
        />
        <div className="flex justify-end">
          <button onClick={onClose} className="px-3 py-1.5 bg-surfaceElevated border border-border text-xs text-slate-300 rounded">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
