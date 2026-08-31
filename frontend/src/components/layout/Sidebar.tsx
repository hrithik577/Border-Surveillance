'use client';

import React from 'react';
import {
  LayoutDashboard,
  Video,
  Eye,
  Car,
  UserCheck,
  Activity,
  Moon,
  AlertTriangle,
  Lock,
  Network,
  Cpu,
  FileText,
  Settings,
  Workflow
} from 'lucide-react';

export type NavItem =
  | 'overview'
  | 'surveillance'
  | 'detection'
  | 'anpr'
  | 'face'
  | 'behaviour'
  | 'night'
  | 'incidents'
  | 'evidence'
  | 'cameras'
  | 'architecture'
  | 'system'
  | 'audit'
  | 'settings';

interface SidebarProps {
  activeView: NavItem;
  onSelectView: (view: NavItem) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeView, onSelectView }) => {
  const getItemClasses = (view: NavItem) =>
    `flex items-center gap-2.5 px-3 py-2 rounded text-xs transition-all cursor-pointer ${
      activeView === view
        ? 'bg-blue-600/15 text-blue-400 font-semibold border-l-2 border-blue-500'
        : 'text-slate-400 hover:bg-surfaceElevated hover:text-slate-200'
    }`;

  return (
    <aside className="w-56 bg-surface border-r border-border flex flex-col shrink-0">
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {/* COMMAND SECTION */}
        <div>
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-2 mb-1">
            COMMAND
          </div>
          <div className="space-y-0.5">
            <div className={getItemClasses('overview')} onClick={() => onSelectView('overview')}>
              <LayoutDashboard className="w-4 h-4" />
              <span>Overview</span>
            </div>
            <div className={getItemClasses('surveillance')} onClick={() => onSelectView('surveillance')}>
              <Video className="w-4 h-4" />
              <span>Live Surveillance</span>
            </div>
          </div>
        </div>

        {/* INTELLIGENCE SECTION */}
        <div>
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-2 mb-1">
            INTELLIGENCE
          </div>
          <div className="space-y-0.5">
            <div className={getItemClasses('detection')} onClick={() => onSelectView('detection')}>
              <Eye className="w-4 h-4" />
              <span>AI Detection</span>
            </div>
            <div className={getItemClasses('anpr')} onClick={() => onSelectView('anpr')}>
              <Car className="w-4 h-4" />
              <span>ANPR Intelligence</span>
            </div>
            <div className={getItemClasses('face')} onClick={() => onSelectView('face')}>
              <UserCheck className="w-4 h-4" />
              <span>Face Intelligence</span>
            </div>
            <div className={getItemClasses('behaviour')} onClick={() => onSelectView('behaviour')}>
              <Activity className="w-4 h-4" />
              <span>Behaviour Analytics</span>
            </div>
            <div className={getItemClasses('night')} onClick={() => onSelectView('night')}>
              <Moon className="w-4 h-4" />
              <span>Night Surveillance</span>
            </div>
          </div>
        </div>

        {/* SECURITY SECTION */}
        <div>
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-2 mb-1">
            SECURITY
          </div>
          <div className="space-y-0.5">
            <div className={getItemClasses('incidents')} onClick={() => onSelectView('incidents')}>
              <AlertTriangle className="w-4 h-4" />
              <span>Incident Center</span>
            </div>
            <div className={getItemClasses('evidence')} onClick={() => onSelectView('evidence')}>
              <Lock className="w-4 h-4" />
              <span>Evidence Vault</span>
            </div>
          </div>
        </div>

        {/* INFRASTRUCTURE SECTION */}
        <div>
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-2 mb-1">
            INFRASTRUCTURE
          </div>
          <div className="space-y-0.5">
            <div className={getItemClasses('cameras')} onClick={() => onSelectView('cameras')}>
              <Network className="w-4 h-4" />
              <span>Camera Network</span>
            </div>
            <div className={getItemClasses('architecture')} onClick={() => onSelectView('architecture')}>
              <Workflow className="w-4 h-4 text-purple-400" />
              <span className="text-purple-300 font-medium">System Architecture</span>
            </div>
            <div className={getItemClasses('system')} onClick={() => onSelectView('system')}>
              <Cpu className="w-4 h-4" />
              <span>System Health</span>
            </div>
            <div className={getItemClasses('audit')} onClick={() => onSelectView('audit')}>
              <FileText className="w-4 h-4" />
              <span>Audit Logs</span>
            </div>
            <div className={getItemClasses('settings')} onClick={() => onSelectView('settings')}>
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="p-3 border-t border-border bg-base text-[11px] space-y-1">
        <div className="flex justify-between">
          <span className="text-slate-400">AI ENGINE</span>
          <span className="text-emerald-400 font-mono font-semibold">● ONLINE</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">EDGE NODES</span>
          <span className="text-sky-400 font-mono">ACTIVE</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">MODEL</span>
          <span className="font-mono text-slate-300">YOLOv8 + TRACK</span>
        </div>
        <div className="flex justify-between pt-1 border-t border-border/50 text-[10px]">
          <span className="text-slate-400">VERSION</span>
          <span className="font-mono text-slate-400">IBVAP v1.0</span>
        </div>
      </div>
    </aside>
  );
};
