import { useMemo } from 'react';
import { Link, useParams } from 'react-router-dom';
import jobsData from '../../data/jobs.json';
import { AbilityBar } from './AbilityBar';
import './job-detail.css';

export function JobDetailPage() {
  const { jobId } = useParams<{ jobId: string }>();

  const job = useMemo(() => {
    return jobsData[jobId as keyof typeof jobsData];
  }, [jobId]);

  if (!job) {
    return (
      <div className="app">
        <p className="empty">未找到该岗位信息</p>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="job-detail-page">
        <Link to="/dashboard" className="back-btn">← 返回列表</Link>

        <div className="job-card">
          <div className="job-header">
            <h3 className="job-title">{job.岗位名称}</h3>
            <span className="job-salary">{job.薪资范围}</span>
          </div>
          <div className="job-info">
            <span className="company">{job.公司名称}</span>
            <span className="location">{job.地址}</span>
          </div>
          <div className="job-tags">
            {job.学历要求 !== '无任何要求' && (
              <span className="tag tag-edu">{job.学历要求}</span>
            )}
          </div>

          <div className="ability-section">
            <h4>能力等级要求</h4>
            <AbilityBar label="沟通能力" level={job.沟通能力} />
            <AbilityBar label="学习能力" level={job.学习能力} />
            <AbilityBar label="抗压能力" level={job.抗压能力} />
            <AbilityBar label="创新能力" level={job.创新能力} />
            <AbilityBar label="实习能力" level={job.实习能力} />
          </div>

          <div className="job-actions">
            <Link to="/summary" state={{ jobName: job.岗位名称 }} className="action-btn">查看岗位画像</Link>
            <Link to="/map" state={{ jobName: job.岗位名称 }} className="action-btn">查看地图分布</Link>
          </div>
        </div>

        <div className="job-detail-full">
          <h2>岗位详情</h2>
          <p className="job-desc">{job.岗位详情}</p>

          {job.职业技能.length > 0 && (
            <div className="job-section">
              <h3>职业技能</h3>
              <div className="skill-list">
                {job.职业技能.map((skill, i) => (
                  <span key={i} className="skill-tag">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {job.证书要求.length > 0 && (
            <div className="job-section">
              <h3>证书要求</h3>
              <div className="skill-list">
                {job.证书要求.map((cert, i) => (
                  <span key={i} className="skill-tag">{cert}</span>
                ))}
              </div>
            </div>
          )}

          {job.职位晋升.length > 0 && (
            <div className="job-section">
              <h3>职位晋升</h3>
              <div className="skill-list">
                {job.职位晋升.map((path, i) => (
                  <span key={i} className="skill-tag">{path}</span>
                ))}
              </div>
            </div>
          )}

          <a
            href={job.岗位来源地址}
            target="_blank"
            rel="noopener noreferrer"
            className="job-link"
          >
            查看原始链接 →
          </a>
        </div>
      </div>
    </div>
  );
}
