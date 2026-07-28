import React, { useEffect, useRef } from 'react';
import { Terminal as TerminalIcon, Trash2, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

interface TerminalLogsProps {
  logs: string[];
  status?: 'compiling' | 'running' | 'completed' | 'failed' | 'idle';
  onClearLogs?: () => void;
}

const statusBadge: Record<string, { className: string; label: string; icon: React.ReactNode }> = {
  compiling: {
    className: 'bg-amber-500/10 text-amber-700 dark:text-amber-400',
    label: 'Compiling',
    icon: <Loader2 className="w-3 h-3 animate-spin" />
  },
  running: {
    className: 'bg-blue-500/10 text-blue-700 dark:text-blue-400',
    label: 'Running',
    icon: <Loader2 className="w-3 h-3 animate-spin" />
  },
  completed: {
    className: 'bg-green-500/10 text-green-700 dark:text-green-400',
    label: 'Done',
    icon: <CheckCircle2 className="w-3 h-3" />
  },
  failed: {
    className: 'bg-red-500/10 text-red-700 dark:text-red-400',
    label: 'Failed',
    icon: <AlertCircle className="w-3 h-3" />
  }
};

export const TerminalLogs: React.FC<TerminalLogsProps> = ({ logs, status = 'idle', onClearLogs }) => {
  const terminalEndRef = useRef<HTMLDivElement>(null);
  const badge = status !== 'idle' ? statusBadge[status] : null;

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <section className="panel p-5 flex flex-col gap-3 min-h-[200px]">
      <div className="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
        <div className="flex items-center gap-2">
          <TerminalIcon className="w-4 h-4 text-zinc-500" />
          <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Console</h3>
        </div>

        <div className="flex items-center gap-2">
          {badge && (
            <span
              className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-medium ${badge.className}`}
            >
              {badge.icon}
              {badge.label}
            </span>
          )}
          {onClearLogs && (
            <button
              type="button"
              onClick={onClearLogs}
              className="p-1.5 rounded-md text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
              title="Clear console"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      <div className="console-surface flex-1 p-3 text-xs overflow-y-auto max-h-[220px] flex flex-col gap-1 leading-relaxed">
        {logs && logs.length > 0 ? (
          logs.map((log, index) => {
            let textColor = 'text-zinc-400';
            if (log.includes('ERROR') || log.includes('failed')) textColor = 'text-red-400';
            else if (log.includes('completed successfully') || log.includes('COMPLETED'))
              textColor = 'text-green-400';
            else if (log.includes('started execution')) textColor = 'text-amber-300/90';
            else if (log.includes('Running Intent') || log.includes('Running LLVM')) textColor = 'text-blue-300/90';

            return (
              <div key={index} className={`${textColor} break-all flex gap-2`}>
                <span className="text-zinc-600 select-none w-5 shrink-0 text-right tabular-nums">{index + 1}</span>
                <span>{log}</span>
              </div>
            );
          })
        ) : (
          <p className="text-zinc-600">&gt; Waiting for input.</p>
        )}
        <div ref={terminalEndRef} />
      </div>
    </section>
  );
};
