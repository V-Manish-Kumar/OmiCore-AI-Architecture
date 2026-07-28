import React, { useCallback, useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import {
  RefreshCw,
  GitGraph,
  AlertTriangle,
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
  Copy,
  Check
} from 'lucide-react';
import { buildMermaidConfig } from '../lib/mermaidConfig';
import { useDashboardTheme } from '../hooks/useDashboardTheme';

export interface MermaidViewerProps {
  chart: string;
  id: string;
  emptyMessage?: string;
  /** Shown in the diagram toolbar */
  title?: string;
  /** Extra vertical space for dense graphs (e.g. Graphify KG) */
  density?: 'normal' | 'large';
  /** Inset layout for split comparison panes */
  frame?: 'canvas' | 'inset';
}

const MIN_ZOOM = 0.35;
const MAX_ZOOM = 2.5;
const ZOOM_STEP = 0.15;

function clampZoom(value: number) {
  return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, value));
}

/** Refine Mermaid SVG output for consistent product-grade rendering. */
function polishRenderedSvg(host: HTMLDivElement | null) {
  if (!host) return;
  const svg = host.querySelector('svg');
  if (!svg) return;

  svg.setAttribute('role', 'img');
  svg.style.maxWidth = 'none';

  host.querySelectorAll('.node rect').forEach((node) => {
    node.setAttribute('rx', '8');
    node.setAttribute('ry', '8');
  });

  host.querySelectorAll('.edgePath path, .flowchart-link').forEach((path) => {
    path.setAttribute('stroke-width', '1.25');
  });

  host.querySelectorAll('.edgeLabel rect').forEach((labelBg) => {
    labelBg.setAttribute('rx', '4');
    labelBg.setAttribute('ry', '4');
  });
}

