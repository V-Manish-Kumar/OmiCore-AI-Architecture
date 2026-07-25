import React, { useEffect, useRef } from 'react';
import { Terminal as TerminalIcon, Trash2, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

interface TerminalLogsProps {
  logs: string[];
  status?: 'compiling' | 'running' | 'completed' | 'failed' | 'idle';
  onClearLogs?: () => void;
}

export const TerminalLogs: React.FC<TerminalLogsProps> = ({ logs, status = 'idle', onClearLogs }) => {
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="liquid-glass-card rounded-3xl p-5 border border-white/15 shadow-2xl flex flex-col gap-3 min-h-[220px]">
      {/* macOS Terminal Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
          </div>

          <div className="flex items-center gap-2">
            <TerminalIcon className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-bold font-mono text-slate-200">Linter Console & Execution Logs</h3>
          </div>
        </div>

        {/* Status Pill & Clear */}
        <div className="flex items-center gap-2">
          {status === 'compiling' && (
            <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px] font-bold uppercase tracking-wider">
              <Loader2 className="w-3 h-3 animate-spin text-indigo-400" />
              Compiling
            </span>
          )}
          {status === 'running' && (
            <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold uppercase tracking-wider">
              <Loader2 className="w-3 h-3 animate-spin text-amber-400" />
              Running DAG
            </span>
          )}
          {status === 'completed' && (
            <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold uppercase tracking-wider">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              Completed
            </span>
          )}
          {status === 'failed' && (
            <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[10px] font-bold uppercase tracking-wider">
              <AlertCircle className="w-3 h-3 text-rose-400" />
              Failed
            </span>
          )}

          {onClearLogs && (
            <button
              onClick={onClearLogs}
              className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-slate-200 border border-white/10 transition-colors"
              title="Clear Console"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Terminal Code Content */}
      <div className="flex-1 bg-slate-950/80 rounded-2xl p-4 border border-white/10 font-mono text-xs overflow-y-auto max-h-[220px] flex flex-col gap-1.5 leading-relaxed selection:bg-emerald-500/30">
        {logs && logs.length > 0 ? (
          logs.map((log, index) => {
            let textColor = 'text-slate-300';
            if (log.includes('ERROR') || log.includes('failed')) textColor = 'text-rose-400 font-semibold';
            else if (log.includes('completed successfully') || log.includes('COMPLETED')) textColor = 'text-emerald-400 font-semibold';
            else if (log.includes('started execution')) textColor = 'text-amber-300';
            else if (log.includes('Running Intent') || log.includes('Running LLVM')) textColor = 'text-indigo-300';

            return (
              <div key={index} className={`${textColor} break-all font-mono tracking-tight flex items-start gap-2`}>
                <span className="opacity-40 select-none text-slate-500">{index + 1}</span>
                <span>{log}</span>
              </div>
            );
          })
        ) : (
          <div className="text-slate-500 italic select-none">
            &gt; Linter console ready. Waiting for compilation run...
          </div>
        )}
        <div ref={terminalEndRef} />
      </div>
    </div>
  );
};
