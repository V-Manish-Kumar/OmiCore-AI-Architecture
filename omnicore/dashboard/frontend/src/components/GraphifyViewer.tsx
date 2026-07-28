import React, { useState } from 'react';
import { Share2, RefreshCw } from 'lucide-react';

export const GraphifyViewer: React.FC = () => {
  const [key, setKey] = useState<number>(0);

  return (
    <div className="flex flex-col gap-4 w-full">
      <div className="panel px-4 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="icon-tile">
            <Share2 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Knowledge graph</h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Served from graphify-out via /api/graphify_html</p>
          </div>
        </div>

        <button type="button" onClick={() => setKey((prev) => prev + 1)} className="btn-secondary shrink-0">
          <RefreshCw className="w-3.5 h-3.5" />
          Reload
        </button>
      </div>

      <div className="panel overflow-hidden p-0">
        <iframe
          key={key}
          src="/api/graphify_html"
          title="Graphify Knowledge Graph"
          className="w-full h-[calc(100vh-220px)] min-h-[560px] border-none bg-zinc-950"
        />
      </div>
    </div>
  );
};
