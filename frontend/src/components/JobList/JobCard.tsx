import { Link } from 'react-router-dom';
import type { Job } from '../../types/job.ts';

interface JobCardProps {
  job: Job;
}

export function JobCard({ job }: JobCardProps) {
  return (
    <Link to={`/${job.岗位编码}`} className="job-card-link">
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
          {job.沟通能力 > 0 && (
            <span className="tag tag-skill">沟通 Lv.{job.沟通能力}</span>
          )}
          {job.学习能力 > 0 && (
            <span className="tag tag-skill">学习 Lv.{job.学习能力}</span>
          )}
          {job.抗压能力 > 0 && (
            <span className="tag tag-skill">抗压 Lv.{job.抗压能力}</span>
          )}
          {job.创新能力 > 0 && (
            <span className="tag tag-skill">创新 Lv.{job.创新能力}</span>
          )}
          {job.实习能力 > 0 && (
            <span className="tag tag-skill">实习 Lv.{job.实习能力}</span>
          )}
        </div>
      </div>
    </Link>
  );
}
