import { useReport } from '../context/ReportContext';

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

  const handleToggle = () => {
    dispatch({ type: 'TOGGLE_SIDEBAR' });
  };

  const handleNavClick = (id: string) => {
    scrollToSection(id);
  };

  return (
    <>
      <aside className={`report-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
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

        <div className="sidebar-footer">
          <div
            className="sidebar-nav-item"
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && alert('AI润色记录功能开发中')}
            onClick={() => alert('AI润色记录功能开发中')}
          >
            <span className="material-symbols-outlined">history</span>
            <span>AI润色记录</span>
          </div>
        </div>
      </aside>

      <button
        className={`sidebar-toggle ${sidebarCollapsed ? 'collapsed' : ''}`}
        onClick={handleToggle}
        aria-label={sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'}
      >
        <span className="material-symbols-outlined">
          {sidebarCollapsed ? 'chevron_right' : 'chevron_left'}
        </span>
      </button>
    </>
  );
}
