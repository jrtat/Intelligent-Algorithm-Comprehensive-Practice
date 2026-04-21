import { Link } from 'react-router-dom';
import CareerReportComponent from '../components/CareerReport/CareerReport';
import '../components/PageDashboard/page-dashboard.css';

export default function CareerReport() {
  return (
    <div className="page-dashboard">
      {/* Breadcrumb */}
      <div className="dashboard-breadcrumb">
        <span className="breadcrumb-item">
          <Link to="/" className="breadcrumb-link">首页</Link>
          <span className="breadcrumb-sep">/</span>
          <span className="breadcrumb-current">职业报告</span>
        </span>
      </div>

      {/* Main Content */}
      <div className="dashboard-content">
        <CareerReportComponent />
      </div>
    </div>
  );
}
