import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const scrollToSection = (id: string) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
};

const NAV_SECTIONS = [
  { id: 'hero', label: '首页' },
  { id: 'market', label: '就业市场' },
  { id: 'ability', label: '能力分析' },
  { id: 'report', label: '职业报告' },
];

const Home = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('hero');
  const [navVisible, setNavVisible] = useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // 监听滚动，控制导航栏显示/隐藏
  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      // Hero（60px）之后显示导航栏
      setNavVisible(scrollY > window.innerHeight * 0.5);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // IntersectionObserver 监听当前可见 section
  useEffect(() => {
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      {
        root: null,
        rootMargin: '-40% 0px -40% 0px',
        threshold: 0,
      }
    );

    NAV_SECTIONS.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) observerRef.current?.observe(el);
    });

    return () => observerRef.current?.disconnect();
  }, []);

  return (
    <div className="home-page">
      {/* ===== 顶部浮动导航栏（仅后三页显示） ===== */}
      <nav className={`top-nav ${navVisible ? 'visible' : ''}`}>
        <div className="top-nav-inner">
          {NAV_SECTIONS.map((s) => (
            <button
              key={s.id}
              className={`nav-btn ${activeSection === s.id ? 'active' : ''}`}
              onClick={() => scrollToSection(s.id)}
            >
              {s.label}
            </button>
          ))}
        </div>
      </nav>

      {/* ===== 模块一：Hero ===== */}
      <section className="hero-section" id="hero">
        <div className="hero-content">
          <div className="hero-badge">✨ AI 驱动 · 智能规划</div>
          <h1 className="hero-title">基于 AI 的大学生职业规划智能体</h1>
          <p className="hero-subtitle">
            从岗位大数据出发，洞察市场趋势，分析个人能力，<br />
            生成专属职业生涯发展报告
          </p>

          {/* 三个跳转卡片 */}
          <div className="hero-features">
            <div className="hero-feature-card" onClick={() => scrollToSection('market')}>
              <span className="hero-feature-icon">📊</span>
              <span className="hero-feature-num">01</span>
              <span className="hero-feature-title">快速了解就业市场需求</span>
              <span className="hero-feature-desc">实时岗位分布、薪资行情、企业用人偏好</span>
              <span className="hero-feature-arrow">→</span>
            </div>

            <div className="hero-feature-card" onClick={() => scrollToSection('ability')}>
              <span className="hero-feature-icon">🎯</span>
              <span className="hero-feature-num">02</span>
              <span className="hero-feature-title">分析自身就业能力与意愿</span>
              <span className="hero-feature-desc">多维度能力评估，找到最适合你的方向</span>
              <span className="hero-feature-arrow">→</span>
            </div>

            <div className="hero-feature-card" onClick={() => scrollToSection('report')}>
              <span className="hero-feature-icon">📋</span>
              <span className="hero-feature-num">03</span>
              <span className="hero-feature-title">生成职业生涯发展报告</span>
              <span className="hero-feature-desc">AI 智能生成个性化职业发展路径规划</span>
              <span className="hero-feature-arrow">→</span>
            </div>
          </div>
        </div>
      </section>

      {/* ===== 模块二：快速了解就业市场需求 ===== */}
      <section className="market-section" id="market">
        <div className="section-card market-card">
          <div className="section-card-header">
            <span className="section-card-num color-blue">01</span>
            <div>
              <h2 className="section-card-title">快速了解就业市场需求</h2>
              <p className="section-card-desc">从多角度洞察市场行情</p>
            </div>
          </div>
          <div className="feature-row">
            <div className="feature-item" onClick={() => navigate('/dashboard')}>
              <span className="feature-item-icon">📋</span>
              <span className="feature-item-title">岗位看板</span>
              <span className="feature-item-desc">实时岗位列表，多维度筛选，查看统计数据</span>
              <span className="feature-item-link">进入 →</span>
            </div>
            <div className="feature-item" onClick={() => navigate('/profile-list')}>
              <span className="feature-item-icon">👤</span>
              <span className="feature-item-title">岗位画像</span>
              <span className="feature-item-desc">选择岗位类型，查看整体能力画像与统计分析</span>
              <span className="feature-item-link">进入 →</span>
            </div>
            <div className="feature-item" onClick={() => navigate('/map')}>
              <span className="feature-item-icon">🗺️</span>
              <span className="feature-item-title">岗位地图</span>
              <span className="feature-item-desc">在地图上直观查看不同岗位的地理分布情况</span>
              <span className="feature-item-link">进入 →</span>
            </div>
          </div>
        </div>
      </section>

      {/* ===== 模块三：分析自身就业能力与意愿 ===== */}
      <section className="ability-section" id="ability">
        <div className="section-card ability-card">
          <div className="section-card-header">
            <span className="section-card-num color-teal">02</span>
            <div>
              <h2 className="section-card-title">分析自身就业能力与意愿</h2>
              <p className="section-card-desc">多维度评估，找到最适合你的方向</p>
            </div>
          </div>
          <div className="placeholder-row">
            <div className="placeholder-item">
              <div className="placeholder-item-icon">🔍</div>
              <div className="placeholder-item-title">能力测评</div>
              <div className="placeholder-item-desc">AI 多维度能力评估</div>
            </div>
            <div className="placeholder-item">
              <div className="placeholder-item-icon">⚡</div>
              <div className="placeholder-item-title">意愿匹配</div>
              <div className="placeholder-item-desc">基于兴趣与价值观匹配</div>
            </div>
            <div className="placeholder-item">
              <div className="placeholder-item-icon">🚀</div>
              <div className="placeholder-item-title">竞争力分析</div>
              <div className="placeholder-item-desc">与目标岗位对比分析</div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== 模块四：生成职业生涯发展报告 ===== */}
      <section className="report-section" id="report">
        <div className="section-card report-card">
          <div className="section-card-header">
            <span className="section-card-num color-violet">03</span>
            <div>
              <h2 className="section-card-title">生成职业生涯发展报告</h2>
              <p className="section-card-desc">AI 智能生成专属职业发展路径规划</p>
            </div>
          </div>
          <div className="placeholder-row single">
            <div className="placeholder-item large">
              <div className="placeholder-item-icon">📑</div>
              <div className="placeholder-item-title">职业报告生成器</div>
              <div className="placeholder-item-desc">输入背景与目标，获取专属职业规划方案</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
