import { Link } from 'react-router-dom';
import './page-dashboard.css';

interface PageDashboardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  showBreadcrumb?: boolean;
  breadcrumbItems?: Array<{ label: string; href?: string }>;
}

export function PageDashboard({
  title,
  subtitle,
  children,
  showBreadcrumb = false,
  breadcrumbItems = [],
}: PageDashboardProps) {
  return (
    <div className="page-dashboard">
      {/* Breadcrumb */}
      {showBreadcrumb && breadcrumbItems.length > 0 && (
        <div className="dashboard-breadcrumb">
          {breadcrumbItems.map((item, index) => (
            <span key={index} className="breadcrumb-item">
              {item.href ? (
                <Link to={item.href} className="breadcrumb-link">
                  {item.label}
                </Link>
              ) : (
                <span className="breadcrumb-current">{item.label}</span>
              )}
              {index < breadcrumbItems.length - 1 && (
                <span className="breadcrumb-sep">/</span>
              )}
            </span>
          ))}
        </div>
      )}

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Page Header */}
        <div className="page-header">
          <div className="page-header-text">
            <h1 className="page-title">{title}</h1>
            {subtitle && <p className="page-subtitle">{subtitle}</p>}
          </div>
        </div>

        {/* Page Body */}
        <div className="page-body">
          {children}
        </div>
      </div>
    </div>
  );
}
