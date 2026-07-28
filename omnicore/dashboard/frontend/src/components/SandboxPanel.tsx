import React, { useState } from 'react';
import { Play, Terminal, Bot } from 'lucide-react';
import { askPuterGemini } from '../services/puterService';

interface SandboxPanelProps {
  onRunQuery: (query: string) => void;
  isExecuting: boolean;
}

const SAMPLE_PROMPTS = [
  'Search Google for ML tools and compile PDF report.',
  'Create pdf with research help of gemini.',
  'Scrape web news articles and build summary slides.'
];

export const SandboxPanel: React.FC<SandboxPanelProps> = ({ onRunQuery, isExecuting }) => {
  const [query, setQuery] = useState('Search Google for ML tools and compile PDF report.');
  const [isPuterThinking, setIsPuterThinking] = useState(false);
  const [puterAnalysis, setPuterAnalysis] = useState<string | null>(null);

  const wordCount = query.trim() ? query.trim().split(/\s+/).length : 0;
  const estimatedTokens = Math.max(1, Math.round(wordCount * 1.3));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isExecuting) {
      onRunQuery(query.trim());
    }
  };

  return (
    <section className="panel p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="icon-tile">
            <Terminal className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Intent query</h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
              Parsed to AST, optimized DAG, then scheduled on the cluster.
            </p>
          </div>
        </div>
        <span className="text-xs font-mono text-zinc-500 dark:text-zinc-400 tabular-nums shrink-0">
          ~{estimatedTokens} tokens
        </span>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          placeholder="Describe the task you want compiled and executed…"
          className="w-full px-3 py-2.5 rounded-lg text-sm text-zinc-900 dark:text-zinc-50 bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500/50 resize-none transition-shadow"
        />

        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-zinc-500 dark:text-zinc-400">Examples</span>
          {SAMPLE_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setQuery(prompt)}
              className="px-2.5 py-1 rounded-md text-xs text-zinc-600 dark:text-zinc-300 bg-zinc-100 dark:bg-zinc-800/80 hover:bg-zinc-200 dark:hover:bg-zinc-800 border border-transparent hover:border-zinc-300 dark:hover:border-zinc-700 transition-colors truncate max-w-[240px] cursor-pointer"
            >
              {prompt}
            </button>
          ))}
        </div>

        <div className="flex items-center justify-end gap-2 pt-1">
          <button
            type="button"
            onClick={async () => {
              if (!query.trim()) return;
              setIsPuterThinking(true);
              const geminiResult = await askPuterGemini(
                `Rephrase and structure this task into a clean executable command pipeline for compiler execution: "${query}"`
              );
              if (geminiResult) {
                setPuterAnalysis(geminiResult);
              }
              setIsPuterThinking(false);
            }}
            disabled={isPuterThinking || !query.trim()}
            className="btn-secondary disabled:opacity-50"
          >
            {isPuterThinking ? (
              <span className="w-3.5 h-3.5 rounded-full border-2 border-zinc-300 border-t-zinc-600 dark:border-zinc-600 dark:border-t-zinc-300 animate-spin" />
            ) : (
              <Bot className="w-3.5 h-3.5" />
            )}
            Refine
          </button>

          <button type="submit" disabled={isExecuting || !query.trim()} className="btn-primary">
            {isExecuting ? (
              <>
                <span className="w-3.5 h-3.5 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                Running…
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                Compile & run
              </>
            )}
          </button>
        </div>

        {puterAnalysis && (
          <div className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/20 text-zinc-700 dark:text-zinc-200 text-xs leading-relaxed">
            <p className="text-[11px] font-medium text-blue-600 dark:text-blue-400 mb-1">Refined brief</p>
            <p className="font-mono text-[11px]">{puterAnalysis}</p>
          </div>
        )}
      </form>
    </section>
  );
};
