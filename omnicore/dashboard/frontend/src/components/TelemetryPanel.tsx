import React from 'react';
import type { CostEstimation, TokenStats, RealtimeMetrics, ClusterStatus } from '../types';
import { Clock, DollarSign, Zap, Server, ShieldCheck, TrendingDown } from 'lucide-react';

interface TelemetryPanelProps {
  costEstimation?: CostEstimation;
  tokenStats?: TokenStats;
  realtimeMetrics?: RealtimeMetrics;
  clusterStatus?: ClusterStatus;
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
      <div className="liquid-glass-card rounded-3xl p-5 border border-white/15 shadow-2xl flex flex-col gap-4">
        <div className="flex items-center gap-2.5 border-b border-white/10 pb-3">
          <div className="p-2 rounded-xl bg-amber-500/20 border border-amber-500/30 text-amber-300">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Optimizer Telemetry</h2>
            <p className="text-[11px] text-slate-400">Pre-flight cost & latency estimates</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-2xl bg-white/5 border border-white/10 flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
              <Clock className="w-3.5 h-3.5 text-indigo-400" />
              <span>Est. Latency</span>
            </div>
            <span className="text-base font-bold text-slate-100 font-mono">
              {costEstimation?.runtime ? `${costEstimation.runtime}s` : '0.000s'}
            </span>
          </div>

          <div className="p-3 rounded-2xl bg-white/5 border border-white/10 flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
              <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
              <span>Est. Cost</span>
            </div>
            <span className="text-base font-bold text-slate-100 font-mono">
              {costEstimation?.cost ? `$${costEstimation.cost}` : '$0.0000'}
            </span>
          </div>

          <div className="p-3 rounded-2xl bg-white/5 border border-white/10 flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
              <Zap className="w-3.5 h-3.5 text-purple-400" />
              <span>Est. Tokens</span>
            </div>
            <span className="text-base font-bold text-slate-100 font-mono">
              {costEstimation?.tokens ? `${costEstimation.tokens}` : '0'}
            </span>
          </div>

          <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-emerald-300 text-[11px]">
              <TrendingDown className="w-3.5 h-3.5" />
              <span>Token Savings</span>
            </div>
            <span className="text-base font-bold text-emerald-300 font-mono">
              {tokenStats?.savings_percentage ? `${tokenStats.savings_percentage}%` : '0.0%'}
            </span>
          </div>
        </div>
      </div>

      <div className="liquid-glass-card rounded-3xl p-5 border border-white/15 shadow-2xl flex flex-col gap-4">
        <div className="flex items-center gap-2.5 border-b border-white/10 pb-3">
          <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-300">
            <Server className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Active Cluster Nodes</h2>
            <p className="text-[11px] text-slate-400">Distributed runtime worker pool</p>
          </div>
        </div>

        <div className="flex flex-col gap-2 max-h-[180px] overflow-y-auto pr-1">
          {onlineWorkers.length > 0 ? (
            onlineWorkers.map((workerId, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 rounded-2xl bg-white/5 border border-white/10 hover:border-indigo-500/30 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                  <span className="text-xs font-semibold font-mono text-slate-200">{workerId}</span>
                </div>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wide">
                  Online
                </span>
              </div>
            ))
          ) : (
            <div className="p-4 text-center text-xs text-slate-400 bg-white/5 rounded-2xl border border-white/5">
              No cluster workers registered. Defaulting to local AdaptiveRuntime.
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="liquid-glass-card rounded-2xl p-4 border border-white/15 flex flex-col items-center justify-center text-center gap-1">
          <span className="text-[11px] font-medium text-slate-400">Completed Nodes</span>
          <span className="text-2xl font-black text-indigo-300 font-mono">
            {realtimeMetrics ? `${realtimeMetrics.completed_nodes} / ${realtimeMetrics.total_nodes}` : '0 / 0'}
          </span>
        </div>

        <div className="liquid-glass-card rounded-2xl p-4 border border-white/15 flex flex-col items-center justify-center text-center gap-1">
          <div className="flex items-center gap-1 text-[11px] font-medium text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Cluster Health</span>
          </div>
          <span className="text-2xl font-black text-emerald-400 font-mono">100%</span>
        </div>
      </div>
    </div>
  );
};
