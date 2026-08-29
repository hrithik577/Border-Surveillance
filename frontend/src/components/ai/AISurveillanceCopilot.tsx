'use client';

import React from 'react';
import { Bot, Navigation, Shield, AlertOctagon } from 'lucide-react';

interface AISurveillanceCopilotProps {
  summary: string;
  onTrack: () => void;
  onCorrelate: () => void;
  onEscalate: () => void;
}

export const AISurveillanceCopilot: React.FC<AISurveillanceCopilotProps> = ({
  summary,
  onTrack,
  onCorrelate,
  onEscalate
}) => {
  return (
    <div className="bg-surface border border-border rounded p-3 space-y-2.5 shrink-0">
      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
        <Bot className="w-3.5 h-3.5 text-sky-400" />
        AI SURVEILLANCE COPILOT ASSESSMENT
      </div>

      <div className="bg-base p-2.5 rounded border border-border/80 text-[11px] text-slate-300 leading-relaxed font-mono">
        "{summary}"
      </div>

      <div className="text-[9px] uppercase tracking-wider font-bold text-slate-400">
        SYSTEM RECOMMENDATION
      </div>

      <div className="flex gap-2">
        <button
          onClick={onTrack}
          className="flex-1 py-1 px-2 bg-blue-600/20 border border-blue-500/50 text-blue-300 text-[11px] font-semibold rounded hover:bg-blue-600/40 transition-all flex items-center justify-center gap-1"
        >
          <Navigation className="w-3 h-3" />
          TRACK
        </button>
        <button
          onClick={onCorrelate}
          className="flex-1 py-1 px-2 bg-surfaceElevated border border-border text-slate-300 text-[11px] font-semibold rounded hover:bg-border transition-all flex items-center justify-center gap-1"
        >
          <Shield className="w-3 h-3" />
          CORRELATE
        </button>
        <button
          onClick={onEscalate}
          className="flex-1 py-1 px-2 bg-rose-600/20 border border-rose-500/50 text-rose-300 text-[11px] font-semibold rounded hover:bg-rose-600/40 transition-all flex items-center justify-center gap-1"
        >
          <AlertOctagon className="w-3 h-3" />
          ESCALATE
        </button>
      </div>
    </div>
  );
};
