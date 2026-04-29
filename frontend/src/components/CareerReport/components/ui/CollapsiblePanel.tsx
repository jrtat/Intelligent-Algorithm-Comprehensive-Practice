import { useState, useEffect } from 'react';
import type { ReactNode } from 'react';

interface CollapsiblePanelProps {
  title: string;
  subtitle?: string;
  defaultExpanded?: boolean;
  forceExpanded?: boolean;
  children: ReactNode;
  onEdit?: () => void;
  onAIPolish?: () => void;
}

export function CollapsiblePanel({
  title,
  subtitle,
  defaultExpanded = false,
  forceExpanded = false,
  children,
  onEdit,
  onAIPolish,
}: CollapsiblePanelProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [isPrinting, setIsPrinting] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('print');
    const handleChange = () => setIsPrinting(mediaQuery.matches);
    setIsPrinting(mediaQuery.matches);
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const isExpanded = forceExpanded || isPrinting || expanded;

  return (
    <div className="collapsible-panel">
      <div
        className="collapsible-header"
        onClick={() => setExpanded(!expanded)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setExpanded(!expanded)}
      >
        <div>
          <span className="collapsible-title">{title}</span>
          {subtitle && (
            <span style={{ marginLeft: 8, fontSize: 12, color: '#999' }}>
              {subtitle}
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {isExpanded && (onEdit || onAIPolish) && (
            <div
              style={{ display: 'flex', gap: 4 }}
              onClick={(e) => e.stopPropagation()}
            >
              {onEdit && (
                <button className="btn-icon" onClick={onEdit}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>edit</span>
                </button>
              )}
              {onAIPolish && (
                <button className="btn-icon" onClick={onAIPolish}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#FF9F43' }}>auto_fix_high</span>
                </button>
              )}
            </div>
          )}
          <span className="material-symbols-outlined" style={{ fontSize: 20 }}>
            {isExpanded ? 'expand_less' : 'expand_more'}
          </span>
        </div>
      </div>

      {isExpanded && <div className="collapsible-content">{children}</div>}
    </div>
  );
}
