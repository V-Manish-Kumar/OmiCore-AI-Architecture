import React, { useState } from 'react';
import { MermaidViewer } from './MermaidViewer';
import { Network, GitBranch, Zap, Sparkles, Layers } from 'lucide-react';

interface DiagramCanvasProps {
  astMermaid: string;
  initialDagMermaid: string;
  optimizedDagMermaid: string;
  currentDagMermaid: string;
  passes: string[];
}

export const DiagramCanvas: React.FC<DiagramCanvasProps> = ({
  astMermaid,
  initialDagMermaid,
  optimizedDagMermaid,
  currentDagMermaid,
  passes
}) => {
  const [viewMode, setViewMode] = useState<'ast' | 'opt' | 'live'>('live');

  return (
    <div className="liquid-glass-card rounded-3xl p-6 flex flex-col gap-4 border border-white/15 shadow-2xl relative min-h-[460px]">
      {/* Header with Liquid Mode Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-purple-500/20 border border-purple-500/30 text-purple-300">
            <Network className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Visual Topology & AST Canvas</h2>
            <p className="text-[11px] text-slate-400">Mermaid.js interactive flowcharts</p>
          </div>
        </div>

        {/* View Switcher Pills */}
        <div className="flex items-center p-1 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md">
          <button
            onClick={() => setViewMode('ast')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'ast'
                ? 'bg-indigo-500/30 text-indigo-200 border border-indigo-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <GitBranch className="w-3.5 h-3.5" />
            AST View
          </button>
          <button
            onClick={() => setViewMode('opt')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'opt'
                ? 'bg-indigo-500/30 text-indigo-200 border border-indigo-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Optimization Comparison
          </button>
          <button
            onClick={() => setViewMode('live')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'live'
                ? 'bg-gradient-to-r from-emerald-500/30 to-indigo-500/30 text-emerald-200 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-emerald-400" />
            Live Execution DAG
          </button>
        </div>
      </div>

      {/* Passes Pill Indicator */}
      {passes && passes.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 py-1 px-3 rounded-xl bg-slate-900/40 border border-white/5 text-[11px] text-slate-400">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span className="font-semibold text-slate-300">Applied Optimization Passes:</span>
          {passes.map((p, idx) => (
            <span
              key={idx}
              className="px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-mono text-[10px]"
            >
              {p}
            </span>
          ))}
        </div>
      )}

      {/* Canvas Rendering Area */}
      <div className="flex-1 rounded-2xl bg-slate-950/50 border border-white/10 overflow-hidden relative min-h-[340px] flex items-center justify-center">
        {viewMode === 'ast' && (
          <MermaidViewer chart={astMermaid} id="ast" emptyMessage="Compile a query to render AST hierarchy tree" />
        )}

        {viewMode === 'opt' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 w-full h-full divide-y lg:divide-y-0 lg:divide-x divide-white/10">
            <div className="flex flex-col p-2">
              <div className="text-center text-[11px] font-semibold text-indigo-300 tracking-wide uppercase py-1 bg-white/5 rounded-lg mb-2">
                Initial DAG (Raw Inputs)
              </div>
              <div className="flex-1 flex items-center justify-center">
                <MermaidViewer chart={initialDagMermaid} id="initial_dag" emptyMessage="No raw DAG available" />
              </div>
            </div>
            <div className="flex flex-col p-2">
              <div className="text-center text-[11px] font-semibold text-emerald-300 tracking-wide uppercase py-1 bg-white/5 rounded-lg mb-2">
                Optimized DAG (Token Minimization)
              </div>
              <div className="flex-1 flex items-center justify-center">
                <MermaidViewer chart={optimizedDagMermaid} id="optimized_dag" emptyMessage="No optimized DAG available" />
              </div>
            </div>
          </div>
        )}

        {viewMode === 'live' && (
          <MermaidViewer
            chart={currentDagMermaid || optimizedDagMermaid}
            id="live_dag"
            emptyMessage="Run an execution query to view live DAG node progress"
          />
        )}
      </div>
    </div>
  );
};
