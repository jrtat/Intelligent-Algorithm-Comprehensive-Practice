import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import jobsData from '../../data/jobs.json';
import type { Job } from '../../types/job';

const JobProfile = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<Job | null>(null);

  useEffect(() => {
    if (jobId) {
      const foundJob = (Object.values(jobsData) as Job[]).find((j) => j.岗位编码 === jobId);
      if (foundJob) {
        setJob(foundJob);
      }
    }
  }, [jobId]);

  if (!job) {
    return <div>岗位数据加载中...</div>;
  }

  const getRadarOption = () => {
    const maxScore = 5;
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: ['能力评分'],
        bottom: '5%'
      },
      radar: {
        shape: 'circle',
        center: ['50%', '55%'],
        radius: '70%',
        splitNumber: 5,
        axisLine: {
          lineStyle: {
            color: '#e0e0e0'
          }
        },
        splitLine: {
          lineStyle: {
            color: '#e0e0e0'
          }
        },
        splitArea: {
          areaStyle: {
            color: 'rgba(128, 128, 128, 0.1)',
            opacity: 0.1
          }
        },
        indicator: [
          { name: '沟通能力', max: maxScore },
          { name: '学习能力', max: maxScore },
          { name: '抗压能力', max: maxScore },
          { name: '创新能力', max: maxScore },
          { name: '实习能力', max: maxScore }
        ]
      },
      series: [
        {
          type: 'radar',
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            width: 3,
            color: '#4f46e5'
          },
          areaStyle: {
            color: 'rgba(79, 70, 229, 0.3)'
          },
          data: [
            {
              value: [
                job.沟通能力,
                job.学习能力,
                job.抗压能力,
                job.创新能力,
                job.实习能力
              ],
              name: job.岗位名称
            }
          ]
        }
      ]
    };
  };

  return (
    <div className="job-profile-container">
      <div className="job-profile-header">
        <h2>{job.岗位名称} - 岗位画像</h2>
        <p className="job-profile-subtitle">
          岗位编码: {job.岗位编码} | 薪资范围: {job.薪资范围.split('元')[0]}
        </p>
      </div>

      <div className="job-profile-content">
        <div className="profile-section radar-section">
          <h3>能力维度雷达图</h3>
          <div className="radar-chart-container">
            <ReactECharts option={getRadarOption()} style={{ height: '500px', width: '100%' }} />
          </div>
        </div>

        <div className="profile-section details-section">
          <h3>岗位详情</h3>
          <div className="detail-item">
            <span className="detail-label">学历要求:</span>
            <span className="detail-value">{job.学历要求}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">工作地址:</span>
            <span className="detail-value">{job.地址}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">能力评分:</span>
            <div className="ability-grid">
              <div className="ability-item">
                沟通: <strong>{job.沟通能力}</strong>
              </div>
              <div className="ability-item">
                学习: <strong>{job.学习能力}</strong>
              </div>
              <div className="ability-item">
                抗压: <strong>{job.抗压能力}</strong>
              </div>
              <div className="ability-item">
                创新: <strong>{job.创新能力}</strong>
              </div>
              <div className="ability-item">
                实习: <strong>{job.实习能力}</strong>
              </div>
            </div>
          </div>
          <div className="detail-item">
            <span className="detail-label">职业技能:</span>
            <div className="skills-tags">
              {job.职业技能.map((skill, index) => (
                <span key={index} className="skill-tag">
                  {skill}
                </span>
              ))}
            </div>
          </div>
          <div className="detail-item">
            <span className="detail-label">职位晋升:</span>
            <div className="skills-tags">
              {job.职位晋升.map((path, index) => (
                <span key={index} className="skill-tag">
                  {path}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobProfile;
