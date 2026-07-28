import React, { useState } from 'react';
import { MermaidViewer } from './MermaidViewer';
import { Network, GitBranch, Zap, Cpu, Layers, Share2, TrendingDown, Coins } from 'lucide-react';
import type { GraphifyAnalytics } from '../types';

interface DiagramCanvasProps {
  astMermaid: string;
  initialDagMermaid: string;
  optimizedDagMermaid: string;
  currentDagMermaid: string;
  graphifyMermaid?: string;
  graphifyAnalytics?: GraphifyAnalytics;
  passes: string[];
}

type ViewMode = 'ast' | 'opt' | 'live' | 'graphify';

const views: { id: ViewMode; label: string; icon: React.ReactNode }[] = [
  { id: 'graphify', label: 'Graphify', icon: <Share2 className="w-3 h-3" /> },
  { id: 'live', label: 'Live DAG', icon: <Zap className="w-3 h-3" /> },
  { id: 'opt', label: 'Optimization', icon: <Layers className="w-3 h-3" /> },
  { id: 'ast', label: 'AST', icon: <GitBranch className="w-3 h-3" /> }
];

const viewMeta: Record<ViewMode, { title: string; density?: 'normal' | 'large' }> = {
  graphify: { title: 'Graphify knowledge graph', density: 'large' },
  live: { title: 'Live execution DAG', density: 'large' },
  opt: { title: 'Optimization comparison', density: 'normal' },
  ast: { title: 'Abstract syntax tree', density: 'normal' }
};

export const DiagramCanvas: React.FC<DiagramCanvasProps> = ({
  astMermaid,
  initialDagMermaid,
  optimizedDagMermaid,
  currentDagMermaid,
  graphifyMermaid,
  graphifyAnalytics,
  passes
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('graphify');
  const meta = viewMeta[viewMode];

  return (
    <section className="panel p-5 flex flex-col gap-4 min-h-[480px]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-200 dark:border-zinc-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="icon-tile">
            <Network className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Diagrams</h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">AST, DAG, and knowledge graph views</p>
          </div>
        </div>

        <div className="segment-control">
          {views.map(({ id, label, icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setViewMode(id)}
              className={`segment-btn flex items-center gap-1.5 ${
                viewMode === id ? 'segment-btn-active' : 'segment-btn-inactive'
              }`}
            >
              {icon}
              {label}
            </button>
          ))}
        </div>
      </div>

      {graphifyAnalytics && viewMode === 'graphify' && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <div className="panel-muted px-3 py-2 flex items-center gap-2">
            <Coins className="w-4 h-4 text-zinc-500 shrink-0" />
            <div>
              <p className="text-[11px] text-zinc-500 dark:text-zinc-400">Baseline tokens</p>
              <p className="text-sm font-medium tabular-nums text-zinc-900 dark:text-zinc-100">
                {graphifyAnalytics.estimated_baseline_tokens.toLocaleString()}
              </p>
            </div>
          </div>
          <div className="panel-muted px-3 py-2 flex items-center gap-2">
            <Zap className="w-4 h-4 text-zinc-500 shrink-0" />
            <div>
              <p className="text-[11px] text-zinc-500 dark:text-zinc-400">Actual</p>
              <p className="text-sm font-medium tabular-nums text-zinc-900 dark:text-zinc-100">
                {graphifyAnalytics.our_actual_tokens.toLocaleString()}
              </p>
            </div>
          </div>
          <div className="panel-muted px-3 py-2 flex items-center gap-2 border-green-500/20 bg-green-500/5">
            <TrendingDown className="w-4 h-4 text-green-600 dark:text-green-400 shrink-0" />
            <div>
              <p className="text-[11px] text-zinc-500 dark:text-zinc-400">Saved</p>
              <p className="text-sm font-medium tabular-nums text-green-700 dark:text-green-400">
                {graphifyAnalytics.tokens_saved.toLocaleString()}
                <span className="text-xs font-normal text-zinc-500 ml-1">
                  ({graphifyAnalytics.savings_percentage}%)
                </span>
              </p>
            </div>
          </div>
        </div>
      )}

      {passes && passes.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
          <Cpu className="w-3.5 h-3.5 shrink-0" />
          <span className="font-medium text-zinc-700 dark:text-zinc-300">Passes</span>
          {passes.map((p, idx) => (
            <span
              key={idx}
              className="px-2 py-0.5 rounded-md bg-zinc-100 dark:bg-zinc-800 font-mono text-[10px] text-zinc-700 dark:text-zinc-300"
            >
              {p}
            </span>
          ))}
        </div>
      )}

      <div className="flex-1 min-h-0 flex flex-col">
        {viewMode === 'opt' ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 flex-1 min-h-[360px]">
            <MermaidViewer
              chart={initialDagMermaid}
              id="initial_dag"
              title="Initial DAG"
              frame="inset"
              density="normal"
              emptyMessage="Run a query to compare raw vs optimized graphs"
            />
            <MermaidViewer
              chart={optimizedDagMermaid}
              id="optimized_dag"
              title="Optimized DAG"
              frame="inset"
              density="normal"
              emptyMessage="Optimizer output will appear here"
            />
          </div>
        ) : (
          <MermaidViewer
            chart={
              viewMode === 'graphify'
                ? graphifyMermaid || ''
                : viewMode === 'ast'
                  ? astMermaid
                  : currentDagMermaid || optimizedDagMermaid
            }
            id={viewMode === 'graphify' ? 'graphify_kg' : viewMode === 'ast' ? 'ast' : 'live_dag'}
            title={meta.title}
            density={meta.density}
            frame="canvas"
            emptyMessage={
              viewMode === 'graphify'
                ? 'Run a query to generate the knowledge graph'
                : viewMode === 'ast'
                  ? 'Compile a query to render the AST'
                  : 'Run an execution to view live progress'
            }
          />
        )}
      </div>
    </section>
  );
};
