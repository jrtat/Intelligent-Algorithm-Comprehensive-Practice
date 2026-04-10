import { useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import jobsData from '../../data/jobs.json';
import type { Job } from '../../types/job';
import './JobProfileDetail.css';

export function JobProfileDetail() {
  const { jobName } = useParams<{ jobName: string }>();
  const decodedJobName = decodeURIComponent(jobName || '');

  // 获取同岗位名称的所有岗位
  const similarJobs = useMemo(() => {
    return Object.values(jobsData as Record<string, Job>).filter(
      (j) => j.岗位名称 === decodedJobName
    );
  }, [decodedJobName]);

  // 聚合计算平均值
  const aggregatedScores = useMemo(() => {
    if (similarJobs.length === 0) return null;
    return {
      沟通能力: Math.round(similarJobs.reduce((sum, j) => sum + j.沟通能力, 0) / similarJobs.length),
      学习能力: Math.round(similarJobs.reduce((sum, j) => sum + j.学习能力, 0) / similarJobs.length),
      抗压能力: Math.round(similarJobs.reduce((sum, j) => sum + j.抗压能力, 0) / similarJobs.length),
      创新能力: Math.round(similarJobs.reduce((sum, j) => sum + j.创新能力, 0) / similarJobs.length),
      实习能力: Math.round(similarJobs.reduce((sum, j) => sum + j.实习能力, 0) / similarJobs.length),
    };
  }, [similarJobs]);

  // 薪资统计
  const salaryStats = useMemo(() => {
    if (similarJobs.length === 0) return { min: 0, max: 0 };
    const salaries = similarJobs.flatMap((j) => j.月薪范围);
    return {
      min: Math.min(...salaries),
      max: Math.max(...salaries),
    };
  }, [similarJobs]);

  if (similarJobs.length === 0) {
    return (
      <div className="app">
        <p className="empty">未找到该岗位的画像数据</p>
      </div>
    );
  }

  const radarOption = {
    tooltip: {
      trigger: 'item',
    },
    legend: {
      data: ['能力评分'],
      bottom: '5%',
    },
    radar: {
      shape: 'circle',
      center: ['50%', '55%'],
      radius: '65%',
      splitNumber: 5,
      axisLine: {
        lineStyle: { color: '#e0e0e0' },
      },
      splitLine: {
        lineStyle: { color: '#e0e0e0' },
      },
      splitArea: {
        areaStyle: { color: ['rgba(128, 128, 128, 0.1)'] },
      },
      indicator: [
        { name: '沟通能力', max: 5 },
        { name: '学习能力', max: 5 },
        { name: '抗压能力', max: 5 },
        { name: '创新能力', max: 5 },
        { name: '实习能力', max: 5 },
      ],
    },
    series: [
      {
        type: 'radar',
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#4f46e5' },
        areaStyle: { color: 'rgba(79, 70, 229, 0.3)' },
        data: [
          {
            value: [
              aggregatedScores!.沟通能力,
              aggregatedScores!.学习能力,
              aggregatedScores!.抗压能力,
              aggregatedScores!.创新能力,
              aggregatedScores!.实习能力,
            ],
            name: decodedJobName,
          },
        ],
      },
    ],
  };

  return (
    <div className="app">
      <div className="profile-detail-page">
        <Link to="/profile-list" className="back-btn">← 返回岗位列表</Link>
        <h2>{decodedJobName} - 整体画像</h2>
        <p className="subtitle">基于 {similarJobs.length} 个岗位数据聚合分析</p>

        <div className="profile-detail-content">
          <div className="profile-card radar-card">
            <h3>能力维度雷达图</h3>
            <ReactECharts option={radarOption} style={{ height: '400px', width: '100%' }} />
          </div>

          <div className="profile-card stats-card">
            <h3>统计概览</h3>
            <div className="stat-item">
              <span className="stat-label">样本数量</span>
              <span className="stat-value">{similarJobs.length} 个岗位</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">平均沟通能力</span>
              <span className="stat-value">{aggregatedScores!.沟通能力}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">平均学习能力</span>
              <span className="stat-value">{aggregatedScores!.学习能力}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">平均抗压能力</span>
              <span className="stat-value">{aggregatedScores!.抗压能力}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">平均创新能力</span>
              <span className="stat-value">{aggregatedScores!.创新能力}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">平均实习能力</span>
              <span className="stat-value">{aggregatedScores!.实习能力}</span>
            </div>
            <div className="stat-item salary">
              <span className="stat-label">月薪范围</span>
              <span className="stat-value">¥{salaryStats.min} - ¥{salaryStats.max}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
