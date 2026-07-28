import React from 'react';
import type { CostEstimation, TokenStats, RealtimeMetrics, ClusterStatus } from '../types';
import { Clock, DollarSign, Zap, Server, ShieldCheck, TrendingDown } from 'lucide-react';

interface TelemetryPanelProps {
  costEstimation?: CostEstimation;
  tokenStats?: TokenStats;
  realtimeMetrics?: RealtimeMetrics;
  clusterStatus?: ClusterStatus;
}

function MetricCell({
  icon,
  label,
  value,
  highlight
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={`p-3 rounded-lg ${highlight ? 'bg-green-500/5 border border-green-500/15' : 'panel-muted'}`}
    >
      <div className="flex items-center gap-1.5 text-zinc-500 dark:text-zinc-400 text-xs mb-1">
        {icon}
        <span>{label}</span>
      </div>
      <span
        className={`text-sm font-semibold tabular-nums font-mono ${
          highlight ? 'text-green-700 dark:text-green-400' : 'text-zinc-900 dark:text-zinc-100'
        }`}
      >
        {value}
      </span>
    </div>
  );
}

export const TelemetryPanel: React.FC<TelemetryPanelProps> = ({
  costEstimation,
  tokenStats,
  realtimeMetrics,
  clusterStatus
}) => {
  const onlineWorkers = clusterStatus?.online_workers || [];

  return (
    <div className="flex flex-col gap-5">
      <section className="panel p-5 flex flex-col gap-4">
        <div className="flex items-center gap-3 border-b border-zinc-200 dark:border-zinc-800 pb-3">
          <div className="icon-tile">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Cost estimate</h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Pre-flight planner projections</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <MetricCell
            icon={<Clock className="w-3.5 h-3.5" />}
            label="Latency"
            value={costEstimation?.runtime ? `${costEstimation.runtime}s` : '0.000s'}
          />
          <MetricCell
            icon={<DollarSign className="w-3.5 h-3.5" />}
            label="Cost"
            value={costEstimation?.cost ? `$${costEstimation.cost}` : '$0.0000'}
          />
          <MetricCell
            icon={<Zap className="w-3.5 h-3.5" />}
            label="Tokens"
            value={costEstimation?.tokens ? `${costEstimation.tokens}` : '0'}
          />
          <MetricCell
            icon={<TrendingDown className="w-3.5 h-3.5" />}
            label="Savings"
            value={tokenStats?.savings_percentage ? `${tokenStats.savings_percentage}%` : '0.0%'}
            highlight
          />
        </div>
      </section>

      <section className="panel p-5 flex flex-col gap-4">
        <div className="flex items-center gap-3 border-b border-zinc-200 dark:border-zinc-800 pb-3">
          <div className="icon-tile">
            <Server className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Workers</h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Registered cluster nodes</p>
          </div>
        </div>

        <div className="flex flex-col gap-1.5 max-h-[220px] overflow-y-auto">
          {clusterStatus?.worker_details && clusterStatus.worker_details.length > 0 ? (
            clusterStatus.worker_details.map((worker, idx) => {
              const isActive = worker.state === 'active';
              return (
                <div
                  key={idx}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-lg border ${
                    isActive
                      ? 'border-green-500/25 bg-green-500/5'
                      : 'panel-muted border-transparent'
                  }`}
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span
                        className={`status-dot ${isActive ? 'status-dot-online' : 'bg-zinc-400 dark:bg-zinc-600'}`}
                      />
                      <span className="text-xs font-mono font-medium text-zinc-900 dark:text-zinc-100 truncate">
                        {worker.worker_id}
                      </span>
                    </div>
                    {worker.current_node && (
                      <p className="text-[11px] text-zinc-500 dark:text-zinc-400 font-mono pl-4 mt-0.5 truncate">
                        {worker.current_node}
                      </p>
                    )}
                  </div>
                  <span
                    className={`text-[10px] font-medium uppercase tracking-wide px-2 py-0.5 rounded ${
                      isActive
                        ? 'text-green-700 dark:text-green-400 bg-green-500/10'
                        : 'text-zinc-500 bg-zinc-100 dark:bg-zinc-800'
                    }`}
                  >
                    {isActive ? 'Active' : 'Idle'}
                  </span>
                </div>
              );
            })
          ) : onlineWorkers.length > 0 ? (
            onlineWorkers.map((workerId, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between px-3 py-2.5 rounded-lg panel-muted"
              >
                <div className="flex items-center gap-2">
                  <span className="status-dot bg-zinc-400 dark:bg-zinc-600" />
                  <span className="text-xs font-mono text-zinc-800 dark:text-zinc-200">{workerId}</span>
                </div>
                <span className="text-[10px] font-medium text-zinc-500 uppercase">Idle</span>
              </div>
            ))
          ) : (
            <p className="text-xs text-zinc-500 dark:text-zinc-400 text-center py-4 panel-muted rounded-lg">
              No remote workers — using local runtime.
            </p>
          )}
        </div>
      </section>

      <div className="grid grid-cols-2 gap-2">
        <div className="panel p-4 text-center">
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-1">Nodes completed</p>
          <p className="text-xl font-semibold tabular-nums font-mono text-zinc-900 dark:text-zinc-100">
            {realtimeMetrics ? `${realtimeMetrics.completed_nodes}/${realtimeMetrics.total_nodes}` : '0/0'}
          </p>
        </div>
        <div className="panel p-4 text-center">
          <div className="flex items-center justify-center gap-1 text-xs text-zinc-500 dark:text-zinc-400 mb-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            Health
          </div>
          <p className="text-xl font-semibold tabular-nums font-mono text-green-600 dark:text-green-400">100%</p>
        </div>
      </div>
    </div>
  );
};
