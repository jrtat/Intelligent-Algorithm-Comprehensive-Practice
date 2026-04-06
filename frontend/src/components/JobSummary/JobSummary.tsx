import { useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import jobsData from '../../data/jobs.json';
import type { Job } from '../../types/job';
import { AbilityBar } from '../JobDetail/AbilityBar';
import './job-summary.css';

export function JobSummaryPage() {
  const location = useLocation();
  const jobName = useMemo(() => {
    return (location.state as { jobName?: string })?.jobName || '';
  }, [location.state]);

  const similarJobs = useMemo(() => {
    return Object.values(jobsData as Record<string, Job>).filter(j => j.岗位名称 === jobName);
  }, [jobName]);

  if (similarJobs.length === 0) {
    return (
      <div className="app">
        <p className="empty">未找到该岗位的画像数据</p>
      </div>
    );
  }

  const avgCommunication = Math.round(similarJobs.reduce((sum, j) => sum + j.沟通能力, 0) / similarJobs.length);
  const avgLearning = Math.round(similarJobs.reduce((sum, j) => sum + j.学习能力, 0) / similarJobs.length);
  const avgPressure = Math.round(similarJobs.reduce((sum, j) => sum + j.抗压能力, 0) / similarJobs.length);
  const avgInnovation = Math.round(similarJobs.reduce((sum, j) => sum + j.创新能力, 0) / similarJobs.length);
  const avgInternship = Math.round(similarJobs.reduce((sum, j) => sum + j.实习能力, 0) / similarJobs.length);

  const minSalary = Math.min(...similarJobs.map(j => j.月薪范围[0]));
  const maxSalary = Math.max(...similarJobs.map(j => j.月薪范围[1]));

  const degreeCount = useMemo(() => {
    const count: Record<string, number> = {};
    similarJobs.forEach(j => {
      count[j.学历要求] = (count[j.学历要求] || 0) + 1;
    });
    return count;
  }, [similarJobs]);

  return (
    <div className="app">
      <div className="summary-page">
        <Link to="/" className="back-btn">← 返回列表</Link>
        <h2>{jobName} - 岗位画像分析</h2>
        <p className="subtitle">共分析 {similarJobs.length} 条岗位数据</p>

        <div className="summary-card">
          <h3>核心指标</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">平均沟通能力</span>
              <AbilityBar label="" level={avgCommunication} maxLevel={5} />
            </div>
            <div className="summary-item">
              <span className="summary-label">平均学习能力</span>
              <AbilityBar label="" level={avgLearning} maxLevel={5} />
            </div>
            <div className="summary-item">
              <span className="summary-label">平均抗压能力</span>
              <AbilityBar label="" level={avgPressure} maxLevel={5} />
            </div>
            <div className="summary-item">
              <span className="summary-label">平均创新能力</span>
              <AbilityBar label="" level={avgInnovation} maxLevel={5} />
            </div>
            <div className="summary-item">
              <span className="summary-label">平均实习能力</span>
              <AbilityBar label="" level={avgInternship} maxLevel={5} />
            </div>
          </div>
        </div>

        <div className="summary-card">
          <h3>薪资范围</h3>
          <div className="salary-stats">
            <span className="salary-min">¥{minSalary}</span>
            <span className="salary-divider">-</span>
            <span className="salary-max">¥{maxSalary}</span>
          </div>
          <div className="salary-bar">
            <div className="salary-bar-fill" style={{ width: '100%' }}></div>
          </div>
        </div>

        <div className="summary-card">
          <h3>学历要求分布</h3>
          <div className="degree-pie">
            {Object.entries(degreeCount).map(([degree, count]) => {
              const percentage = ((count / similarJobs.length) * 100).toFixed(1);
              return (
                <div key={degree} className="degree-item">
                  <span className="degree-label">{degree}</span>
                  <div className="degree-bar">
                    <div className="degree-fill" style={{ width: `${percentage}%` }}></div>
                  </div>
                  <span className="degree-value">{count} ({percentage}%)</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="summary-card">
          <h3>公司分布</h3>
          <div className="company-list">
            {Array.from(new Set(similarJobs.map(j => j.公司名称))).map((company, i) => (
              <span key={i} className="company-tag">{company}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
