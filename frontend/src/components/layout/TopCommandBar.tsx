'use client';

import React, { useState, useEffect } from 'react';
import { Search, User, ShieldAlert, Cpu, Activity, Zap } from 'lucide-react';
import { SystemMetrics } from '@/types/surveillance';

interface TopCommandBarProps {
  metrics: SystemMetrics;
  onRunSimulation: () => void;
  onOpenSearch: () => void;
  onOpenLogin: () => void;
}

export const TopCommandBar: React.FC<TopCommandBarProps> = ({
  metrics,
  onRunSimulation,
  onOpenSearch,
  onOpenLogin
}) => {
  const [clock, setClock] = useState<string>('21:43:18 IST');

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      const hrs = String(now.getHours()).padStart(2, '0');
      const mins = String(now.getMinutes()).padStart(2, '0');
      const secs = String(now.getSeconds()).padStart(2, '0');
      setClock(`${hrs}:${mins}:${secs} IST`);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-[52px] bg-surface border-b border-border px-4 flex items-center justify-between shrink-0 z-50">
      {/* Left Brand Identity */}
      <div className="flex items-center gap-3">
        <div className="w-7 h-7 bg-gradient-to-br from-blue-900 to-sky-600 border border-sky-400 rounded flex items-center justify-center font-bold text-white text-sm shadow-[0_0_10px_rgba(2,132,199,0.4)]">
          IB
        </div>
        <div>
          <div className="text-[15px] font-bold tracking-wider text-slate-100 flex items-center gap-2">
            IBVAP
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30 font-mono">
              SIH26-26187
            </span>
          </div>
          <div className="text-[10px] text-slate-400 tracking-wider uppercase">
            INTELLIGENT BORDER VIDEO ANALYTICS PLATFORM
          </div>
        </div>
      </div>

      {/* Center System Telemetry Strip */}
      <div className="flex items-center gap-5 bg-base/80 px-4 py-1 rounded border border-border">
        <div className="flex flex-col items-center">
          <span className="text-[9px] text-slate-400 uppercase tracking-wider">SYSTEM STATUS</span>
          <span className="text-[12px] font-mono font-semibold text-emerald-400 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            OPERATIONAL
          </span>
        </div>
        <div className="w-px h-6 bg-border"></div>
        <div className="flex flex-col items-center">
          <span className="text-[9px] text-slate-400 uppercase tracking-wider">CAMERAS</span>
          <span className="text-[12px] font-mono font-semibold text-slate-100">
            {metrics.camerasOnline} / {metrics.camerasTotal}
          </span>
        </div>
        <div className="w-px h-6 bg-border"></div>
        <div className="flex flex-col items-center">
          <span className="text-[9px] text-slate-400 uppercase tracking-wider">AI MODELS</span>
          <span className="text-[12px] font-mono font-semibold text-sky-400">
            {metrics.aiModelsActive} / {metrics.aiModelsTotal} ACTIVE
          </span>
        </div>
        <div className="w-px h-6 bg-border"></div>
        <div className="flex flex-col items-center">
          <span className="text-[9px] text-slate-400 uppercase tracking-wider">ACTIVE ALERTS</span>
          <span className="text-[12px] font-mono font-semibold text-rose-400">
            {metrics.activeAlerts}
          </span>
        </div>
        <div className="w-px h-6 bg-border"></div>
        <div className="flex flex-col items-center">
          <span className="text-[9px] text-slate-400 uppercase tracking-wider">INFERENCE</span>
          <span className="text-[12px] font-mono font-semibold text-slate-100">
            {metrics.inferenceFps} FPS
          </span>
        </div>
        <div className="w-px h-6 bg-border"></div>
        <div className="flex flex-col items-center">
          <span className="text-[9px] text-slate-400 uppercase tracking-wider">GPU LOAD</span>
          <span className="text-[12px] font-mono font-semibold text-amber-400">
            {metrics.gpuUtilization}%
          </span>
        </div>
        <div className="w-px h-6 bg-border"></div>
        <div className="flex flex-col items-center">
          <span className="text-[9px] text-slate-400 uppercase tracking-wider">LATENCY</span>
          <span className="text-[12px] font-mono font-semibold text-emerald-400">
            {metrics.latencyMs} ms
          </span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        <span className="font-mono text-xs text-slate-300 bg-surfaceElevated px-2 py-1 rounded border border-border">
          {clock}
        </span>
        <span className="text-[10px] font-semibold tracking-wide uppercase px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          SECURE OPERATIONS
        </span>

        <button
          onClick={onRunSimulation}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 border border-purple-400 rounded hover:from-purple-500 hover:to-indigo-500 transition-all shadow-[0_0_12px_rgba(124,58,237,0.4)]"
        >
          <Zap className="w-3.5 h-3.5" />
          RUN SIMULATION MODE
        </button>

        <button
          onClick={onOpenSearch}
          className="p-1.5 bg-surfaceElevated border border-border text-slate-300 rounded hover:bg-border transition-all"
          title="Search"
        >
          <Search className="w-4 h-4" />
        </button>

        <button
          onClick={onOpenLogin}
          className="p-1.5 bg-surfaceElevated border border-border text-slate-300 rounded hover:bg-border transition-all"
          title="Operator Settings"
        >
          <User className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
