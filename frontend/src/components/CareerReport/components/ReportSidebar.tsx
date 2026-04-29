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
      // 移动端点击导航后自动关闭侧边栏
      dispatch({ type: 'TOGGLE_SIDEBAR' });
    }
  };

  const handleOverlayClick = () => {
    if (isMobile && !sidebarCollapsed) {
      dispatch({ type: 'TOGGLE_SIDEBAR' });
    }
  };

  // 渲染遮罩层（仅移动端且侧边栏展开时显示）
  const renderOverlay = () => {
    if (!isMobile || sidebarCollapsed) return null;
    return <div className="sidebar-overlay" onClick={handleOverlayClick} />;
  };

  return (
    <>
      {renderOverlay()}
      <aside
        className={`report-sidebar ${sidebarCollapsed ? 'collapsed' : ''} ${isMobile ? 'mobile' : ''}`}
      >
        <nav className="sidebar-nav">
          {SIDEBAR_ITEMS.map((item) => (
            <div
              key={item.id}
              className={`sidebar-nav-item ${activeSection === item.id ? 'active' : ''}`}
              onClick={() => handleNavClick(item.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleNavClick(item.id)}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span>{item.label}</span>
            </div>
          ))}
        </nav>
      </aside>
      {/* PC 端的 toggle 按钮 */}
      {!isMobile && (
        <button
          className={`sidebar-toggle ${sidebarCollapsed ? 'collapsed' : ''}`}
          onClick={handleToggle}
          aria-label={sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'}
        >
          <span className="material-symbols-outlined">
            {sidebarCollapsed ? 'chevron_right' : 'chevron_left'}
          </span>
        </button>
      )}
    </>
  );
}