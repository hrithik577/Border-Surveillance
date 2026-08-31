'use client';

import React, { useState } from 'react';
import { CameraNode } from '@/types/surveillance';
import { Video, Sparkles, Play, Pause, Square, RotateCcw } from 'lucide-react';

interface CameraWallProps {
  cameras: CameraNode[];
  onSelectCamera: (camId: string) => void;
}

export const CameraWall: React.FC<CameraWallProps> = ({ cameras, onSelectCamera }) => {
  const [useDirectVideo, setUseDirectVideo] = useState<boolean>(false);
  const [playbackState, setPlaybackState] = useState<'PLAYING' | 'PAUSED' | 'STOPPED'>('PLAYING');

  const sendControlCommand = async (command: string) => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/video/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
      });
      if (res.ok) {
        const data = await res.json();
        setPlaybackState(data.state || 'PLAYING');
      }
    } catch (e) {
      console.warn('Video control fetch note:', e);
    }
  };

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
          📹 DIRECT SURVEILLANCE VIDEO INGESTION PIPELINE
        </div>
        <div className="flex items-center gap-2">
          {/* Playback Controls: Start, Pause, Resume, Stop, Restart */}
          <div className="flex items-center gap-1 bg-base p-1 rounded border border-border">
            <button
              onClick={() => sendControlCommand(playbackState === 'PAUSED' ? 'resume' : 'play')}
              title="Play / Resume"
              className="p-1 hover:bg-emerald-500/20 text-emerald-400 rounded transition-all"
            >
              <Play className="w-3.5 h-3.5 fill-emerald-400" />
            </button>
            <button
              onClick={() => sendControlCommand('pause')}
              title="Pause"
              className="p-1 hover:bg-amber-500/20 text-amber-400 rounded transition-all"
            >
              <Pause className="w-3.5 h-3.5 fill-amber-400" />
            </button>
            <button
              onClick={() => sendControlCommand('stop')}
              title="Stop"
              className="p-1 hover:bg-rose-500/20 text-rose-400 rounded transition-all"
            >
              <Square className="w-3.5 h-3.5 fill-rose-400" />
            </button>
            <button
              onClick={() => sendControlCommand('restart')}
              title="Restart"
              className="p-1 hover:bg-sky-500/20 text-sky-400 rounded transition-all"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>

          <button
            onClick={() => setUseDirectVideo(!useDirectVideo)}
            className={`px-2 py-1 rounded text-[10px] font-mono font-bold border transition-all flex items-center gap-1 ${
              useDirectVideo
                ? 'bg-sky-500/20 text-sky-400 border-sky-500/40'
                : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
            }`}
          >
            {useDirectVideo ? <Video className="w-3 h-3" /> : <Sparkles className="w-3 h-3" />}
            {useDirectVideo ? 'RAW HD MP4' : 'AI REALTIME OVERLAY'}
          </button>
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
