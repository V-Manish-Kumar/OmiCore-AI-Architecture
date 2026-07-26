import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { SandboxPanel } from './components/SandboxPanel';
import { DiagramCanvas } from './components/DiagramCanvas';
import { TelemetryPanel } from './components/TelemetryPanel';
import { TerminalLogs } from './components/TerminalLogs';
import { TopologyEditor } from './components/TopologyEditor';
import { TracesPanel } from './components/TracesPanel';
import { GraphifyViewer } from './components/GraphifyViewer';
import type { ExecutionDetails, ClusterStatus, MetricsData } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<'ide' | 'topology' | 'telemetry' | 'traces' | 'graphify'>('ide');


  const [clusterStatus, setClusterStatus] = useState<ClusterStatus>({
    online_workers: ['worker_search_node', 'worker_summarize_node'],
    status: 'online',
    diagnostics: { warnings: [], timeline: [] }
  });

  const [metrics, setMetrics] = useState<MetricsData>({
    active_workers: 2,
    queue_depth: 0,
    completed_tasks: 0,
    failed_tasks: 0
  });

  const [executionDetails, setExecutionDetails] = useState<ExecutionDetails>({
    status: 'idle' as any,
    query: '',
    ast_mermaid: '',
    initial_dag_mermaid: '',
    optimized_dag_mermaid: '',
    current_dag_mermaid: '',
    passes: [],
    node_statuses: {},
    logs: ['> Linter console ready. Enter intent query to begin compilation...'],
    token_stats: { raw_tokens: 0, optimized_tokens: 0, savings_percentage: 0.0 },
    cost_estimation: { runtime: 0.0, cost: 0.0, tokens: 0 },
    realtime_metrics: { completed_nodes: 0, total_nodes: 0, total_tokens_processed: 0, total_tokens_saved: 0 }
  });

  const [activeExecutionId, setActiveExecutionId] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);

  useEffect(() => {
    const fetchStatusAndMetrics = async () => {
      try {
        const [statRes, metRes] = await Promise.all([
          fetch('/api/status').then((r) => r.json()),
          fetch('/api/metrics').then((r) => r.json())
        ]);
        setClusterStatus(statRes);
        setMetrics(metRes);
      } catch (err) {
        console.error('Failed to poll status/metrics:', err);
      }
    };

    fetchStatusAndMetrics();
    const interval = setInterval(fetchStatusAndMetrics, 4000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!activeExecutionId) return;

    const pollExecution = async () => {
      try {
        const res = await fetch(`/api/execution/${activeExecutionId}`);
        const data: ExecutionDetails = await res.json();
        if (data && data.status) {
          setExecutionDetails(data);
          if (data.status === 'completed' || data.status === 'failed') {
            setIsExecuting(false);
            setActiveExecutionId(null);
          }
        }
      } catch (err) {
        console.error('Error polling execution:', err);
        setIsExecuting(false);
      }
    };

    pollExecution();
    const interval = setInterval(pollExecution, 600);
    return () => clearInterval(interval);
  }, [activeExecutionId]);

  const handleRunQuery = async (query: string) => {
    setIsExecuting(true);
    try {
      const res = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      if (data.success && data.execution_id) {
        setActiveExecutionId(data.execution_id);
      } else {
        setIsExecuting(false);
      }
    } catch (err: any) {
      console.error('Execute error:', err);
      setIsExecuting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col relative selection:bg-indigo-500/30 selection:text-indigo-200">
      <div className="fixed top-10 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="fixed bottom-10 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-600/5 rounded-full blur-[160px] pointer-events-none -z-10" />

      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        status={clusterStatus.status}
        activeWorkersCount={metrics.active_workers || clusterStatus.online_workers.length}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-6">
        {activeTab === 'ide' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-8 flex flex-col gap-6">
              <SandboxPanel onRunQuery={handleRunQuery} isExecuting={isExecuting} />
              <DiagramCanvas
                astMermaid={executionDetails.ast_mermaid}
                initialDagMermaid={executionDetails.initial_dag_mermaid}
                optimizedDagMermaid={executionDetails.optimized_dag_mermaid}
                currentDagMermaid={executionDetails.current_dag_mermaid}
                graphifyMermaid={executionDetails.graphify_mermaid}
                graphifyAnalytics={executionDetails.graphify_analytics}
                passes={executionDetails.passes}
              />

              <TerminalLogs
                logs={executionDetails.logs}
                status={executionDetails.status}
                onClearLogs={() =>
                  setExecutionDetails((prev) => ({ ...prev, logs: ['> Console cleared.'] }))
                }
              />
            </div>

            <div className="lg:col-span-4 flex flex-col gap-6">
              <TelemetryPanel
                costEstimation={executionDetails.cost_estimation}
                tokenStats={executionDetails.token_stats}
                realtimeMetrics={executionDetails.realtime_metrics}
                clusterStatus={clusterStatus}
              />
            </div>
          </div>
        )}

        {activeTab === 'graphify' && <GraphifyViewer />}

        {activeTab === 'topology' && <TopologyEditor />}


        {activeTab === 'telemetry' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-5">
              <TelemetryPanel
                costEstimation={executionDetails.cost_estimation}
                tokenStats={executionDetails.token_stats}
                realtimeMetrics={executionDetails.realtime_metrics}
                clusterStatus={clusterStatus}
              />
            </div>
            <div className="lg:col-span-7">
              <TerminalLogs
                logs={executionDetails.logs}
                status={executionDetails.status}
              />
            </div>
          </div>
        )}

        {activeTab === 'traces' && <TracesPanel />}
      </main>

      <footer className="w-full py-4 border-t border-white/10 text-center text-xs text-slate-500 backdrop-blur-md">
        OmniCore AI Compiler Dashboard &bull; Liquid Glass UI Edition &bull; Provider-Agnostic Distributed Engine
      </footer>
    </div>
  );
}
export default App;
