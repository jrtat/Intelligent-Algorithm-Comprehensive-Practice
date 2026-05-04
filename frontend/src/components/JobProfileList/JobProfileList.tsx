import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import jobsData from '../../data/jobs.json';
import type { Job } from '../../types/job.ts';
import './JobProfileList.css';

export function JobProfileList() {
  const navigate = useNavigate();

  // 提取唯一岗位名称及其数量
  const jobNameStats = useMemo(() => {
    const stats: Record<string, { count: number; jobs: Job[] }> = {};
    Object.values(jobsData as Record<string, Job>).forEach((job) => {
      if (!stats[job.岗位名称]) {
        stats[job.岗位名称] = { count: 0, jobs: [] };
      }
      stats[job.岗位名称].count++;
      stats[job.岗位名称].jobs.push(job);
    });
    return Object.entries(stats)
      .map(([name, data]) => ({ name, count: data.count, jobs: data.jobs }))
      .sort((a, b) => b.count - a.count);
  }, []);

  return (
    <div className="app">
      <div className="profile-list-page">
        <h2>选择岗位类型</h2>
        <p className="subtitle">点击岗位名称查看其整体能力画像</p>
        <div className="job-name-grid">
          {jobNameStats.map(({ name, count }) => (
            <div
              key={name}
              className="job-name-card"
              onClick={() => navigate('/profile-list/' + encodeURIComponent(name))}
            >
              <h3>{name}</h3>
              <p>{count} 个岗位</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
