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

  const fieldClass =
    'w-full px-2.5 py-1.5 rounded-lg text-xs bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30';

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
      <div className="lg:col-span-5 flex flex-col gap-5">
        <section className="panel p-5 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
            <div className="flex items-center gap-3">
              <div className="icon-tile">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Node builder</h3>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">Define capabilities and data flow</p>
              </div>
            </div>

            <button
              type="button"
              onClick={handleCompileTopology}
              disabled={isCompiling || nodes.length === 0}
              className="btn-primary text-xs py-1.5"
            >
              {isCompiling ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <CheckCircle className="w-3.5 h-3.5" />
              )}
              Compile
            </button>
          </div>

          <div className="flex flex-col gap-1.5 max-h-[280px] overflow-y-auto">
            {nodes.map((node, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between px-3 py-2.5 rounded-lg panel-muted text-xs"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="px-1.5 py-0.5 rounded bg-zinc-200 dark:bg-zinc-800 font-mono text-[10px] text-zinc-600 dark:text-zinc-300">
                      {node.node_id}
                    </span>
                    <span className="font-medium text-zinc-900 dark:text-zinc-100 truncate">{node.name}</span>
                  </div>
                  <p className="text-[11px] text-zinc-500 font-mono mt-0.5 truncate">
                    {node.capability} · {node.input} → {node.output}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => handleDeleteNode(idx)}
                  className="p-1.5 rounded-md text-red-600 hover:bg-red-500/10 transition-colors shrink-0"
                  aria-label="Remove node"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>

          <div className="panel-muted p-4 flex flex-col gap-3">
            <h4 className="text-xs font-medium text-zinc-700 dark:text-zinc-300">Add node</h4>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[11px] text-zinc-500 block mb-1">ID</label>
                <input
                  type="text"
                  value={newNode.node_id}
                  onChange={(e) => setNewNode({ ...newNode, node_id: e.target.value })}
                  className={fieldClass + ' font-mono'}
                />
              </div>
              <div>
                <label className="text-[11px] text-zinc-500 block mb-1">Name</label>
                <input
                  type="text"
                  value={newNode.name}
                  onChange={(e) => setNewNode({ ...newNode, name: e.target.value })}
                  className={fieldClass}
                />
              </div>
              <div>
                <label className="text-[11px] text-zinc-500 block mb-1">Capability</label>
                <select
                  value={newNode.capability}
                  onChange={(e) => setNewNode({ ...newNode, capability: e.target.value })}
                  className={fieldClass}
                >
                  <option value="WEB_SEARCH">WEB_SEARCH</option>
                  <option value="SUMMARIZATION">SUMMARIZATION</option>
                  <option value="PDF_GENERATION">PDF_GENERATION</option>
                  <option value="DATA_ANALYSIS">DATA_ANALYSIS</option>
                </select>
              </div>
              <div>
                <label className="text-[11px] text-zinc-500 block mb-1">Input</label>
                <input
                  type="text"
                  value={newNode.input}
                  onChange={(e) => setNewNode({ ...newNode, input: e.target.value })}
                  className={fieldClass + ' font-mono'}
                />
              </div>
            </div>

            <div className="flex items-end gap-2">
              <div className="flex-1">
                <label className="text-[11px] text-zinc-500 block mb-1">Output</label>
                <input
                  type="text"
                  value={newNode.output}
                  onChange={(e) => setNewNode({ ...newNode, output: e.target.value })}
                  className={fieldClass + ' font-mono'}
                />
              </div>
              <button type="button" onClick={handleAddNode} className="btn-secondary shrink-0">
                <Plus className="w-4 h-4" />
                Add
              </button>
            </div>
          </div>
        </section>
      </div>

      <div className="lg:col-span-7 flex flex-col gap-5">
        <section className="panel p-5 flex flex-col gap-4 min-h-[420px]">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-200 dark:border-zinc-800 pb-3">
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Compiled graph</h3>
            {topologicalOrder.length > 0 && (
              <span className="text-[11px] font-mono text-zinc-500 dark:text-zinc-400">
                Order: {topologicalOrder.join(' → ')}
              </span>
            )}
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-700 dark:text-red-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {diagnostics.length > 0 && (
            <pre className="p-3 rounded-lg panel-muted text-[11px] font-mono text-zinc-600 dark:text-zinc-300 whitespace-pre-wrap">
              {diagnostics.join('\n')}
            </pre>
          )}

          <div className="flex-1 min-h-[340px] flex flex-col">
            <MermaidViewer
              chart={dagMermaid}
              id="topology_canvas"
              title="Topology DAG"
              density="large"
              frame="canvas"
              emptyMessage="Compile the topology to preview the DAG"
            />
          </div>
        </section>
      </div>
    </div>
  );
};
