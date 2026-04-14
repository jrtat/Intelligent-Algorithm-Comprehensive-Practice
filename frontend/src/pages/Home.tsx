import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const scrollToSection = (id: string) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
};

const NAV_SECTIONS = [
  { id: 'hero', label: '首页' },
  { id: 'insight', label: '岗位洞察' },
  { id: 'eval', label: '能力测评' },
  { id: 'report', label: '专属报告' },
];

const Home = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('hero');

  // 各板块可见状态（用于触发进入动画，离开后重置，再次进入可重播）
  const [insightVisible, setInsightVisible] = useState(false);
  const [evalVisible, setEvalVisible] = useState(false);
  const [reportVisible, setReportVisible] = useState(false);

  // 板块 ref
  const insightSectionRef = useRef<HTMLElement>(null);
  const evalSectionRef = useRef<HTMLElement>(null);
  const reportSectionRef = useRef<HTMLElement>(null);

  // 监听滚动，控制导航栏当前激活项
  useEffect(() => {
    const observer = new IntersectionObserver(
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
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  // 监听三个板块的可见性，用于触发入场动画（支持离开后重置，再次进入重播）
  useEffect(() => {
    const sections = [
      { ref: insightSectionRef, setVisible: setInsightVisible },
      { ref: evalSectionRef, setVisible: setEvalVisible },
      { ref: reportSectionRef, setVisible: setReportVisible },
    ];

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const target = entry.target as HTMLElement;
          const section = sections.find((s) => s.ref.current === target);
          if (section) {
            // 进入视口时设为 true，离开时设为 false，确保每次进入都播放动画
            section.setVisible(entry.isIntersecting);
          }
        });
      },
      { threshold: 0.2 }
    );

    sections.forEach(({ ref }) => {
      if (ref.current) observer.observe(ref.current);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <div className="home-page">
      {/* ===== 固定导航栏 ===== */}
      <nav className="top-nav">
        <div className="top-nav-inner">
          <div className="nav-logo">AI 职业规划</div>
          <div className="nav-links">
            {NAV_SECTIONS.map((s) => (
              <span
                key={s.id}
                className={`nav-link ${activeSection === s.id ? 'active' : ''}`}
                onClick={() => scrollToSection(s.id)}
              >
                {s.label}
              </span>
            ))}
          </div>
          <button className="nav-cta" onClick={() => scrollToSection('eval')}>
            立即测评
          </button>
          <button className="nav-menu-btn">☰</button>
        </div>
      </nav>

      {/* ===== 板块一：Hero 首屏 ===== */}
      <section className="hero-section" id="hero">
        <div className="hero-bg" />
        <div className="hero-content">
          <div className="hero-badge">✨ AI 驱动 · 智能规划</div>
          <h1 className="hero-title">
            AI 精准测评，让职业选择<span className="highlight">更简单</span>
          </h1>
          <p className="hero-subtitle">
            基于AI大数据，精准匹配你的能力、兴趣与岗位需求，告别迷茫，
            解锁专属职业方向——无需复杂思考，一键测评，直达适配路径。
          </p>
          <button className="hero-cta" onClick={() => scrollToSection('eval')}>
            立即测评
          </button>
          <p className="hero-hint">测评免费 · 报告精准 · 隐私保护</p>
        </div>
        <div className="hero-scroll-hint">
          <span>向下滑动</span>
          <span className="hero-scroll-icon">↓</span>
        </div>
      </section>

      {/* ===== 板块二：全景洞察岗位 ===== */}
      <section
        className={`insight-section ${insightVisible ? 'section-visible' : ''}`}
        id="insight"
        ref={insightSectionRef}
      >
        <div className="section-container">
          <div className="section-header">
            <h2 className="section-title">全景洞察岗位，看清细节与发展关系</h2>
            <div className="section-title-underline" />
            <p className="section-desc">
              覆盖全行业AI相关岗位，拆解岗位职责、技能要求、薪资范围、晋升路径，
              用数据帮你看清岗位本质，避开选择误区。
            </p>
          </div>

          <div className="insight-grid">
            <div className="feature-card" onClick={() => navigate('/dashboard')}>
              <div className="feature-icon">📊</div>
              <h3 className="feature-title">岗位看板</h3>
              <p className="feature-desc">
                实时更新全行业AI相关岗位动态、薪资波动、招聘热度，一目了然
              </p>
              <span className="feature-link">进入 →</span>
            </div>
            <div className="feature-card" onClick={() => navigate('/profile-list')}>
              <div className="feature-icon">👤</div>
              <h3 className="feature-title">岗位画像</h3>
              <p className="feature-desc">
                拆解岗位核心职责、技能要求、任职门槛，精准呈现岗位核心特质
              </p>
              <span className="feature-link">进入 →</span>
            </div>
            <div className="feature-card" onClick={() => navigate('/map')}>
              <div className="feature-icon">🗺️</div>
              <h3 className="feature-title">岗位地图</h3>
              <p className="feature-desc">
                可视化展现岗位全国分布，清晰了解职业地区差异与机会
              </p>
              <span className="feature-link">进入 →</span>
            </div>
          </div>
        </div>
      </section>

      {/* ===== 板块三：科学测评 ===== */}
      <section
        className={`eval-section ${evalVisible ? 'section-visible' : ''}`}
        id="eval"
        ref={evalSectionRef}
      >
        <div className="section-container">
          <div className="section-header">
            <h2 className="section-title">科学测评实力，找到最适配你的岗位</h2>
            <div className="section-title-underline" />
          </div>

          <div className="eval-container">
            {/* 左侧功能区 */}
            <div className="eval-text">
              <div className="eval-card" onClick={() => navigate('/capability-analysis')}>
                <h3>🔬 能力测评</h3>
                <p>
                  多维度拆解个人能力，涵盖专业技能、通用能力、潜力特质三大核心维度，
                  通过科学题库与AI分析，精准量化个人能力短板与优势，拒绝模糊判断。
                </p>
                <span className="eval-card-link">开始测评 →</span>
              </div>

              <div className="eval-card" onClick={() => navigate('/job-match')}>
                <h3>🎯 岗位匹配</h3>
                <p>
                  基于能力测评结果，结合千万级岗位数据库，AI智能匹配岗位适配度，
                  生成适配排名，标注适配亮点与改进方向，帮你快速锁定最适合的岗位。
                </p>
                <span className="eval-card-link">立即匹配 →</span>
              </div>
            </div>

            {/* 右侧图片区域（占位） */}
            <div className="eval-visual">
              <div className="eval-visual-placeholder">
                <span>测评流程示意图位置</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== 板块四：专属报告 ===== */}
      <section
        className={`report-section ${reportVisible ? 'section-visible' : ''}`}
        id="report"
        ref={reportSectionRef}
      >
        <div className="section-container">
          <div className="section-header">
            <h2 className="section-title">定制你的专属报告，解锁清晰职业路径</h2>
            <div className="section-title-underline" />
            <p className="section-desc">
              一份专属报告，涵盖你的测评分析、岗位适配排名、能力提升建议、
              长期职业规划，帮你从"迷茫"到"清晰"，一步到位。
            </p>
          </div>

          <div className="report-card-inner">
            <div className="report-modules">
              <div className="report-module">
                <div className="report-module-icon">📋</div>
                <div className="report-module-title">能力测评总结</div>
              </div>
              <div className="report-module">
                <div className="report-module-icon">🎯</div>
                <div className="report-module-title">岗位适配分析</div>
              </div>
              <div className="report-module">
                <div className="report-module-icon">💡</div>
                <div className="report-module-title">专属改进建议</div>
              </div>
            </div>
            <div className="report-actions">
              <button
                className="report-cta"
                onClick={() => navigate('/career-report')}
              >
                立即获取专属报告
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ===== Footer ===== */}
      <footer className="home-footer">
        <div className="footer-content">
          <span>© 2026 AI 职业规划智能体</span>
          <a href="#">隐私政策</a>
          <a href="#">使用条款</a>
          <a href="#">联系我们</a>
        </div>
      </footer>
    </div>
  );
};

export default Home;