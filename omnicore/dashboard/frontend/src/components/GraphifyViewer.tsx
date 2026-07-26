import React, { useState } from 'react';
import { Share2, RefreshCw, Layers } from 'lucide-react';

export const GraphifyViewer: React.FC = () => {
  const [key, setKey] = useState<number>(0);

  const handleRefresh = () => {
    setKey((prev) => prev + 1);
  };

  return (
    <div className="flex flex-col gap-4 w-full">
      <div className="liquid-glass-card rounded-3xl p-4 px-6 border border-white/15 shadow-2xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-300">
            <Share2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              Graphify Codebase Knowledge Graph
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                1,528 Nodes &bull; 4,242 Edges
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">Interactive Network Visualization (`graphify-out/graph.html`)</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-xl border border-emerald-500/20">
            <Layers className="w-3.5 h-3.5" />
            <span>70 Communities Detected</span>
          </div>

          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-200 border border-white/10 text-xs font-semibold transition-all cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh View
          </button>
        </div>
      </div>

      <div className="w-full rounded-3xl border border-white/15 shadow-2xl overflow-hidden bg-slate-950/80">
        <iframe
          key={key}
          src="/api/graphify_html"
          title="Graphify Knowledge Graph"
          className="w-full h-[calc(100vh-210px)] min-h-[640px] border-none"
        />
      </div>
    </div>
  );
};
