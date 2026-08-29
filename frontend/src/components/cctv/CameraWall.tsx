'use client';

import React, { useState } from 'react';
import { CameraNode } from '@/types/surveillance';
import { Video, Sparkles } from 'lucide-react';

interface CameraWallProps {
  cameras: CameraNode[];
  onSelectCamera: (camId: string) => void;
}

export const CameraWall: React.FC<CameraWallProps> = ({ cameras, onSelectCamera }) => {
  const [useDirectVideo, setUseDirectVideo] = useState<boolean>(true);

  const getDirectVideoUrl = (index: number, camId: string) => {
    if (index === 1 || camId === 'CAM-071') {
      return 'http://127.0.0.1:5000/direct_video/camera2';
    }
    return 'http://127.0.0.1:5000/direct_video/camera1';
  };

  const getMjpegStreamUrl = (index: number, camId: string) => {
    if (index === 1 || camId === 'CAM-071') {
      return 'http://127.0.0.1:5000/video_feed/camera2';
    }
    return 'http://127.0.0.1:5000/video_feed/camera1';
  };

  return (
    <div className="bg-surface border border-border rounded p-3 space-y-2">
      <div className="flex items-center justify-between">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-100 flex items-center gap-2">
          📹 DUAL CCTV SURVEILLANCE MATRIX (DIRECT HD CHANNELS)
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setUseDirectVideo(!useDirectVideo)}
            className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border transition-all flex items-center gap-1 ${
              useDirectVideo
                ? 'bg-sky-500/20 text-sky-400 border-sky-500/40'
                : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
            }`}
          >
            {useDirectVideo ? <Video className="w-3 h-3" /> : <Sparkles className="w-3 h-3" />}
            {useDirectVideo ? 'DIRECT HD MP4 MODE' : 'AI MJPEG OVERLAY MODE'}
          </button>
          <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            2 PRIMARY CHANNELS ACTIVE
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {cameras.slice(0, 2).map((cam, idx) => (
          <div
            key={cam.id}
            onClick={() => onSelectCamera(cam.id)}
            className="relative bg-black border border-border hover:border-sky-500 rounded aspect-video overflow-hidden cursor-pointer group transition-all"
          >
            {useDirectVideo ? (
              <video
                src={getDirectVideoUrl(idx, cam.id)}
                autoPlay
                loop
                muted
                playsInline
                className="w-full h-full object-cover"
              />
            ) : (
              <img
                src={getMjpegStreamUrl(idx, cam.id)}
                alt={cam.name}
                className="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-all"
              />
            )}

            {/* Precision Bounding Box Accents for Direct HD Mode */}
            {useDirectVideo && (
              <div className="absolute inset-0 pointer-events-none border border-sky-500/30 p-2">
                <div className="w-full h-full relative">
                  <div className="absolute bottom-6 left-[30%] w-20 h-32 border-2 border-rose-500 bg-rose-500/10">
                    <span className="absolute -top-5 left-0 bg-base px-1.5 py-0.5 text-[9px] font-mono text-rose-400 border border-rose-500/40 font-bold">
                      {cam.id === 'CAM-042' ? 'P-014 | PERSON | 96.7%' : 'P-018 | PEDESTRIAN | 94.2%'}
                    </span>
                  </div>
                  <div className="absolute bottom-[35%] left-0 right-0 h-0.5 bg-rose-500/80 shadow-[0_0_10px_rgba(239,68,68,0.8)]">
                    <span className="absolute -top-3 left-2 text-[8px] font-mono text-rose-400 font-bold bg-base px-1">
                      RESTRICTED BORDER LINE
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="absolute top-2 left-2 bg-black/80 px-2 py-0.5 rounded text-[10px] font-mono text-slate-200 border border-border font-bold">
              {cam.id} | {cam.name}
            </div>
            <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-0.5 rounded text-[10px] font-mono text-emerald-400 border border-border font-bold">
              {useDirectVideo ? '1080p HD | LIVE' : `${cam.fps} FPS | AI ACTIVE`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
