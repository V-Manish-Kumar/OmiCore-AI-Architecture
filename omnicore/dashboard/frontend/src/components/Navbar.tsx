import React from 'react';
import { Cpu, Activity, Zap, Layers, Share2, Sun, Moon, Terminal } from 'lucide-react';

interface NavbarProps {
  activeTab: 'ide' | 'topology' | 'telemetry' | 'traces' | 'graphify';
  setActiveTab: (tab: 'ide' | 'topology' | 'telemetry' | 'traces' | 'graphify') => void;
  status: string;
  activeWorkersCount: number;
  theme: 'dark' | 'light';
  toggleTheme: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  status,
  activeWorkersCount,
  theme,
  toggleTheme
}) => {
  return (
    <header className="sticky top-0 z-50 w-full px-6 py-3 liquid-glass-header transition-colors">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Logo & Title */}
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-500">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight flex items-center gap-2">
              OmniCore AI
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-indigo-500/10 text-indigo-500 border border-indigo-500/20">
                v2.4
              </span>
            </h1>
            <p className="text-[11px] opacity-70 font-medium">Provider-Agnostic AI Task Compiler & Runtime</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center p-1 rounded-2xl bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 backdrop-blur-md">
          <button
            onClick={() => setActiveTab('ide')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 cursor-pointer ${
              activeTab === 'ide'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'opacity-70 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            Compiler IDE
          </button>
          <button
            onClick={() => setActiveTab('graphify')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 cursor-pointer ${
              activeTab === 'graphify'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'opacity-70 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5'
            }`}
          >
            <Share2 className="w-3.5 h-3.5" />
            Graphify Graph
          </button>
          <button
            onClick={() => setActiveTab('topology')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 cursor-pointer ${
              activeTab === 'topology'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'opacity-70 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Topology Builder
          </button>
          <button
            onClick={() => setActiveTab('telemetry')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 cursor-pointer ${
              activeTab === 'telemetry'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'opacity-70 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            Telemetry & Nodes
          </button>
          <button
            onClick={() => setActiveTab('traces')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 cursor-pointer ${
              activeTab === 'traces'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'opacity-70 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5'
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            Profiler & Traces
          </button>
        </nav>

        {/* Right Actions & Theme Toggle */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-xs font-semibold">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span>{status || 'Cluster Online'} ({activeWorkersCount} Active)</span>
          </div>


          <button
            onClick={toggleTheme}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/15 border border-black/10 dark:border-white/10 text-xs font-semibold transition-all cursor-pointer"
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? (
              <>
                <Sun className="w-4 h-4 text-amber-400" />
                <span className="hidden md:inline">Light</span>
              </>
            ) : (
              <>
                <Moon className="w-4 h-4 text-indigo-500" />
                <span className="hidden md:inline">Dark</span>
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

