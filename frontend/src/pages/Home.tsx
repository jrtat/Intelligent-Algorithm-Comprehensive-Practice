import { useNavigate } from 'react-router-dom';
import './Home.css';

const scrollToSection = (id: string) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
};

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      {/* ===== 板块一：英雄区 Hero ===== */}
      <section className="hero-section" id="hero">
        {/* 装饰性浮动元素 */}
        <div className="floating-shape shape-1" />
        <div className="floating-shape shape-2" />
        <div className="floating-shape shape-3" />

        <div className="hero-content">
          <div className="hero-badge">✨ AI 驱动 · 智能规划</div>
          <h1 className="hero-title">基于 AI 的大学生<br />职业规划智能体</h1>
          <p className="hero-subtitle">
            从岗位大数据出发，洞察市场趋势，分析个人能力，<br />
            生成专属职业生涯发展报告
          </p>

          <div className="hero-features">
            <div
              className="hero-feature-card"
              onClick={() => scrollToSection('market')}
            >
              <div className="hero-feature-icon">📊</div>
              <div className="hero-feature-text">
                <span className="hero-feature-num">01</span>
                <h3>快速了解就业市场需求</h3>
                <p>实时岗位分布、薪资行情、企业用人偏好</p>
              </div>
              <div className="hero-feature-arrow">→</div>
            </div>

            <div
              className="hero-feature-card"
              onClick={() => scrollToSection('ability')}
            >
              <div className="hero-feature-icon">🎯</div>
              <div className="hero-feature-text">
                <span className="hero-feature-num">02</span>
                <h3>分析自身就业能力与意愿</h3>
                <p>多维度能力评估，找到最适合你的岗位方向</p>
              </div>
              <div className="hero-feature-arrow">→</div>
            </div>

            <div
              className="hero-feature-card"
              onClick={() => scrollToSection('report')}
            >
              <div className="hero-feature-icon">📋</div>
              <div className="hero-feature-text">
                <span className="hero-feature-num">03</span>
                <h3>生成职业生涯发展报告</h3>
                <p>AI 智能生成个性化职业发展路径规划</p>
              </div>
              <div className="hero-feature-arrow">→</div>
            </div>
          </div>
        </div>

        <div className="scroll-hint" onClick={() => scrollToSection('market')}>
          <span>向下滚动探索</span>
          <div className="scroll-arrow">↓</div>
        </div>
      </section>

      {/* ===== 板块二：快速了解就业市场需求 ===== */}
      <section className="market-section" id="market">
        <div className="section-header">
          <span className="section-tag">模块一</span>
          <h2>快速了解就业市场需求</h2>
          <p>从岗位分布、能力画像、地理行情多角度洞察市场</p>
        </div>

        <div className="feature-grid">
          <div className="feature-card" onClick={() => navigate('/dashboard')}>
            <div className="feature-card-icon">📋</div>
            <div className="feature-card-body">
              <h3>岗位看板</h3>
              <p>实时岗位列表，支持多维度筛选，查看基本统计数据</p>
            </div>
            <div className="feature-card-footer">
              <span className="feature-enter">进入功能</span>
              <span className="feature-arrow">→</span>
            </div>
          </div>

          <div className="feature-card" onClick={() => navigate('/profile-list')}>
            <div className="feature-card-icon">👤</div>
            <div className="feature-card-body">
              <h3>岗位画像</h3>
              <p>选择岗位类型，查看整体能力画像与统计分析</p>
            </div>
            <div className="feature-card-footer">
              <span className="feature-enter">进入功能</span>
              <span className="feature-arrow">→</span>
            </div>
          </div>

          <div className="feature-card" onClick={() => navigate('/map')}>
            <div className="feature-card-icon">🗺️</div>
            <div className="feature-card-body">
              <h3>岗位地图</h3>
              <p>在地图上直观查看不同岗位的地理分布情况</p>
            </div>
            <div className="feature-card-footer">
              <span className="feature-enter">进入功能</span>
              <span className="feature-arrow">→</span>
            </div>
          </div>
        </div>
      </section>

      {/* ===== 板块三：分析自身就业能力与意愿 ===== */}
      <section className="ability-section" id="ability">
        <div className="section-header">
          <span className="section-tag">模块二</span>
          <h2>分析自身就业能力与意愿</h2>
          <p>多维度评估个人竞争力，找到最适合你的发展方向</p>
        </div>

        <div className="placeholder-grid">
          <div className="placeholder-card">
            <div className="placeholder-icon">🔍</div>
            <h3>能力测评</h3>
            <p>即将上线 · AI 驱动的多维度能力评估</p>
          </div>
          <div className="placeholder-card">
            <div className="placeholder-icon">⚡</div>
            <h3>意愿匹配</h3>
            <p>即将上线 · 基于兴趣与价值观的岗位匹配</p>
          </div>
          <div className="placeholder-card">
            <div className="placeholder-icon">🚀</div>
            <h3>竞争力分析</h3>
            <p>即将上线 · 与目标岗位要求对比分析</p>
          </div>
        </div>
      </section>

      {/* ===== 板块四：生成职业生涯发展报告 ===== */}
      <section className="report-section" id="report">
        <div className="section-header">
          <span className="section-tag">模块三</span>
          <h2>生成职业生涯发展报告</h2>
          <p>AI 智能分析，生成专属个性化职业发展路径规划</p>
        </div>

        <div className="placeholder-grid single">
          <div className="placeholder-card large">
            <div className="placeholder-icon large">📑</div>
            <h3>职业报告生成器</h3>
            <p>即将上线 · 输入你的背景与目标，获取专属职业规划方案</p>
            <button className="placeholder-btn" disabled>功能开发中</button>
          </div>
        </div>
      </section>

      {/* 底部留白 */}
      <footer className="home-footer">
        <p>基于 AI 的大学生职业规划智能体 · 2026</p>
      </footer>
    </div>
  );
};

export default Home;
