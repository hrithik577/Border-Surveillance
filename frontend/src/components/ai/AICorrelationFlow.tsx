'use client';

import React from 'react';
import { Workflow, ArrowRight } from 'lucide-react';

interface AICorrelationFlowProps {
  onOpenFullArchitecture?: () => void;
}

export const AICorrelationFlow: React.FC<AICorrelationFlowProps> = ({ onOpenFullArchitecture }) => {
  const steps = [
    { num: '01', title: 'VIDEO INGESTION & BUFFER', detail: 'RTSP IP Cameras ➔ Redis Stream Queue' },
    { num: '02', title: 'CENTRAL AI PERCEPTION', detail: 'YOLOv8 BBoxes • Person P-014 Detected' },
    { num: '03', title: 'TRACKING & GEOFENCING', detail: 'ByteTrack Persistent ID • Restricted Zone A' },
    { num: '04', title: 'CROSS-CAM & INTEL FUSION', detail: 'Watchlist Match + Multi-Cam Handoff', active: true },
    { num: '05', title: 'THREAT FUSION ENGINE', detail: 'Multi-Signal Scoring: 95/100 (Critical)', active: true },
    { num: '06', title: 'OLLAMA LLM & DISPATCH', detail: 'Mistral Assessment ➔ Command Center & MLOps', active: true }
  ];

  return (
    <div className="bg-surface border border-border rounded p-3 space-y-2 shrink-0 shadow-md">
      <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-wider text-slate-300">
        <div className="flex items-center gap-1.5">
          <Workflow className="w-3.5 h-3.5 text-sky-400" />
          <span>AI MULTI-SIGNAL ARCHITECTURE PIPELINE</span>
        </div>
        {onOpenFullArchitecture && (
          <button
            onClick={onOpenFullArchitecture}
            className="text-[9px] text-sky-400 hover:text-sky-300 font-mono font-bold flex items-center gap-1 hover:underline"
          >
            FULL FLOW <ArrowRight className="w-3 h-3" />
          </button>
        )}
      </div>
      <div className="space-y-1.5">
        {steps.map(step => (
          <div
            key={step.num}
            className={`flex items-center gap-2 p-1.5 rounded text-[10px] border transition-all ${
              step.active
                ? 'bg-rose-500/10 border-rose-500/40 text-slate-100 border-l-2 border-l-rose-500'
                : 'bg-base border-border/60 text-slate-400 border-l-2 border-l-blue-500'
            }`}
          >
            <span className="font-mono font-bold text-slate-400 w-4">{step.num}</span>
            <div className="flex-1">
              <div className="font-semibold">{step.title}</div>
              <div className="text-[9px] text-slate-400 font-mono">{step.detail}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

