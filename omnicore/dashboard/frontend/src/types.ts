export interface TokenStats {
  raw_tokens: number;
  optimized_tokens: number;
  savings_percentage: number;
}

export interface CostEstimation {
  runtime: number;
  cost: number;
  tokens: number;
}

export interface RealtimeMetrics {
  completed_nodes: number;
  total_nodes: number;
  total_tokens_processed: number;
  total_tokens_saved: number;
}

export interface GraphifyAnalytics {
  estimated_baseline_tokens: number;
  our_actual_tokens: number;
  tokens_saved: number;
  savings_percentage: number;
  nodes_eliminated: number;
}

export interface ExecutionDetails {
  status: 'compiling' | 'running' | 'completed' | 'failed';
  query: string;
  ast_mermaid: string;
  initial_dag_mermaid: string;
  optimized_dag_mermaid: string;
  current_dag_mermaid: string;
  graphify_mermaid?: string;
  graphify_analytics?: GraphifyAnalytics;
  passes: string[];
  node_statuses: Record<string, string>;
  logs: string[];
  token_stats: TokenStats;
  cost_estimation: CostEstimation;
  realtime_metrics: RealtimeMetrics;
  final_outputs?: Record<string, any>;
  error?: string;
}


export interface TopologyNode {
  node_id: string;
  name: string;
  capability: string;
  input: string;
  output: string;
}

export interface WorkerDetail {
  worker_id: string;
  state: 'idle' | 'active';
  active_tasks: number;
  capabilities: string[];
  current_node?: string | null;
}

export interface ClusterStatus {
  online_workers: string[];
  busy_workers?: string[];
  worker_details?: WorkerDetail[];
  status: string;
  diagnostics: {
    warnings: string[];
    timeline: {
      timestamp: number;
      event_type: string;
      message: string;
    }[];
  };
}


export interface MetricsData {
  active_workers: number;
  queue_depth: number;
  completed_tasks: number;
  failed_tasks: number;
  retry_count?: number;
  average_execution_latency_seconds?: number;
  cluster_health_score?: number;
}

export interface ProfilerReport {
  phase_metrics: {
    average_parsing_seconds?: number;
    average_optimization_seconds?: number;
    average_execution_seconds?: number;
  };
  caching: {
    hits: number;
    misses: number;
    hit_rate: number;
  };
  timestamp: number;
}
