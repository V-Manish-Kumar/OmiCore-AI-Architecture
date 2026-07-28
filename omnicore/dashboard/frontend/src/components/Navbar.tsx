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

const tabs: {
  id: NavbarProps['activeTab'];
  label: string;
  icon: React.ReactNode;
}[] = [
  { id: 'ide', label: 'Compiler', icon: <Terminal className="w-3.5 h-3.5" /> },
  { id: 'graphify', label: 'Graphify', icon: <Share2 className="w-3.5 h-3.5" /> },
  { id: 'topology', label: 'Topology', icon: <Layers className="w-3.5 h-3.5" /> },
  { id: 'telemetry', label: 'Telemetry', icon: <Activity className="w-3.5 h-3.5" /> },
  { id: 'traces', label: 'Traces', icon: <Zap className="w-3.5 h-3.5" /> }
];

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  status,
  activeWorkersCount,
  theme,
  toggleTheme
}) => {
  return (
    <header className="sticky top-0 z-50 w-full px-4 sm:px-6 py-3 app-header liquid-glass-header">
      <div className="max-w-[1400px] mx-auto flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-3 min-w-0">
          <div className="icon-tile">
            <Cpu className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 truncate">
                OmniCore
              </h1>
              <span className="hidden sm:inline text-[11px] font-medium text-zinc-500 dark:text-zinc-400">
                Compiler dashboard
              </span>
            </div>
          </div>
        </div>

        <nav className="nav-rail flex flex-wrap items-center overflow-x-auto">
          {tabs.map(({ id, label, icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setActiveTab(id)}
              className={`nav-tab flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === id ? 'nav-tab-active' : ''
              }`}
            >
              {icon}
              {label}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-2 shrink-0">
          <div
            className="hidden sm:flex items-center gap-2 px-2.5 py-1.5 rounded-lg panel-muted text-xs font-medium text-zinc-600 dark:text-zinc-300"
            title="Cluster status"
          >
            <span className={`status-dot ${status === 'online' ? 'status-dot-online' : 'bg-zinc-500'}`} />
            <span className="capitalize">{status || 'online'}</span>
            <span className="text-zinc-400 dark:text-zinc-500">·</span>
            <span>{activeWorkersCount} workers</span>
          </div>

          <button
            type="button"
            onClick={toggleTheme}
            className="btn-secondary p-2 sm:px-3 sm:py-1.5"
            title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            <span className="hidden md:inline">{theme === 'dark' ? 'Light' : 'Dark'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
