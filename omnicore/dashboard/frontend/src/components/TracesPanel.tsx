import React, { useEffect, useState } from 'react';
import type { ProfilerReport } from '../types';
import { Zap, RefreshCw, BarChart2, CheckCircle2 } from 'lucide-react';

export const TracesPanel: React.FC = () => {
  const [profilerReport, setProfilerReport] = useState<ProfilerReport | null>(null);
  const [traces, setTraces] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [profRes, traceRes] = await Promise.all([
        fetch('/api/profiler').then((r) => r.json()),
        fetch('/api/traces').then((r) => r.json())
      ]);
      setProfilerReport(profRes);
      setTraces(traceRes || []);
    } catch (err) {
      console.error('Failed to fetch profiler data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-6 flex flex-col gap-5">
        <div className="liquid-glass-card rounded-3xl p-5 border border-white/15 shadow-2xl flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-purple-500/20 border border-purple-500/30 text-purple-300">
                <BarChart2 className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-100">Performance Profiler Report</h2>
                <p className="text-[11px] text-slate-400">Compilation phase timing metrics & caching</p>
              </div>
            </div>

            <button
              onClick={fetchData}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 flex flex-col gap-1">
              <span className="text-[11px] text-slate-400">Avg Parsing Duration</span>
              <span className="text-xl font-bold font-mono text-indigo-300">
                {profilerReport?.phase_metrics?.average_parsing_seconds
                  ? `${profilerReport.phase_metrics.average_parsing_seconds.toFixed(4)}s`
                  : '0.000s'}
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 flex flex-col gap-1">
              <span className="text-[11px] text-slate-400">Avg Optimization Duration</span>
              <span className="text-xl font-bold font-mono text-purple-300">
                {profilerReport?.phase_metrics?.average_optimization_seconds
                  ? `${profilerReport.phase_metrics.average_optimization_seconds.toFixed(4)}s`
                  : '0.000s'}
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 flex flex-col gap-1">
              <span className="text-[11px] text-slate-400">Plan Cache Hits</span>
              <span className="text-xl font-bold font-mono text-emerald-400">
                {profilerReport?.caching?.hits ?? 0}
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 flex flex-col gap-1">
              <span className="text-[11px] text-slate-400">Cache Hit Rate</span>
              <span className="text-xl font-bold font-mono text-emerald-400">
                {profilerReport?.caching?.hit_rate
                  ? `${(profilerReport.caching.hit_rate * 100).toFixed(1)}%`
                  : '0.0%'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="lg:col-span-6 flex flex-col gap-5">
        <div className="liquid-glass-card rounded-3xl p-5 border border-white/15 shadow-2xl flex flex-col gap-4 min-h-[340px]">
          <div className="flex items-center gap-2.5 border-b border-white/10 pb-3">
            <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-300">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-100">Compiler Telemetry Traces</h2>
              <p className="text-[11px] text-slate-400">Execution span logs & phase details</p>
            </div>
          </div>

          <div className="flex flex-col gap-2.5 max-h-[280px] overflow-y-auto pr-1">
            {traces && traces.length > 0 ? (
              traces.map((span, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-2.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <div>
                      <div className="font-bold text-slate-200">{span.name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">Phase: {span.phase}</div>
                    </div>
                  </div>
                  <span className="font-mono text-xs font-bold text-indigo-300 bg-indigo-500/10 px-2.5 py-1 rounded-xl border border-indigo-500/20">
                    {span.duration_ms ? `${span.duration_ms}ms` : '0ms'}
                  </span>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-xs text-slate-400 bg-white/5 rounded-2xl border border-white/5">
                No active execution spans logged yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
