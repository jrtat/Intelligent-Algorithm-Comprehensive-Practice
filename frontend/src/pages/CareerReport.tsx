import { Link } from 'react-router-dom';
import CareerReportComponent from '../components/CareerReport/CareerReport';
import './career-report-page.css';

export default function CareerReport() {
  return (
    <div className="career-report-page">
      {/* Breadcrumb */}
      <div className="career-report-breadcrumb">
        <span className="breadcrumb-item">
          <Link to="/" className="breadcrumb-link">首页</Link>
          <span className="breadcrumb-sep">/</span>
          <span className="breadcrumb-current">职业报告</span>
        </span>
      </div>

      {/* Main Content */}
      <div className="career-report-content">
        <CareerReportComponent />
      </div>
    </div>
  );
}