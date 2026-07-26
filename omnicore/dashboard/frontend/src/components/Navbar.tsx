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
        {/* Logo & Title */}
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500/30 to-purple-500/30 border border-white/20 shadow-[inset_0_1px_1px_rgba(255,255,255,0.4)]">
            <Cpu className="w-5 h-5 text-indigo-300" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-indigo-200">
              OmniCore AI
            </h1>
            <p className="text-[11px] text-slate-400 font-medium">Task Compiler & Adaptive Distributed Runtime</p>
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
            <span className="text-xs font-semibold text-slate-300 capitalize">{status || '3 Nodes Registered'}</span>
          </div>

          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium">
            <Cpu className="w-3.5 h-3.5" />
            <span>{activeWorkersCount > 0 ? `${activeWorkersCount} Active Task Worker` : '0 Active (Standby Pool)'}</span>
          </div>
        </div>

      </div>
    </header>
  );
};
