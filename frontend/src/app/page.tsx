'use client';

import React, { useState, useEffect } from 'react';
import { TopCommandBar } from '@/components/layout/TopCommandBar';
import { Sidebar, NavItem } from '@/components/layout/Sidebar';
import { BorderMap } from '@/components/map/BorderMap';
import { IncidentPanel } from '@/components/incidents/IncidentPanel';
import { AICorrelationFlow } from '@/components/ai/AICorrelationFlow';
import { AISurveillanceCopilot } from '@/components/ai/AISurveillanceCopilot';
import { ThreatFeed } from '@/components/incidents/ThreatFeed';
import { CameraWall } from '@/components/cctv/CameraWall';
import { DetectionTrend } from '@/components/analytics/DetectionTrend';
import {
  ANPRModule,
  FaceModule,
  BehaviourModule,
  EvidenceVaultModule,
  CameraNetworkModule,
  ArchitectureFlowModule,
  AuditLogsModule,
  SearchModal
} from '@/components/views/SubModules';
import {
  mockMetrics,
  mockCameras,
  mockBorderPosts,
  mockGeofences,
  mockTrackedSubject,
  mockIncidents
} from '@/mock/surveillanceData';
import { IncidentAlert } from '@/types/surveillance';

export default function Home() {
  const [activeView, setActiveView] = useState<NavItem>('overview');
  const [selectedCameraId, setSelectedCameraId] = useState<string>('CAM-042');
  const [incidents, setIncidents] = useState<IncidentAlert[]>(mockIncidents);
  const [currentIncident, setCurrentIncident] = useState<IncidentAlert>(mockIncidents[0]);
  const [copilotSummary, setCopilotSummary] = useState<string>(
    'Ollama Mistral LLM Copilot: Subject P-014 tracked across Sector Alpha (CAM-042). High probability perimeter breach with threat score 91/100. Immediate dispatch to BOP Alpha-07 recommended.'
  );
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const [liveStats, setLiveStats] = useState({
    persons_detected: 0,
    faces_detected: 0,
    vehicles_detected: 0,
    inference_fps: 30.0,
    latency_ms: 10.0,
    active_alerts: 0,
    intrusions: 0
  });

  // Fetch Ollama LLM Copilot assessment from backend API
  const fetchLlmCopilot = async (cam = 'CAM-042 (Sector Alpha)', threatScore = 91) => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/copilot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ camera: cam, threat_score: threatScore })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.copilot_summary) {
          setCopilotSummary(data.copilot_summary);
        }
      }
    } catch (e) {
      console.warn('Ollama Copilot fetch note:', e);
    }
  };

  // Fetch real-time stats from backend
  const fetchRealStats = async () => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/stats');
      if (res.ok) {
        const data = await res.json();
        setLiveStats({
          persons_detected: data.persons_detected ?? 0,
          faces_detected: data.faces_detected ?? (data.persons_detected ?? 0),
          vehicles_detected: data.vehicles_detected ?? 0,
          inference_fps: data.inference_fps ?? 30.0,
          latency_ms: data.latency_ms ?? 10.0,
          active_alerts: data.active_alerts ?? 0,
          intrusions: data.intrusions ?? 0
        });
      }
    } catch (e) {
      // quiet fallback
    }
  };

  useEffect(() => {
    fetchLlmCopilot();
    fetchRealStats();
    const interval = setInterval(fetchRealStats, 3000);
    return () => clearInterval(interval);
  }, []);

  // End-to-End Interactive Simulation Trigger
  const handleRunSimulation = () => {
    setActiveView('overview');
    setSelectedCameraId('CAM-071');
    setCopilotSummary(
      'Ollama Mistral LLM: Simulation Active. Subject P-014 trajectory correlated on CAM-071 top-view pedestrian feed.'
    );

    setTimeout(() => {
      setSelectedCameraId('CAM-042');
      setCurrentIncident({
        ...mockIncidents[0],
        threatScore: 95,
        status: 'NEW'
      });
      fetchLlmCopilot('CAM-042 (Sector Alpha Perimeter)', 95);
    }, 4000);
  };

  const handleAcknowledge = () => {
    setCurrentIncident(prev => ({ ...prev, status: 'INVESTIGATING' }));
    setIncidents(prev =>
      prev.map(i => (i.id === currentIncident.id ? { ...i, status: 'INVESTIGATING' } : i))
    );
    alert(`Incident #${currentIncident.id} Acknowledged. Status updated to INVESTIGATING.`);
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-base text-slate-100">
      {/* Top Header */}
      <TopCommandBar
        metrics={mockMetrics}
        onRunSimulation={handleRunSimulation}
        onOpenSearch={() => setIsSearchOpen(true)}
        onOpenLogin={() => alert('Operator Profile: OP-014 (Level 5 Security Clearance)')}
      />

      {/* Main Workspace */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar Navigation */}
        <Sidebar activeView={activeView} onSelectView={setActiveView} />

        {/* Dynamic Center View Pane */}
        <main className="flex-1 flex flex-col overflow-y-auto p-3 space-y-3">
          {activeView === 'overview' && (
            <>
              {/* Top KPI Strip */}
              <div className="grid grid-cols-8 gap-2 shrink-0">
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">CAMERAS ONLINE</div>
                  <div className="text-base font-mono font-bold text-emerald-400">2 / 2 ACTIVE</div>
                  <div className="text-[9px] text-emerald-400 font-mono">{liveStats.inference_fps} FPS ({Math.round(liveStats.latency_ms)}ms)</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">PERSONS DETECTED</div>
                  <div className="text-base font-mono font-bold text-sky-400">{liveStats.persons_detected} LIVE</div>
                  <div className="text-[9px] text-slate-400 font-mono">Real Inference</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">VEHICLES DETECTED</div>
                  <div className="text-base font-mono font-bold text-blue-400">{liveStats.vehicles_detected} LIVE</div>
                  <div className="text-[9px] text-slate-400 font-mono">Real Inference</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">SECURITY EVENTS</div>
                  <div className="text-base font-mono font-bold text-amber-400">{liveStats.active_alerts}</div>
                  <div className="text-[9px] text-slate-400 font-mono">Live Logged</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">CRITICAL ALERTS</div>
                  <div className="text-base font-mono font-bold text-rose-400">{liveStats.intrusions}</div>
                  <div className="text-[9px] text-rose-400 font-mono">SECTOR ALPHA</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">FACES DETECTED</div>
                  <div className="text-base font-mono font-bold text-purple-400">{liveStats.faces_detected} LIVE</div>
                  <div className="text-[9px] text-purple-400 font-mono">Privacy Blur Active</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">INTRUSIONS</div>
                  <div className="text-base font-mono font-bold text-rose-400">{liveStats.intrusions}</div>
                  <div className="text-[9px] text-rose-400 font-mono">BOUNDARY BREACH</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">OLLAMA LLM</div>
                  <div className="text-base font-mono font-bold text-purple-400">MISTRAL</div>
                  <div className="text-[9px] text-purple-400 font-mono">AI COPILOT ACTIVE</div>
                </div>
              </div>

              {/* Middle Section (65% Map + 35% Intelligence Column) */}
              <div className="grid grid-cols-12 gap-3 h-[500px] shrink-0">
                <div className="col-span-8 h-full">
                  <BorderMap
                    cameras={mockCameras}
                    borderPosts={mockBorderPosts}
                    geofences={mockGeofences}
                    trackedSubject={mockTrackedSubject}
                    selectedCameraId={selectedCameraId}
                    onSelectCamera={setSelectedCameraId}
                  />
                </div>

                <div className="col-span-4 flex flex-col gap-2.5 overflow-y-auto pr-1">
                  <IncidentPanel
                    incident={currentIncident}
                    onAcknowledge={handleAcknowledge}
                    onTrackMap={() => setSelectedCameraId('CAM-042')}
                    onViewEvidence={() => setActiveView('evidence')}
                  />
                  <AICorrelationFlow onOpenFullArchitecture={() => setActiveView('architecture')} />
                  <AISurveillanceCopilot
                    summary={copilotSummary}
                    onTrack={() => alert('Subject P-014 locked on target track list.')}
                    onCorrelate={() => alert('Cross-correlating CAM-042 and CAM-071 feeds...')}
                    onEscalate={() => alert('Incident escalated to Sector Commander.')}
                  />
                </div>
              </div>

              {/* Lower Section (Dual CCTV Wall + Analytics + Threat Feed) */}
              <div className="grid grid-cols-12 gap-3 shrink-0">
                <div className="col-span-7">
                  <CameraWall cameras={mockCameras} onSelectCamera={setSelectedCameraId} />
                </div>
                <div className="col-span-5 flex flex-col gap-3">
                  <DetectionTrend />
                  <ThreatFeed incidents={incidents} />
                </div>
              </div>
            </>
          )}

          {activeView === 'surveillance' && (
            <CameraWall cameras={mockCameras} onSelectCamera={setSelectedCameraId} />
          )}

          {activeView === 'anpr' && <ANPRModule />}
          {activeView === 'face' && <FaceModule />}
          {activeView === 'behaviour' && <BehaviourModule />}
          {activeView === 'evidence' && <EvidenceVaultModule />}
          {activeView === 'cameras' && <CameraNetworkModule />}
          {activeView === 'architecture' && <ArchitectureFlowModule />}
          {activeView === 'audit' && <AuditLogsModule />}
          {activeView === 'system' && <CameraNetworkModule />}
          {activeView === 'detection' && <BehaviourModule />}
          {activeView === 'incidents' && <ThreatFeed incidents={incidents} />}
          {activeView === 'night' && <BehaviourModule />}
          {activeView === 'settings' && <AuditLogsModule />}
        </main>
      </div>

      <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </div>
  );
}
