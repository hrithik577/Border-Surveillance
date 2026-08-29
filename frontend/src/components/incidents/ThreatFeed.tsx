'use client';

import React from 'react';
import { IncidentAlert } from '@/types/surveillance';

interface ThreatFeedProps {
  incidents: IncidentAlert[];
}

export const ThreatFeed: React.FC<ThreatFeedProps> = ({ incidents }) => {
  return (
    <div className="bg-surface border border-border rounded p-3 flex flex-col flex-1 overflow-hidden">
      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-300 mb-2">
        📊 REAL-TIME THREAT INTELLIGENCE LOG
      </div>
      <div className="overflow-y-auto flex-1 border border-border/60 rounded">
        <table className="w-full text-left text-[11px]">
          <thead className="bg-surfaceElevated text-[9px] uppercase tracking-wider text-slate-400 border-b border-border sticky top-0">
            <tr>
              <th className="py-1.5 px-2">Time</th>
              <th className="py-1.5 px-2">Sev</th>
              <th className="py-1.5 px-2">Event</th>
              <th className="py-1.5 px-2">Location</th>
              <th className="py-1.5 px-2">Cam</th>
              <th className="py-1.5 px-2">Conf</th>
              <th className="py-1.5 px-2">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40 font-mono text-slate-300">
            {incidents.map(inc => (
              <tr key={inc.id} className="hover:bg-surfaceElevated transition-all">
                <td className="py-1.5 px-2 text-slate-400">{inc.timestamp}</td>
                <td className="py-1.5 px-2">
                  <span
                    className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                      inc.severity === 'CRITICAL'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : inc.severity === 'HIGH'
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    }`}
                  >
                    {inc.severity}
                  </span>
                </td>
                <td className="py-1.5 px-2 font-sans font-medium text-slate-200">{inc.event}</td>
                <td className="py-1.5 px-2 text-slate-400">{inc.location}</td>
                <td className="py-1.5 px-2 text-sky-400">{inc.camera}</td>
                <td className="py-1.5 px-2 text-emerald-400">{inc.confidence}%</td>
                <td className="py-1.5 px-2">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-surfaceElevated text-slate-300 border border-border">
                    {inc.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
