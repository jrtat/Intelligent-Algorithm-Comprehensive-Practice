import { useReport } from '../context/ReportContext';
import { useEffect, useState } from 'react';

interface SidebarItem {
  id: string;
  label: string;
  icon: string;
}

const SIDEBAR_ITEMS: SidebarItem[] = [
  { id: 'basic-info', label: '基础信息', icon: 'person' },
  { id: 'candidate-summary', label: '候选人总结', icon: 'summarize' },
  { id: 'match-analysis', label: '匹配分析', icon: 'trending_up' },
  { id: 'gap-analysis', label: '差距分析', icon: 'analytics' },
  { id: 'career-path', label: '职业路径', icon: 'route' },
  { id: 'development-plan', label: '发展计划', icon: 'timeline' },
  { id: 'action-plan', label: '行动计划', icon: 'checklist' },
  { id: 'final-recommendation', label: '最终建议', icon: 'lightbulb' },
];

export function ReportSidebar() {
  const { state, dispatch, scrollToSection } = useReport();
  const { sidebarCollapsed, activeSection } = state;
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleToggle = () => {
    dispatch({ type: 'TOGGLE_SIDEBAR' });
  };

  const handleNavClick = (id: string) => {
    scrollToSection(id);
    if (isMobile && !sidebarCollapsed) {
      dispatch({ type: 'TOGGLE_SIDEBAR' });
    }
  };

  return (
    <>
      {/* Mobile overlay */}
      {isMobile && !sidebarCollapsed && (
        <div
          className="fixed inset-0 z-[99] bg-black/50"
          onClick={() => dispatch({ type: 'TOGGLE_SIDEBAR' })}
        />
      )}

      <aside
        className={`report-sidebar fixed z-[100] flex flex-col bg-white transition-all duration-300 ${
          sidebarCollapsed
            ? isMobile
              ? '-translate-x-full'
              : 'left-0 w-0 overflow-hidden'
            : isMobile
              ? 'translate-x-0'
              : 'left-0 w-[240px]'
        }`}
        style={{
          top: '60px',
          height: 'calc(100vh - 60px)',
          borderRight: sidebarCollapsed && !isMobile ? 'none' : '1px solid #DCDCDC',
        }}
      >
        <nav className="flex-1 overflow-y-auto !py-8">
          {SIDEBAR_ITEMS.map((item) => (
            <div
              key={item.id}
              className={`flex cursor-pointer items-center gap-3 !px-6 !py-4 transition-all hover:bg-[#E8F4F8] ${
                activeSection === item.id
                  ? 'border-l-[4px] bg-[#E8F4F8] font-medium text-[24px]'
                  : 'border-l-[4px] border-transparent text-[16px]'
              }`}
              style={{ color: activeSection === item.id ? '#1677ff' : '#666' }}
              onClick={() => handleNavClick(item.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleNavClick(item.id)}
            >
              <span className="material-symbols-outlined text-[24px]">{item.icon}</span>
              <span>{item.label}</span>
            </div>
          ))}
        </nav>
        <div className="border-t border-[#DCDCDC] !px-6 !py-4">
          <span className="text-[12px] text-[#999]">v1.0</span>
        </div>
      </aside>

      {/* PC toggle button */}
      {!isMobile && (
        <button
          className={`sidebar-toggle fixed z-[101] flex h-10 w-6 cursor-pointer items-center justify-center rounded-r-lg border border-l-0 bg-white shadow-sm transition-all duration-300 hover:bg-gray-50 ${
            sidebarCollapsed ? 'left-0' : 'left-[240px]'
          }`}
          style={{ top: '50%', transform: 'translateY(-50%)' }}
          onClick={handleToggle}
          aria-label={sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'}
        >
          <span className="material-symbols-outlined text-[18px]" style={{ color: '#666' }}>
            {sidebarCollapsed ? 'chevron_right' : 'chevron_left'}
          </span>
        </button>
      )}
    </>
  );
}