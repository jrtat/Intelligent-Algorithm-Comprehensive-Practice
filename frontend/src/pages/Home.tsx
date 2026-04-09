import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <header className="home-header">
        <h1>岗位大数据分析平台</h1>
        <p>探索岗位分布、能力画像与市场趋势</p>
      </header>

      <div className="home-grid">
        <div className="home-card" onClick={() => navigate('/dashboard')}>
          <div className="home-card-content">
            <h3>岗位看板</h3>
            <p>查看实时岗位列表、筛选及基本统计数据</p>
          </div>
        </div>
        <div className="home-card" onClick={() => navigate('/profile-list')}>
          <div className="home-card-content">
            <h3>岗位画像</h3>
            <p>选择岗位类型查看整体能力画像与统计分析</p>
          </div>
        </div>
        <div className="home-card" onClick={() => navigate('/map')}>
          <div className="home-card-content">
            <h3>岗位坐标</h3>
            <p>在地图上直观查看不同岗位的地理分布情况</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
