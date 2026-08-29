'use client';

import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

const mockTrendData = [
  { time: '00:00', persons: 45, vehicles: 12, intrusions: 0 },
  { time: '04:00', persons: 28, vehicles: 5, intrusions: 1 },
  { time: '08:00', persons: 120, vehicles: 85, intrusions: 2 },
  { time: '12:00', persons: 310, vehicles: 140, intrusions: 1 },
  { time: '16:00', persons: 450, vehicles: 210, intrusions: 4 },
  { time: '20:00', persons: 280, vehicles: 110, intrusions: 6 }
];

export const DetectionTrend: React.FC = () => {
  return (
    <div className="bg-surface border border-border rounded p-3 space-y-2 h-full flex flex-col">
      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-300">
        📈 24-HOUR DETECTION & INCIDENT TIMELINE
      </div>
      <div className="flex-1 w-full min-h-[140px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={mockTrendData}>
            <CartesianGrid stroke="#1e2c40" strokeDasharray="3 3" />
            <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0e141f', borderColor: '#1e2c40', fontSize: '11px' }}
            />
            <Line type="monotone" dataKey="persons" stroke="#06b6d4" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="vehicles" stroke="#3b82f6" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="intrusions" stroke="#ef4444" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
