'use client';

import React from 'react';
import { CameraNode } from '@/types/surveillance';

interface CameraWallProps {
  cameras: CameraNode[];
  onSelectCamera: (camId: string) => void;
}

export const CameraWall: React.FC<CameraWallProps> = ({ cameras, onSelectCamera }) => {
  return (
    <div className="bg-surface border border-border rounded p-3 space-y-2">
      <div className="flex items-center justify-between">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-100 flex items-center gap-2">
          📹 LIVE CCTV MATRIX (HIGH-DENSITY MONITORING)
        </div>
        <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          8 CHANNELS LIVE
        </span>
      </div>

      <div className="grid grid-cols-4 gap-2">
        {cameras.slice(0, 8).map(cam => (
          <div
            key={cam.id}
            onClick={() => onSelectCamera(cam.id)}
            className="relative bg-black border border-border hover:border-sky-500 rounded aspect-video overflow-hidden cursor-pointer group transition-all"
          >
            <img
              src="http://127.0.0.1:5000/video_feed/camera1"
              alt={cam.name}
              className="w-full h-full object-cover opacity-85 group-hover:opacity-100 transition-all"
            />
            <div className="absolute top-1 left-1 bg-black/70 px-1.5 py-0.5 rounded text-[9px] font-mono text-slate-200">
              {cam.id} | {cam.name}
            </div>
            <div className="absolute bottom-1 right-1 bg-black/70 px-1.5 py-0.5 rounded text-[9px] font-mono text-emerald-400">
              {cam.fps} FPS | AI ACTIVE
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
