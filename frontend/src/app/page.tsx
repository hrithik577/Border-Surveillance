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

  useEffect(() => {
    fetchLlmCopilot();
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
                  <div className="text-[9px] text-slate-400 font-mono">100% OPERATIONAL</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">PERSONS DETECTED</div>
                  <div className="text-base font-mono font-bold text-sky-400">1,284</div>
                  <div className="text-[9px] text-slate-400 font-mono">+12.1% vs 24h</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">VEHICLES DETECTED</div>
                  <div className="text-base font-mono font-bold text-blue-400">437</div>
                  <div className="text-[9px] text-slate-400 font-mono">-3.5% vs 24h</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">SECURITY EVENTS</div>
                  <div className="text-base font-mono font-bold text-amber-400">23</div>
                  <div className="text-[9px] text-slate-400 font-mono">+4 events</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">CRITICAL ALERTS</div>
                  <div className="text-base font-mono font-bold text-rose-400">4</div>
                  <div className="text-[9px] text-rose-400 font-mono">SECTOR ALPHA</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">ANPR MATCHES</div>
                  <div className="text-base font-mono font-bold text-slate-100">17</div>
                  <div className="text-[9px] text-amber-400 font-mono">1 REVIEW REQ</div>
                </div>
                <div className="bg-surface border border-border p-2 rounded flex flex-col justify-between">
                  <div className="text-[9px] text-slate-400 font-bold uppercase">INTRUSIONS</div>
                  <div className="text-base font-mono font-bold text-rose-400">6</div>
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
                  <AICorrelationFlow />
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
