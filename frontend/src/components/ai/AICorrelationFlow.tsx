'use client';

import React from 'react';

export const AICorrelationFlow: React.FC = () => {
  const steps = [
    { num: '01', title: 'PERSON DETECTED', detail: 'YOLOv8 sm_120 Neural Network' },
    { num: '02', title: 'TRACK ESTABLISHED', detail: 'ByteTrack Multi-Object Tracker (P-014)' },
    { num: '03', title: 'GEOFENCE PROXIMITY', detail: 'Restricted Zone A Vector Approach' },
    { num: '04', title: 'BOUNDARY CROSSING', detail: 'Virtual Fence Polygon Breach Confirmed', active: true },
    { num: '05', title: 'CROSS-CAMERA CORRELATION', detail: 'Spatial Path: CAM-039 ➔ CAM-041 ➔ CAM-042', active: true },
    { num: '06', title: 'THREAT SCORE 91 / 100', detail: 'Critical Security Alert Generated', active: true }
  ];

  return (
    <div className="bg-surface border border-border rounded p-3 space-y-2 shrink-0">
      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
        <span>⚙️</span> AI MULTI-SIGNAL CORRELATION PIPELINE
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
              <div className="text-[9px] text-slate-400">{step.detail}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
