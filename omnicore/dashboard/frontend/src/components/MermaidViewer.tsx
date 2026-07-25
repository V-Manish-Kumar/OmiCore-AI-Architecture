import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { RefreshCw, Code2, AlertTriangle } from 'lucide-react';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  themeVariables: {
    darkMode: true,
    background: 'transparent',
    primaryColor: '#6366f1',
    primaryTextColor: '#f8fafc',
    primaryBorderColor: '#818cf8',
    lineColor: '#a5b4fc',
    secondaryColor: '#334155',
    tertiaryColor: '#1e293b'
  }
});

interface MermaidViewerProps {
  chart: string;
  id: string;
  emptyMessage?: string;
}

export const MermaidViewer: React.FC<MermaidViewerProps> = ({ chart, id, emptyMessage = 'No graph data to render' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    if (!chart || chart.trim() === '') {
      setSvgContent('');
      setError(null);
      return;
    }

    const renderChart = async () => {
      setLoading(true);
      setError(null);
      try {
        const uniqueId = `mermaid_${id}_${Math.random().toString(36).substring(2, 9)}`;
        const { svg } = await mermaid.render(uniqueId, chart);
        if (isMounted) {
          setSvgContent(svg);
          setLoading(false);
        }
      } catch (err: any) {
        if (isMounted) {
          console.error('Mermaid render error:', err);
          setError(err.message || 'Failed to render Mermaid diagram');
          setLoading(false);
        }
      }
    };

    renderChart();

    return () => {
      isMounted = false;
    };
  }, [chart, id]);

  if (!chart || chart.trim() === '') {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[220px] text-slate-400 gap-3">
        <Code2 className="w-8 h-8 opacity-40 text-indigo-400" />
        <span className="text-xs font-medium tracking-wide">{emptyMessage}</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[220px] text-rose-400 gap-2 p-4 text-center">
        <AlertTriangle className="w-6 h-6 opacity-80" />
        <span className="text-xs font-semibold">Diagram Render Issue</span>
        <span className="text-[11px] opacity-75 font-mono max-w-md break-all">{error}</span>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full min-h-[260px] flex items-center justify-center p-4 overflow-auto">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-950/40 backdrop-blur-sm z-10">
          <RefreshCw className="w-6 h-6 text-indigo-400 animate-spin" />
        </div>
      )}
      <div
        ref={containerRef}
        className="mermaid-svg-container w-full h-full flex items-center justify-center [&_svg]:max-w-full [&_svg]:h-auto [&_svg]:drop-shadow-[0_10px_20px_rgba(0,0,0,0.5)]"
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    </div>
  );
};
