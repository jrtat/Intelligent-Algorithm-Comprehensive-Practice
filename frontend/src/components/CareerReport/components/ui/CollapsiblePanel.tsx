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
    <div className="mb-3 overflow-hidden rounded-lg border border-[#DCDCDC]">
      <div
        className="flex cursor-pointer items-center justify-between bg-[#F5F7FA] !px-4 !py-4 transition-colors hover:bg-[#E8F4F8]"
        onClick={() => setExpanded(!expanded)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setExpanded(!expanded)}
      >
        <div className="flex items-center gap-138">
          <span className="text-[15px] font-medium text-[#333]">{title}</span>
          {subtitle && (
            <span className="text-[12px] text-[#999]">{subtitle}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {isExpanded && (onEdit || onAIPolish) && (
            <div
              className="flex gap-1"
              onClick={(e) => e.stopPropagation()}
            >
              {onEdit && (
                <button className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-[#1677ff]/10">
                  <span className="material-symbols-outlined text-[15px]" style={{ color: '#666' }}>edit</span>
                </button>
              )}
              {onAIPolish && (
                <button className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-[#FF9F43]/10">
                  <span className="material-symbols-outlined text-[15px]" style={{ color: '#FF9F43' }}>auto_fix_high</span>
                </button>
              )}
            </div>
          )}
          <span className="material-symbols-outlined text-[20px]">
            {isExpanded ? 'expand_less' : 'expand_more'}
          </span>
        </div>
      </div>

      {isExpanded && <div className="bg-white !px-2 !py-4">{children}</div>}
    </div>
  );
}