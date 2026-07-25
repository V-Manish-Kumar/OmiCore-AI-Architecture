import React, { useState } from 'react';
import type { TopologyNode } from '../types';
import { MermaidViewer } from './MermaidViewer';
import { Layers, Plus, Trash2, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-react';

export const TopologyEditor: React.FC = () => {
  const [nodes, setNodes] = useState<TopologyNode[]>([
    {
      node_id: 'n0',
      name: 'Query Google',
      capability: 'WEB_SEARCH',
      input: 'query',
      output: 'findings'
    },
    {
      node_id: 'n1',
      name: 'Summarizer',
      capability: 'SUMMARIZATION',
      input: 'findings',
      output: 'summary'
    },
    {
      node_id: 'n2',
      name: 'PDF Exporter',
      capability: 'PDF_GENERATION',
      input: 'summary',
      output: 'report_pdf'
    }
  ]);

  const [newNode, setNewNode] = useState<TopologyNode>({
    node_id: `n${nodes.length}`,
    name: 'New Custom Task',
    capability: 'WEB_SEARCH',
    input: 'summary',
    output: 'audio_file'
  });

  const [topologicalOrder, setTopologicalOrder] = useState<string[]>([]);
  const [dagMermaid, setDagMermaid] = useState<string>('');
  const [diagnostics, setDiagnostics] = useState<string[]>([]);
  const [isCompiling, setIsCompiling] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddNode = () => {
    if (!newNode.node_id || !newNode.name) return;
    setNodes([...nodes, newNode]);
    const nextId = `n${nodes.length + 1}`;
    setNewNode({
      node_id: nextId,
      name: 'New Custom Task',
      capability: 'WEB_SEARCH',
      input: newNode.output,
      output: `out_${nextId}`
    });
  };

  const handleDeleteNode = (index: number) => {
    setNodes(nodes.filter((_, i) => i !== index));
  };

  const handleCompileTopology = async () => {
    setIsCompiling(true);
    setError(null);
    try {
      const res = await fetch('/api/compile_topology', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodes })
      });
      const data = await res.json();
      if (data.success) {
        setTopologicalOrder(data.topological_order || []);
        setDagMermaid(data.dag_mermaid || '');
        setDiagnostics(data.diagnostics || []);
      } else {
        setError(data.error || 'Failed to compile topology');
      }
    } catch (err: any) {
      setError(err.message || 'Server connection error');
    } finally {
      setIsCompiling(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-5 flex flex-col gap-5">
        <div className="liquid-glass-card rounded-3xl p-5 border border-white/15 shadow-2xl flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-300">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-100">Dynamic Topology Node Builder</h2>
                <p className="text-[11px] text-slate-400">Construct custom DAG node graphs</p>
              </div>
            </div>

            <button
              onClick={handleCompileTopology}
              disabled={isCompiling || nodes.length === 0}
              className="liquid-button flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white"
            >
              {isCompiling ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <CheckCircle className="w-3.5 h-3.5" />
              )}
              Lint & Compile
            </button>
          </div>

          <div className="flex flex-col gap-2.5 max-h-[300px] overflow-y-auto pr-1">
            {nodes.map((node, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all text-xs"
              >
                <div className="flex flex-col gap-0.5">
                  <div className="flex items-center gap-2">
                    <span className="px-1.5 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 font-mono text-[10px] font-bold">
                      {node.node_id}
                    </span>
                    <span className="font-semibold text-slate-100">{node.name}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono">
                    <span className="text-indigo-400">{node.capability}</span> ({node.input} &rarr; {node.output})
                  </div>
                </div>

                <button
                  onClick={() => handleDeleteNode(idx)}
                  className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/10 flex flex-col gap-3">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Add New Node</h3>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Node ID</label>
                <input
                  type="text"
                  value={newNode.node_id}
                  onChange={(e) => setNewNode({ ...newNode, node_id: e.target.value })}
                  className="w-full px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs font-mono text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Node Name</label>
                <input
                  type="text"
                  value={newNode.name}
                  onChange={(e) => setNewNode({ ...newNode, name: e.target.value })}
                  className="w-full px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Capability</label>
                <select
                  value={newNode.capability}
                  onChange={(e) => setNewNode({ ...newNode, capability: e.target.value })}
                  className="w-full px-3 py-1.5 rounded-xl bg-slate-900 border border-white/10 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="WEB_SEARCH">WEB_SEARCH</option>
                  <option value="SUMMARIZATION">SUMMARIZATION</option>
                  <option value="PDF_GENERATION">PDF_GENERATION</option>
                  <option value="DATA_ANALYSIS">DATA_ANALYSIS</option>
                </select>
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Input Var</label>
                <input
                  type="text"
                  value={newNode.input}
                  onChange={(e) => setNewNode({ ...newNode, input: e.target.value })}
                  className="w-full px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs font-mono text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <div className="flex-1 mr-2">
                <label className="text-[10px] text-slate-400 block mb-1">Output Var</label>
                <input
                  type="text"
                  value={newNode.output}
                  onChange={(e) => setNewNode({ ...newNode, output: e.target.value })}
                  className="w-full px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs font-mono text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <button
                type="button"
                onClick={handleAddNode}
                className="mt-4 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center gap-1.5 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="lg:col-span-7 flex flex-col gap-5">
        <div className="liquid-glass-card rounded-3xl p-5 border border-white/15 shadow-2xl flex flex-col gap-4 min-h-[420px]">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h2 className="text-sm font-bold text-slate-100">Compiled Topological Output</h2>
            {topologicalOrder.length > 0 && (
              <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                Order: {topologicalOrder.join(' → ')}
              </span>
            )}
          </div>

          {error && (
            <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {diagnostics.length > 0 && (
            <div className="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-200 text-xs font-mono">
              {diagnostics.join('\n')}
            </div>
          )}

          <div className="flex-1 rounded-2xl bg-slate-950/60 border border-white/10 flex items-center justify-center p-2 min-h-[300px]">
            <MermaidViewer
              chart={dagMermaid}
              id="topology_canvas"
              emptyMessage="Click 'Lint & Compile' to render custom topology graph"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
