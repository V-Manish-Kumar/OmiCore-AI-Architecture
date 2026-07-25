import React from 'react';
import { Cpu, Activity, Zap, Layers, Sparkles } from 'lucide-react';

interface NavbarProps {
  activeTab: 'ide' | 'topology' | 'telemetry' | 'traces';
  setActiveTab: (tab: 'ide' | 'topology' | 'telemetry' | 'traces') => void;
  status: string;
  activeWorkersCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  status,
  activeWorkersCount
}) => {
  return (
    <header className="sticky top-0 z-50 w-full px-6 py-3 border-b border-white/10 bg-slate-950/60 backdrop-blur-2xl shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* macOS Window Controls + Logo */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 pr-2 border-r border-white/10">
            <span className="w-3 h-3 rounded-full bg-rose-500/80 shadow-[0_0_10px_rgba(244,63,94,0.6)] cursor-pointer hover:opacity-100 transition-opacity" />
            <span className="w-3 h-3 rounded-full bg-amber-500/80 shadow-[0_0_10px_rgba(245,158,11,0.6)] cursor-pointer hover:opacity-100 transition-opacity" />
            <span className="w-3 h-3 rounded-full bg-emerald-500/80 shadow-[0_0_10px_rgba(16,185,129,0.6)] cursor-pointer hover:opacity-100 transition-opacity" />
          </div>

          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500/30 to-purple-500/30 border border-white/20 shadow-[inset_0_1px_1px_rgba(255,255,255,0.4)]">
              <Cpu className="w-5 h-5 text-indigo-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-indigo-200">
                  OmniCore AI
                </h1>
                <span className="px-1.5 py-0.5 text-[10px] font-semibold tracking-wide uppercase rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  v2.0 Glass
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Task Compiler & Adaptive Distributed Runtime</p>
            </div>
          </div>
        </div>

        {/* Liquid Glass Navigation Tabs */}
        <nav className="flex items-center p-1 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md shadow-[inset_0_1px_2px_rgba(0,0,0,0.4)]">
          <button
            onClick={() => setActiveTab('ide')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
              activeTab === 'ide'
                ? 'bg-gradient-to-r from-indigo-600/80 to-purple-600/80 text-white shadow-[0_4px_15px_rgba(99,102,241,0.4)] border border-white/20'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Compiler IDE
          </button>
          <button
            onClick={() => setActiveTab('topology')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
              activeTab === 'topology'
                ? 'bg-gradient-to-r from-indigo-600/80 to-purple-600/80 text-white shadow-[0_4px_15px_rgba(99,102,241,0.4)] border border-white/20'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Topology Builder
          </button>
          <button
            onClick={() => setActiveTab('telemetry')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
              activeTab === 'telemetry'
                ? 'bg-gradient-to-r from-indigo-600/80 to-purple-600/80 text-white shadow-[0_4px_15px_rgba(99,102,241,0.4)] border border-white/20'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            Telemetry & Nodes
          </button>
          <button
            onClick={() => setActiveTab('traces')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
              activeTab === 'traces'
                ? 'bg-gradient-to-r from-indigo-600/80 to-purple-600/80 text-white shadow-[0_4px_15px_rgba(99,102,241,0.4)] border border-white/20'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            Profiler & Traces
          </button>
        </nav>

        {/* Live Cluster Pill */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
            </span>
            <span className="text-xs font-semibold text-slate-300 capitalize">{status || 'Online'}</span>
          </div>

          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium">
            <Cpu className="w-3.5 h-3.5" />
            <span>{activeWorkersCount} Cluster Nodes</span>
          </div>
        </div>
      </div>
    </header>
  );
};