export const MermaidViewer: React.FC<MermaidViewerProps> = ({
  chart,
  id,
  emptyMessage = 'No graph data to render',
  title,
  density = 'normal',
  frame = 'canvas'
}) => {
  const theme = useDashboardTheme();
  const viewportRef = useRef<HTMLDivElement>(null);
  const svgHostRef = useRef<HTMLDivElement>(null);

  const [svgContent, setSvgContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    mermaid.initialize(buildMermaidConfig(theme));
  }, [theme]);

  useEffect(() => {
    let isMounted = true;

    if (!chart || chart.trim() === '') {
      setSvgContent('');
      setError(null);
      setLoading(false);
      return;
    }

    const renderChart = async () => {
      setLoading(true);
      setError(null);
      try {
        mermaid.initialize(buildMermaidConfig(theme));
        const uniqueId = `mermaid_${id}_${Math.random().toString(36).substring(2, 9)}`;
        const { svg } = await mermaid.render(uniqueId, chart);
        if (isMounted) {
          setSvgContent(svg);
          setZoom(1);
          setLoading(false);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const message = err instanceof Error ? err.message : 'Failed to render diagram';
          console.error('Mermaid render error:', err);
          setError(message);
          setLoading(false);
        }
      }
    };

    renderChart();
    return () => {
      isMounted = false;
    };
  }, [chart, id, theme]);

  const fitToWidth = useCallback(() => {
    const host = svgHostRef.current;
    const viewport = viewportRef.current;
    if (!host || !viewport) return;
    const svg = host.querySelector('svg');
    if (!svg) return;

    const viewW = viewport.clientWidth - 48;
    const attrW = svg.width?.baseVal?.value || parseFloat(svg.getAttribute('width') || '0');
    let bboxW = attrW;
    if (!bboxW) {
      try {
        bboxW = svg.getBBox().width;
      } catch {
        return;
      }
    }
    if (bboxW <= 0 || viewW <= 0) return;
    setZoom(clampZoom(viewW / bboxW));
  }, []);

  useEffect(() => {
    if (!svgContent || loading) return;
    const t = window.requestAnimationFrame(() => {
      polishRenderedSvg(svgHostRef.current);
      fitToWidth();
    });
    return () => window.cancelAnimationFrame(t);
  }, [svgContent, loading, fitToWidth]);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (!e.ctrlKey && !e.metaKey) return;
    e.preventDefault();
    setZoom((z) => clampZoom(z + (e.deltaY < 0 ? ZOOM_STEP : -ZOOM_STEP)));
  }, []);

  const copySource = async () => {
    if (!chart.trim()) return;
    try {
      await navigator.clipboard.writeText(chart);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable */
    }
  };

  const minHeight =
    frame === 'inset' ? 'min-h-[240px]' : density === 'large' ? 'min-h-[420px]' : 'min-h-[320px]';

  if (!chart || chart.trim() === '') {
    return (
      <div
        className={`mermaid-empty flex flex-col items-center justify-center w-full ${minHeight} rounded-lg border border-dashed border-zinc-300 dark:border-zinc-700 bg-zinc-100/50 dark:bg-zinc-900/40`}
      >
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-200/80 dark:bg-zinc-800 mb-2">
          <GitGraph className="w-5 h-5 text-zinc-400" strokeWidth={1.5} />
        </div>
        <p className="text-sm font-medium text-zinc-600 dark:text-zinc-300">No diagram yet</p>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 max-w-xs text-center px-4">{emptyMessage}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className={`mermaid-empty flex flex-col items-center justify-center w-full ${minHeight} rounded-lg border border-red-500/20 bg-red-500/5 p-4 text-center`}
      >
        <AlertTriangle className="w-5 h-5 text-red-500 mb-2" />
        <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">Diagram could not be rendered</p>
        <p className="text-[11px] text-zinc-500 font-mono mt-2 max-w-lg break-all">{error}</p>
      </div>
    );
  }

  const zoomLabel = `${Math.round(zoom * 100)}%`;

  return (
    <div
      className={`mermaid-frame flex flex-col w-full h-full ${frame === 'inset' ? 'rounded-md' : 'rounded-lg'} overflow-hidden border border-zinc-200 dark:border-zinc-800 bg-[var(--mermaid-canvas)]`}
    >
      <div className="mermaid-toolbar flex items-center justify-between gap-2 px-2.5 py-1.5 border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/90 dark:bg-zinc-900/90 shrink-0">
        <div className="flex items-center gap-2 min-w-0">
          <GitGraph className="w-3.5 h-3.5 text-zinc-400 shrink-0" strokeWidth={1.75} />
          <span className="text-xs font-medium text-zinc-700 dark:text-zinc-200 truncate">
            {title ?? 'Mermaid diagram'}
          </span>
        </div>

        <div className="flex items-center gap-0.5 shrink-0">
          <span className="hidden sm:inline text-[10px] tabular-nums text-zinc-500 dark:text-zinc-400 w-9 text-right mr-1">
            {zoomLabel}
          </span>
          <ToolbarBtn onClick={() => setZoom((z) => clampZoom(z - ZOOM_STEP))} label="Zoom out">
            <ZoomOut className="w-3.5 h-3.5" />
          </ToolbarBtn>
          <ToolbarBtn onClick={() => setZoom((z) => clampZoom(z + ZOOM_STEP))} label="Zoom in">
            <ZoomIn className="w-3.5 h-3.5" />
          </ToolbarBtn>
          <ToolbarBtn onClick={fitToWidth} label="Fit to width">
            <Maximize2 className="w-3.5 h-3.5" />
          </ToolbarBtn>
          <ToolbarBtn onClick={() => setZoom(1)} label="Reset zoom">
            <RotateCcw className="w-3.5 h-3.5" />
          </ToolbarBtn>
          <span className="w-px h-4 bg-zinc-200 dark:bg-zinc-700 mx-0.5" />
          <ToolbarBtn onClick={copySource} label="Copy Mermaid source">
            {copied ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
          </ToolbarBtn>
        </div>
      </div>

      <div
        ref={viewportRef}
        onWheel={handleWheel}
        className={`mermaid-viewport relative flex-1 overflow-auto ${minHeight} mermaid-dot-grid`}
        title="Ctrl + scroll to zoom"
      >
        {loading && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-2 bg-zinc-100/80 dark:bg-zinc-950/80 backdrop-blur-[1px]">
            <RefreshCw className="w-5 h-5 text-zinc-400 animate-spin" />
            <span className="text-xs text-zinc-500">Rendering diagram…</span>
          </div>
        )}

        <div className="mermaid-viewport-inner flex min-h-full min-w-full items-start justify-center p-6">
          <div
            ref={svgHostRef}
            className="mermaid-svg-host origin-top transition-transform duration-150 ease-out"
            style={{ transform: `scale(${zoom})` }}
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        </div>
      </div>
    </div>
  );
};

function ToolbarBtn({
  children,
  onClick,
  label
}: {
  children: React.ReactNode;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      className="p-1.5 rounded-md text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-200/80 dark:hover:bg-zinc-800 transition-colors"
    >
      {children}
    </button>
  );
}
