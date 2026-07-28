import { useEffect, useState } from 'react';
import type { DashboardTheme } from '../lib/mermaidConfig';

function readTheme(): DashboardTheme {
  if (typeof document === 'undefined') return 'dark';
  return (
    document.body.classList.contains('light-mode') ||
    document.body.classList.contains('light') ||
    document.documentElement.classList.contains('light-mode') ||
    document.documentElement.classList.contains('light')
  ) ? 'light' : 'dark';
}

export function useDashboardTheme(): DashboardTheme {
  const [theme, setTheme] = useState<DashboardTheme>(readTheme);

  useEffect(() => {
    setTheme(readTheme());
    const observer = new MutationObserver(() => setTheme(readTheme()));
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  return theme;
}
