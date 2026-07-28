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
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
      <div className="lg:col-span-6 flex flex-col gap-5">
        <section className="panel p-5 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
            <div className="flex items-center gap-3">
              <div className="icon-tile">
                <BarChart2 className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Profiler</h3>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">Phase timings and plan cache</p>
              </div>
            </div>

            <button type="button" onClick={fetchData} className="btn-secondary p-2" aria-label="Refresh">
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {[
              {
                label: 'Avg parsing',
                value: profilerReport?.phase_metrics?.average_parsing_seconds
                  ? `${profilerReport.phase_metrics.average_parsing_seconds.toFixed(4)}s`
                  : '0.000s'
              },
              {
                label: 'Avg optimization',
                value: profilerReport?.phase_metrics?.average_optimization_seconds
                  ? `${profilerReport.phase_metrics.average_optimization_seconds.toFixed(4)}s`
                  : '0.000s'
              },
              { label: 'Cache hits', value: String(profilerReport?.caching?.hits ?? 0) },
              {
                label: 'Hit rate',
                value: profilerReport?.caching?.hit_rate
                  ? `${(profilerReport.caching.hit_rate * 100).toFixed(1)}%`
                  : '0.0%'
              }
            ].map(({ label, value }) => (
              <div key={label} className="panel-muted p-3 flex flex-col gap-0.5">
                <span className="text-xs text-zinc-500 dark:text-zinc-400">{label}</span>
                <span className="text-lg font-semibold font-mono tabular-nums text-zinc-900 dark:text-zinc-100">
                  {value}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="lg:col-span-6 flex flex-col gap-5">
        <section className="panel p-5 flex flex-col gap-4 min-h-[320px]">
          <div className="flex items-center gap-3 border-b border-zinc-200 dark:border-zinc-800 pb-3">
            <div className="icon-tile">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Trace spans</h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">Recent compilation and execution spans</p>
            </div>
          </div>

          <div className="flex flex-col gap-1.5 max-h-[280px] overflow-y-auto">
            {traces && traces.length > 0 ? (
              traces.map((span, idx) => (
                <div
                  key={idx}
                  className="panel-muted px-3 py-2.5 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-400 shrink-0" />
                    <div className="min-w-0">
                      <div className="font-medium text-zinc-900 dark:text-zinc-200 truncate">{span.name}</div>
                      <div className="text-[11px] text-zinc-500 font-mono">Phase: {span.phase}</div>
                    </div>
                  </div>
                  <span className="font-mono text-[11px] tabular-nums text-zinc-600 dark:text-zinc-300 shrink-0 ml-2">
                    {span.duration_ms ? `${span.duration_ms}ms` : '0ms'}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-zinc-500 text-center py-8 panel-muted rounded-lg">No spans recorded yet.</p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};
