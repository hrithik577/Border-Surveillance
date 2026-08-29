'use client';

import React, { useState } from 'react';
import { IncidentAlert } from '@/types/surveillance';
import { ShieldAlert, Eye, MapPin, Camera, Clock, CheckCircle, Video } from 'lucide-react';

interface IncidentPanelProps {
  incident: IncidentAlert;
  onAcknowledge: () => void;
  onTrackMap: () => void;
  onViewEvidence: () => void;
}

export const IncidentPanel: React.FC<IncidentPanelProps> = ({
  incident,
  onAcknowledge,
  onTrackMap,
  onViewEvidence
}) => {
  const [useDirectVideo, setUseDirectVideo] = useState<boolean>(true);

  return (
    <div className="bg-surface border border-rose-500/80 rounded p-3 space-y-3 shadow-[0_0_15px_rgba(239,68,68,0.15)] shrink-0">
      <div className="flex items-center justify-between">
        <div>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40">
            {incident.severity} INCIDENT #{incident.id}
          </span>
          <h3 className="text-xs font-bold text-slate-100 mt-1 uppercase tracking-wide">
            {incident.event}
          </h3>
        </div>
        <div className="bg-rose-500/20 border border-rose-500 text-rose-400 font-mono font-bold text-sm px-2.5 py-1 rounded">
          {incident.threatScore} / 100
        </div>
      </div>

      {/* Meta Grid */}
      <div className="grid grid-cols-2 gap-2 bg-base p-2 rounded border border-border text-[11px]">
        <div>
          <div className="text-[9px] uppercase text-slate-400">Location</div>
          <div className="font-mono font-semibold text-rose-400 flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {incident.location}
          </div>
        </div>
        <div>
          <div className="text-[9px] uppercase text-slate-400">Camera</div>
          <div className="font-mono font-semibold text-sky-400 flex items-center gap-1">
            <Camera className="w-3 h-3" />
            {incident.camera}
          </div>
        </div>
        <div>
          <div className="text-[9px] uppercase text-slate-400">Time</div>
          <div className="font-mono text-slate-300 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {incident.timestamp}
          </div>
        </div>
        <div>
          <div className="text-[9px] uppercase text-slate-400">AI Confidence</div>
          <div className="font-mono font-semibold text-emerald-400">
            {incident.confidence}%
          </div>
        </div>
      </div>

      {/* Evidence Snapshot / Video Frame */}
      <div className="relative w-full h-36 bg-black border border-border rounded overflow-hidden">
        {useDirectVideo ? (
          <video
            src="http://127.0.0.1:5000/direct_video/camera1"
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover"
          />
        ) : (
          <img
            src="http://127.0.0.1:5000/video_feed/camera1"
            alt="Evidence Stream"
            className="w-full h-full object-cover opacity-90"
          />
        )}

        {/* Overlay Badge */}
        <div className="absolute top-2 right-2">
          <button
            onClick={() => setUseDirectVideo(!useDirectVideo)}
            className="px-1.5 py-0.5 rounded text-[8px] font-mono bg-black/80 text-sky-400 border border-sky-500/40 hover:bg-sky-500/20"
          >
            {useDirectVideo ? 'HD MP4' : 'AI STREAM'}
          </button>
        </div>

        <div className="absolute bottom-1.5 left-1.5 bg-black/80 px-1.5 py-0.5 rounded text-[9px] font-mono text-cyan-400 border border-cyan-500/30">
          SUBJECT P-014 | BOUNDARY BREACH
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={onAcknowledge}
          className="flex-1 py-1.5 px-2 bg-rose-600/30 border border-rose-500 text-rose-300 text-xs font-semibold rounded hover:bg-rose-600/50 transition-all flex items-center justify-center gap-1"
        >
          <CheckCircle className="w-3.5 h-3.5" />
          ACKNOWLEDGE
        </button>
        <button
          onClick={onTrackMap}
          className="py-1.5 px-3 bg-blue-600/30 border border-blue-500 text-blue-300 text-xs font-semibold rounded hover:bg-blue-600/50 transition-all flex items-center justify-center gap-1"
        >
          <Eye className="w-3.5 h-3.5" />
          TRACK MAP
        </button>
        <button
          onClick={onViewEvidence}
          className="py-1.5 px-3 bg-surfaceElevated border border-border text-slate-300 text-xs font-semibold rounded hover:bg-border transition-all"
        >
          EVIDENCE
        </button>
      </div>
    </div>
  );
};
