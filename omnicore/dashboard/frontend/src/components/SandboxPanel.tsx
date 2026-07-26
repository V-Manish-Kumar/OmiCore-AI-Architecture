import React, { useState } from 'react';
import { Play, Sparkles, Sliders } from 'lucide-react';
import { askPuterGemini } from '../services/puterService';

interface SandboxPanelProps {
  onRunQuery: (query: string) => void;
  isExecuting: boolean;
}

const SAMPLE_PROMPTS = [
  "Search Google for ML tools and compile PDF report.",
  "Create pdf with reasearch help of gemini.",
  "Scrape web news articles and build summary slides."
];

export const SandboxPanel: React.FC<SandboxPanelProps> = ({ onRunQuery, isExecuting }) => {
  const [query, setQuery] = useState(
    "Search Google for ML tools and compile PDF report."
  );
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
    <div className="liquid-glass-card rounded-3xl p-6 flex flex-col gap-5 border border-white/15 shadow-2xl relative overflow-hidden">
      <div className="absolute -top-24 -right-24 w-48 h-48 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-300">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Natural Language Sandbox</h2>
            <p className="text-[11px] text-slate-400">Compile prompt into Task IR & LLVM DAG</p>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-slate-300 text-xs font-mono">
          <Sliders className="w-3.5 h-3.5 text-indigo-400" />
          <span>{wordCount} words (~{estimatedTokens} tokens)</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={3}
            placeholder="Type your intent query here (e.g. Search Python packages and generate summary report)..."
            className="w-full p-4 rounded-2xl bg-slate-900/60 border border-white/10 text-slate-100 text-sm placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20 backdrop-blur-md resize-none transition-all"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] text-slate-400 font-medium mr-1">Presets:</span>
          {SAMPLE_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setQuery(prompt)}
              className="px-3 py-1 rounded-xl text-[11px] font-medium bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 transition-colors text-left truncate max-w-xs"
            >
              {prompt}
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between pt-2">
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
            className="flex items-center gap-2 px-4 py-2.5 rounded-2xl text-xs font-bold bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 transition-all cursor-pointer"
          >
            {isPuterThinking ? (
              <span className="w-3.5 h-3.5 rounded-full border-2 border-indigo-400/40 border-t-indigo-300 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            Puter Gemini AI Assist
          </button>

          <button
            type="submit"
            disabled={isExecuting || !query.trim()}
            className={`liquid-button flex items-center gap-2.5 px-6 py-2.5 rounded-2xl text-xs font-bold text-white transition-all ${
              isExecuting ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
            }`}
          >
            {isExecuting ? (
              <>
                <span className="w-4 h-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                Compiling & Scheduling...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                Compile & Run Execution
              </>
            )}
          </button>
        </div>

        {puterAnalysis && (
          <div className="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-200 text-xs font-mono flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-indigo-400">Puter Gemini 2.0 Flash Understanding:</span>
            <span>{puterAnalysis}</span>
          </div>
        )}

      </form>
    </div>
  );
};
