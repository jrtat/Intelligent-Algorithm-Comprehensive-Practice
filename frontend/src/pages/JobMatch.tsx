import { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import jobsData from '../data/jobs.json';
import type { Job, JobData, ResumeData, Report } from '../types/job';
import { processReport } from '../api/reportApi';
import { useToast } from '../context/ToastContext';
import { PageDashboard } from '../components/PageDashboard/PageDashboard';
import './job-match.css';

// 随机推荐同类型岗位组件
interface RecommendedJobsProps {
  jobType: string;
  onSelectJob: (jobId: string) => void;
}

function RecommendedJobs({ jobType, onSelectJob }: RecommendedJobsProps) {
  const allJobs = useMemo(() => Object.values(jobsData as Record<string, Job>), []);

  const recommendedJobs = useMemo(() => {
    const matchedJobs = allJobs.filter(job =>
      job.岗位名称.toLowerCase().includes(jobType.toLowerCase()) ||
      jobType.toLowerCase().includes(job.岗位名称.toLowerCase())
    );
    if (matchedJobs.length <= 5) return matchedJobs;
    const shuffled = [...matchedJobs].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, 5);
  }, [jobType, allJobs]);

  if (recommendedJobs.length === 0) return null;

  return (
    <section className="md:col-span-12 bg-gradient-to-br from-primary/5 via-surface to-secondary/5 !p-6 rounded-2xl ring-1 ring-primary/20 relative overflow-hidden">
      <div className="absolute -right-20 -top-20 w-64 h-64 bg-primary/10 rounded-full blur-3xl"></div>
      <div className="absolute -left-20 -bottom-20 w-64 h-64 bg-secondary/10 rounded-full blur-3xl"></div>
      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-14 h-14 bg-primary rounded-xl flex items-center justify-center text-white shadow-lg shadow-primary/30">
            <span className="material-symbols-outlined text-2xl">recommend</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-on-surface">推荐岗位</h3>
            <p className="text-sm text-on-surface-variant">根据"{jobType}"为您推荐以下岗位</p>
          </div>
        </div>
      <hr className="my-4 border-0 h-px bg-outline-variant/30" />
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {recommendedJobs.map((job) => (
          <button
            key={job.岗位编码}
            onClick={() => onSelectJob(job.岗位编码)}
            className="bg-white/80 !p-4 rounded-xl border border-surface-container-high hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10 transition-all text-left group"
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-bold text-on-surface text-sm line-clamp-1 group-hover:text-primary transition-colors">
                {job.岗位名称}
              </h4>
              <span className="material-symbols-outlined text-primary/50 group-hover:text-primary transition-colors">open_in_new</span>
            </div>
            <p className="text-xs text-on-surface-variant mb-2 line-clamp-1">{job.公司名称}</p>
            <div className="flex items-center gap-2 text-xs text-on-surface-variant">
              <span className="material-symbols-outlined text-sm">location_on</span>
              <span className="line-clamp-1">{job.地址}</span>
            </div>
            <div className="mt-2 text-sm font-bold text-secondary">{job.薪资范围}</div>
          </button>
        ))}
      </div>
      </div>
    </section>
  );
}

