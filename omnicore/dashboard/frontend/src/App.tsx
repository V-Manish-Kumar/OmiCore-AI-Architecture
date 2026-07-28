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

const TAB_TITLES: Record<string, string> = {
  ide: 'Compiler',
  graphify: 'Graphify',
  topology: 'Topology',
  telemetry: 'Telemetry',
  traces: 'Traces'
};

export function App() {
  const [activeTab, setActiveTab] = useState<'ide' | 'topology' | 'telemetry' | 'traces' | 'graphify'>('ide');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    const isDark = theme === 'dark';
    if (isDark) {
      document.documentElement.classList.add('dark', 'dark-mode');
      document.documentElement.classList.remove('light', 'light-mode');
      document.body.classList.add('dark', 'dark-mode');
      document.body.classList.remove('light', 'light-mode');
    } else {
      document.documentElement.classList.add('light', 'light-mode');
      document.documentElement.classList.remove('dark', 'dark-mode');
      document.body.classList.add('light', 'light-mode');
      document.body.classList.remove('dark', 'dark-mode');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

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
    logs: ['> Console ready. Enter intent query to compile & execute pipeline.'],
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
    <div className="min-h-screen flex flex-col">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        status={clusterStatus.status}
        activeWorkersCount={metrics.active_workers || clusterStatus.online_workers.length}
        theme={theme}
        toggleTheme={toggleTheme}
      />

      <main className="flex-1 max-w-[1400px] w-full mx-auto px-4 sm:px-6 py-5 sm:py-6 space-y-5">
        <header className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3 pb-1">
          <div>
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
              {TAB_TITLES[activeTab]}
            </h2>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">
              {activeTab === 'ide' && 'Compile intent queries and monitor pipeline execution.'}
              {activeTab === 'graphify' && 'Codebase knowledge graph from Graphify output.'}
              {activeTab === 'topology' && 'Build and validate custom task DAGs.'}
              {activeTab === 'telemetry' && 'Runtime metrics and cluster worker status.'}
              {activeTab === 'traces' && 'Profiler timings and distributed trace spans.'}
            </p>
          </div>
          {activeTab === 'ide' && (
            <dl className="flex gap-4 text-sm">
              <div>
                <dt className="text-zinc-500 dark:text-zinc-400 text-xs">Queue</dt>
                <dd className="font-medium tabular-nums text-zinc-900 dark:text-zinc-100">{metrics.queue_depth}</dd>
              </div>
              <div>
                <dt className="text-zinc-500 dark:text-zinc-400 text-xs">Workers</dt>
                <dd className="font-medium tabular-nums text-zinc-900 dark:text-zinc-100">
                  {clusterStatus.online_workers.length}
                </dd>
              </div>
              <div>
                <dt className="text-zinc-500 dark:text-zinc-400 text-xs">Tasks done</dt>
                <dd className="font-medium tabular-nums text-zinc-900 dark:text-zinc-100">{metrics.completed_tasks}</dd>
              </div>
            </dl>
          )}
        </header>

        {activeTab === 'ide' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
            <div className="lg:col-span-8 flex flex-col gap-5">
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

            <div className="lg:col-span-4 flex flex-col gap-5">
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
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
            <div className="lg:col-span-5">
              <TelemetryPanel
                costEstimation={executionDetails.cost_estimation}
                tokenStats={executionDetails.token_stats}
                realtimeMetrics={executionDetails.realtime_metrics}
                clusterStatus={clusterStatus}
              />
            </div>
            <div className="lg:col-span-7">
              <TerminalLogs logs={executionDetails.logs} status={executionDetails.status} />
            </div>
          </div>
        )}

        {activeTab === 'traces' && <TracesPanel />}
      </main>

      <footer className="mt-auto py-3 px-4 border-t border-zinc-200 dark:border-zinc-800 text-center text-xs text-zinc-500 dark:text-zinc-500">
        OmniCore · Task IR compiler & distributed runtime
      </footer>
    </div>
  );
}
export default App;