export default function JobMatch() {
  const navigate = useNavigate();
  const [selectedJob, setSelectedJob] = useState<JobData | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortConfig, setSortConfig] = useState<{ key: 'match_score', direction: 'asc' | 'desc' } | null>({ key: 'match_score', direction: 'desc' });
  const [jobList, setJobList] = useState<JobData[]>([]);
  const { showToast } = useToast();

  useEffect(() => {
    if (jobList.length > 0) return;
    const savedResult = localStorage.getItem('matchResult');
    if (savedResult) {
      try {
        const parsed = JSON.parse(savedResult);
        setJobList(Array.isArray(parsed) ? parsed : [parsed]);
      } catch (e) {
        console.error('解析匹配结果失败:', e);
      }
    }
  }, []);

  const filteredAndSortedJobs = useMemo(() => {
    if (jobList.length === 0) return [];
    let result = jobList;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(job => job[0].toLowerCase().includes(query));
    }
    if (sortConfig) {
      result.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) return sortConfig.direction === 'asc' ? -1 : 1;
        if (a[sortConfig.key] > b[sortConfig.key]) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    return result;
  }, [jobList, searchQuery, sortConfig]);

  const highestScore = filteredAndSortedJobs.length > 0 ? Math.max(...filteredAndSortedJobs.map(j => j[1])) : 0;

  const handleSort = (key: 'match_score') => {
    let direction: 'asc' | 'desc' = 'desc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'desc') direction = 'asc';
    setSortConfig({ key, direction });
  };

  const handleGetReport = () => {
    if (!selectedJob) return;
    const savedResume = localStorage.getItem('resumeData');
    if (!savedResume) {
      showToast({ message: '请先在能力分析页面填写简历信息', duration: 5000 });
      return;
    }
    let resumeData: ResumeData;
    try {
      resumeData = JSON.parse(savedResume);
    } catch {
      showToast({ message: '简历数据解析失败', duration: 5000 });
      return;
    }
    processReport(
      { resume: resumeData, job: selectedJob },
      {
        onProgress: () => {},
        onCompleted: (result: Report, taskId?: string) => {
          localStorage.setItem('careerReport', JSON.stringify(result));
          if (taskId) localStorage.setItem('reportTaskId', taskId);
          showToast({
            message: '专项提升报告已生成，点击立即查看！',
            onClick: () => navigate('/career-report'),
            duration: 5000,
          });
        },
        onFailed: (err) => showToast({ message: `报告生成失败: ${err}`, duration: 5000 }),
        onTimeout: () => showToast({ message: '任务处理超时，请稍后重试', duration: 5000 }),
      }
    );
    showToast({ message: '正在生成专项提升报告，请稍候...', duration: 3000 });
  };

  if (selectedJob) {
    return (
      <>
        <PageDashboard
          title={`${selectedJob[0]} - 深度解析`}
          subtitle="基于核心算法理解力、产品架构设计及跨团队协作维度的量化对比"
          showBreadcrumb={false}
        >
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* 返回按钮 */}
            <button
              onClick={() => setSelectedJob(null)}
              className="mb-6 flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors group"
            >
              <span className="material-symbols-outlined text-xl group-hover:-translate-x-1 transition-transform">arrow_back</span>
              <span className="font-medium">返回岗位列表</span>
            </button>

            {/* 头部信息 */}
            <div className="mb-6">
            <header className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
              <div className="flex items-center gap-4 !p-6">
                <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center shadow-lg shadow-primary/20">
                  <span className="material-symbols-outlined text-3xl text-white">work</span>
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-on-surface">{selectedJob[0]}</h1>
                  <p className="text-on-surface-variant">人岗匹配深度分析报告</p>
                </div>
              </div>
              <div className="bg-gradient-to-br from-secondary/10 to-primary/5 !p-6 rounded-2xl min-w-[300px] ring-1 ring-secondary/20">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-bold text-on-surface-variant uppercase tracking-wider mb-1">综合匹配度</div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-5xl font-black text-secondary">{selectedJob[1]}</span>
                      <span className="text-xl text-on-surface-variant">分</span>
                    </div>
                  </div>
                  <div className="w-20 h-20 relative">
                    <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 36 36">
                      <path className="stroke-surface-container-highest" strokeWidth="3" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                      <path className="stroke-secondary" strokeWidth="3" strokeLinecap="round" fill="none" strokeDasharray={`${selectedJob[1]}, 100`} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-secondary">TOP</span>
                  </div>
                </div>
              </div>
            </header>
            </div>

            {/* 新布局：专业技能 + 创新能力 (col-6) */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
              {/* 专业技能 */}
              <section className="md:col-span-6 bg-gradient-to-br from-surface-container-lowest to-surface-container-low !p-6 rounded-2xl ring-1 ring-primary/10">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 bg-primary/10 text-primary rounded-xl flex items-center justify-center">
                      <span className="material-symbols-outlined text-2xl">psychology</span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-on-surface">专业技能</h3>
                      <p className="text-sm text-on-surface-variant">对核心技术栈与业务场景的掌握程度</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-4xl font-black text-primary">{selectedJob[2].professional_skill.score}</span>
                    <span className="text-sm text-on-surface-variant"> / 基准 {selectedJob[2].professional_skill.benchmark_score}</span>
                  </div>
                </div>
                
                <hr className="my-4 border-0 h-px bg-outline-variant/30" />

                <div className="mt-8">
                  <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-secondary/5 !p-4 rounded-xl border-l-4 border-secondary">
                    <h4 className="text-sm font-bold text-secondary mb-2 flex items-center gap-2">
                      <span className="material-symbols-outlined text-sm">check_circle</span>
                      匹配理由
                    </h4>
                    <p className="text-sm text-on-surface-variant leading-relaxed">{selectedJob[2].professional_skill.matched_reason}</p>
                  </div>
                  <div className="bg-primary/5 !p-4 rounded-xl border-l-4 border-primary">
                    <h4 className="text-sm font-bold text-primary mb-2 flex items-center gap-2">
                      <span className="material-symbols-outlined text-sm">info</span>
                      提升建议
                    </h4>
                    <p className="text-sm text-on-surface-variant leading-relaxed">{selectedJob[2].professional_skill.missing_reason}</p>
                  </div>
                </div>
                </div>
              </section>

              {/* 创新能力 */}
              <section className="md:col-span-6 bg-gradient-to-br from-surface-container-lowest to-surface-container-low !p-6 rounded-2xl ring-1 ring-secondary/10">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 bg-secondary/10 text-secondary rounded-xl flex items-center justify-center">
                      <span className="material-symbols-outlined text-2xl">lightbulb</span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-on-surface">创新能力</h3>
                      <p className="text-sm text-on-surface-variant">对技术创新与问题解决的思考深度</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-4xl font-black text-secondary">{selectedJob[2].innovation_ability.score}</span>
                    <span className="text-sm text-on-surface-variant"> / 基准 {selectedJob[2].innovation_ability.benchmark_score}</span>
                  </div>
                </div>

                <hr className="my-4 border-0 h-px bg-outline-variant/30" />

                <div className="mt-8">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-secondary/5 !p-4 rounded-xl border-l-4 border-secondary">
                      <h4 className="text-sm font-bold text-secondary mb-2 flex items-center gap-2">
                        <span className="material-symbols-outlined text-sm">check_circle</span>
                        匹配理由
                      </h4>
                      <p className="text-sm text-on-surface-variant leading-relaxed">{selectedJob[2].innovation_ability.matched_reason}</p>
                    </div>
                    <div className="bg-primary/5 !p-4 rounded-xl border-l-4 border-primary">
                      <h4 className="text-sm font-bold text-primary mb-2 flex items-center gap-2">
                        <span className="material-symbols-outlined text-sm">info</span>
                        提升建议
                      </h4>
                      <p className="text-sm text-on-surface-variant leading-relaxed">{selectedJob[2].innovation_ability.missing_reason}</p>
                    </div>
                  </div>
                </div>
              </section>

              {/* 三项软技能：学习能力、沟通表达、团队协作 各占4列 */}
              <section className="md:col-span-4 bg-surface-container-low !p-5 rounded-xl ring-1 ring-outline-variant/5 hover:ring-primary/20 transition-all">
                <div className="flex items-center gap-3 mb-4">
                  <span className="material-symbols-outlined text-primary">school</span>
                  <h3 className="font-bold text-on-surface">学习能力</h3>
                  <span className="ml-auto text-2xl font-black text-primary">{selectedJob[2].learning_ability.score}</span>
                </div>
                <div className="h-2 w-full bg-surface-container-highest rounded-full overflow-hidden relative mb-3">
                  <div className="h-full bg-primary rounded-full absolute left-0 top-0" style={{ width: `${selectedJob[2].learning_ability.score}%` }}></div>
                  <div className="h-full w-1 bg-on-surface-variant absolute top-0 z-10" style={{ left: `${selectedJob[2].learning_ability.benchmark_score}%` }}></div>
                </div>
                <p className="text-xs text-on-surface-variant leading-relaxed">{selectedJob[2].learning_ability.matched_reason}</p>
              </section>

              <section className="md:col-span-4 bg-surface-container-low !p-5 rounded-xl ring-1 ring-outline-variant/5 hover:ring-secondary/20 transition-all">
                <div className="flex items-center gap-3 mb-4">
                  <span className="material-symbols-outlined text-secondary">diversity_3</span>
                  <h3 className="font-bold text-on-surface">沟通表达</h3>
                  <span className="ml-auto text-2xl font-black text-secondary">{selectedJob[2].communication_ability.score}</span>
                </div>
                <div className="h-2 w-full bg-surface-container-highest rounded-full overflow-hidden relative mb-3">
                  <div className="h-full bg-secondary rounded-full absolute left-0 top-0" style={{ width: `${selectedJob[2].communication_ability.score}%` }}></div>
                  <div className="h-full w-1 bg-on-surface-variant absolute top-0 z-10" style={{ left: `${selectedJob[2].communication_ability.benchmark_score}%` }}></div>
                </div>
                <p className="text-xs text-on-surface-variant leading-relaxed">{selectedJob[2].communication_ability.matched_reason}</p>
              </section>

              <section className="md:col-span-4 bg-surface-container-low !p-5 rounded-xl ring-1 ring-outline-variant/5 hover:ring-tertiary/20 transition-all">
                <div className="flex items-center gap-3 mb-4">
                  <span className="material-symbols-outlined text-tertiary">groups</span>
                  <h3 className="font-bold text-on-surface">团队协作</h3>
                  <span className="ml-auto text-2xl font-black text-tertiary">{selectedJob[2].teamwork_ability.score}</span>
                </div>
                <div className="h-2 w-full bg-surface-container-highest rounded-full overflow-hidden relative mb-3">
                  <div className="h-full bg-tertiary rounded-full absolute left-0 top-0" style={{ width: `${selectedJob[2].teamwork_ability.score}%` }}></div>
                  <div className="h-full w-1 bg-on-surface-variant absolute top-0 z-10" style={{ left: `${selectedJob[2].teamwork_ability.benchmark_score}%` }}></div>
                </div>
                <p className="text-xs text-on-surface-variant leading-relaxed">{selectedJob[2].teamwork_ability.matched_reason}</p>
              </section>

              {/* 核心实习经历 全宽 */}
              <section className="md:col-span-12 bg-gradient-to-br from-primary/5 via-surface to-secondary/5 !p-6 rounded-2xl ring-1 ring-primary/20 relative overflow-hidden">
                <div className="absolute -right-20 -top-20 w-64 h-64 bg-primary/10 rounded-full blur-3xl"></div>
                <div className="absolute -left-20 -bottom-20 w-64 h-64 bg-secondary/10 rounded-full blur-3xl"></div>
                <div className="relative z-10">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-14 h-14 bg-primary rounded-xl flex items-center justify-center text-white shadow-lg shadow-primary/30">
                      <span className="material-symbols-outlined text-2xl">work</span>
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-on-surface">核心实习经历</h3>
                      <p className="text-sm text-on-surface-variant">Internship Experience</p>
                    </div>
                  </div>
                  <hr className="my-4 border-0 h-px bg-outline-variant/30" />
                  <div className="grid md:grid-cols-3 gap-6">
                    <div className="bg-white/80 !p-6 rounded-xl border border-surface-container-high">
                      <div className="text-sm font-bold text-on-surface-variant mb-4">得分差距分析</div>
                      <div className="flex items-end gap-2 mb-3">
                        <span className={`text-5xl font-black ${selectedJob[2].internship_experience.score < selectedJob[2].internship_experience.benchmark_score ? 'text-error' : 'text-secondary'}`}>
                          {selectedJob[2].internship_experience.score}
                        </span>
                        <span className="text-xl text-on-surface-variant pb-1">/ {selectedJob[2].internship_experience.benchmark_score}</span>
                      </div>
                      {selectedJob[2].internship_experience.score < selectedJob[2].internship_experience.benchmark_score ? (
                        <div className="flex items-center gap-2 text-error font-bold text-sm animate-pulse">
                          <span className="material-symbols-outlined text-sm">warning</span>
                          <span>低于目标 {selectedJob[2].internship_experience.benchmark_score - selectedJob[2].internship_experience.score} 分</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 text-secondary font-bold text-sm">
                          <span className="material-symbols-outlined text-sm">check_circle</span>
                          <span>已达到基准要求</span>
                        </div>
                      )}
                    </div>
                    <div className="bg-white/80 !p-6 rounded-xl border border-surface-container-high">
                      <h4 className="text-sm font-bold text-on-surface mb-3 flex items-center gap-2">
                        <span className="w-2 h-4 bg-primary rounded-full"></span>
                        现状分析
                      </h4>
                      <p className="text-sm text-on-surface-variant leading-relaxed">"{selectedJob[2].internship_experience.matched_reason}"</p>
                    </div>
                    <div className="bg-white/80 !p-6 rounded-xl border border-surface-container-high">
                      <h4 className={`text-sm font-bold mb-3 flex items-center gap-2 ${selectedJob[2].internship_experience.score < selectedJob[2].internship_experience.benchmark_score ? 'text-error' : 'text-primary'}`}>
                        <span className={`w-2 h-4 rounded-full ${selectedJob[2].internship_experience.score < selectedJob[2].internship_experience.benchmark_score ? 'bg-error' : 'bg-primary'}`}></span>
                        核心缺失
                      </h4>
                      <p className="text-sm text-on-surface-variant leading-relaxed">"{selectedJob[2].internship_experience.missing_reason}"</p>
                    </div>
                  </div>
                  <hr className="my-4 border-0 h-px bg-outline-variant/30" />
                  <div className="flex flex-wrap gap-4 mt-6">
                    <button onClick={handleGetReport} className="bg-gradient-to-r from-primary to-primary/80 text-white !px-8 !py-3 rounded-xl font-bold flex items-center gap-2 hover:shadow-lg hover:shadow-primary/30 transition-all">
                      <span className="material-symbols-outlined">rocket_launch</span>
                      获取专项提升报告
                    </button>
            
                  </div>
                </div>
              </section>

              {/* 推荐岗位 全宽 */}
              <RecommendedJobs jobType={selectedJob[0]} onSelectJob={(jobId) => navigate(`/dashboard?job=${jobId}`)} />
            </div>
          </div>
        </PageDashboard>
      </>
    );
  }

  // 岗位列表视图
  return (
    <PageDashboard
      title="岗位匹配"
      subtitle="根据您的技能矩阵和职业轨迹，为您精选的建筑与技术交叉领域机遇"
      showBreadcrumb
      breadcrumbItems={[
        { label: '首页', href: '/' },
        { label: '岗位匹配' },
      ]}
    >
      <div className="animate-in fade-in duration-500">
        <div className="mb-8">
          <div className="mb-10 bg-surface-container-low rounded-xl !p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="flex gap-8 items-center">
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-1">最高匹配度</span>
                <span className="text-3xl font-bold text-secondary">{highestScore}%</span>
              </div>
            </div>
            <div className="flex gap-3 w-full sm:w-auto">
              <div className="relative flex-1 sm:flex-initial">
                <input
                  className="bg-surface-container-highest border-none rounded-lg !py-2.5 !pl-10 pr-4 text-sm focus:ring-2 focus:ring-primary/40 transition-all w-full sm:w-72 outline-none"
                  placeholder="搜索职位名称、公司..."
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">search</span>
              </div>
              <button className="flex items-center gap-2 !px-5 !py-2.5 bg-surface-container-high rounded-lg text-sm font-semibold hover:bg-surface-container-highest transition-colors">
                <span className="material-symbols-outlined text-lg">filter_list</span>
                筛选
              </button>
            </div>
          </div>
        </div>

        {jobList.length === 0 ? (
          <div className="job-match-empty">
            <div className="job-match-empty-icon">
              <span className="material-symbols-outlined">work</span>
            </div>
            <h3 className="job-match-empty-title">暂无匹配的岗位</h3>
            <p className="job-match-empty-desc">请先在能力分析页面填写简历信息，系统将为您推荐合适的岗位</p>
            <button onClick={() => navigate('/capability-analysis')} className="job-match-empty-btn">
              前往能力分析
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>arrow_forward</span>
            </button>
          </div>
        ) : (
          <div className="bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm border border-outline-variant/10">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[600px]">
                <thead>
                  <tr className="bg-surface-container-low">
                    <th className="!px-6 !py-4 text-sm font-bold text-on-surface-variant">岗位类型</th>
                    <th
                      className="!px-6 !py-4 text-sm font-bold text-on-surface-variant cursor-pointer group hover:text-primary transition-colors"
                      onClick={() => handleSort('match_score')}
                    >
                      <div className="flex items-center gap-1">
                        匹配得分
                        <span className={`material-symbols-outlined text-xs transition-opacity ${sortConfig?.key === 'match_score' ? 'opacity-100 text-primary' : 'opacity-0 group-hover:opacity-50'}`}>
                          {sortConfig?.key === 'match_score' && sortConfig.direction === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      </div>
                    </th>
                    <th className="!px-6 !py-4 text-sm font-bold text-on-surface-variant text-center">操作</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-container-low">
                  {filteredAndSortedJobs.map((job) => (
                    <tr key={job[0]} className="hover:bg-surface transition-colors group">
                      <td className="!px-6 !py-5">
                        <span className="text-on-surface font-bold block">{job[0]}</span>
                        {job[1] >= 80 && (
                          <div className="flex gap-2 mt-1">
                            <span className="text-[10px] bg-primary-fixed text-on-primary-fixed-variant px-2 py-0.5 rounded-full font-bold">热门</span>
                          </div>
                        )}
                      </td>
                      <td className="!px-6 !py-5">
                        <div className="flex items-center gap-3">
                          <div className="w-20 h-1.5 bg-surface-container-high rounded-full overflow-hidden">
                            <div className="h-full bg-secondary rounded-full" style={{ width: `${job[1]}%` }}></div>
                          </div>
                          <span className="text-secondary font-bold text-sm">{job[1]}</span>
                        </div>
                      </td>
                      <td className="!px-6 !py-5 text-center">
                        <button
                          onClick={() => setSelectedJob(job)}
                          className="text-xs font-bold text-primary hover:bg-primary/10 !px-4 !py-2 rounded-lg transition-colors inline-flex items-center gap-1 border border-primary/10"
                        >
                          查看详情
                          <span className="material-symbols-outlined text-sm">chevron_right</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="!px-6 !py-5 bg-surface-container-low/50 flex flex-col sm:flex-row justify-between items-center gap-4">
              <span className="text-sm text-on-surface-variant font-medium">显示第 1-{filteredAndSortedJobs.length} 项，共 {filteredAndSortedJobs.length} 项结果</span>
              <div className="flex gap-2">
                <button className="!p-2 hover:bg-surface-container-high rounded-lg transition-colors">
                  <span className="material-symbols-outlined text-sm">chevron_left</span>
                </button>
                <button className="w-9 h-9 flex items-center justify-center bg-primary text-white rounded-lg text-sm font-bold shadow-md shadow-primary/20">1</button>
                <button className="!p-2 hover:bg-surface-container-high rounded-lg transition-colors">
                  <span className="material-symbols-outlined text-sm">chevron_right</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </PageDashboard>
  );
}