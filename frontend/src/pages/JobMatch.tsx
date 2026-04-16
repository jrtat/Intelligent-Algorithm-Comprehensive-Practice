import React, { useState, useMemo, useEffect } from 'react';
import type { JobData } from '../types/job';
import { PageDashboard } from '../components/PageDashboard/PageDashboard';

const mockJobs: JobData[] = [
  {
    job_id: "db_id_9527",
    job_name: "AI产品经理(校招)",
    location: "北京·海淀",
    salary_range: "25k-40k",
    salary_min: 25000,
    company_name: "某科技巨头",
    industry: "人工智能/互联网",
    company_size: "10000人以上",
    company_type: "民营企业",
    update_date: "2026-04-09",
    source_url: "https://...",
    job_details: "岗位职责：1. 负责AI模型产品化... 要求：计算机背景，对LLM有深入理解...",
    company_details: "公司简介：全球领先的AI研发机构...",
    match_score: 82.1,
    benchmark_total_score: 88.0,
    dimension_analysis: {
      professional_skill: {
        score: 75,
        benchmark_score: 95,
        matched_reason: "具备计算机专业背景，熟悉基础机器学习算法。",
        missing_reason: "缺乏大型语言模型（LLM）的实际调优经验，对Transformer架构理解不够深入。"
      },
      innovation_ability: {
        score: 90,
        benchmark_score: 85,
        matched_reason: "在校期间发表过一篇顶会论文，提出过创新的数据清洗算法。",
        missing_reason: "无明显缺失，建议继续保持发散性思维。"
      },
      learning_ability: {
        score: 95,
        benchmark_score: 90,
        matched_reason: "自主考取了多项AI证书，并快速掌握了最新的提示词工程技术。",
        missing_reason: "无明显缺失。"
      },
      stress_resistance: {
        score: 80,
        benchmark_score: 85,
        matched_reason: "有在创业团队高强度工作的经历。",
        missing_reason: "面对复杂业务波动时的情绪管理经验相对较少。"
      },
      communication_ability: {
        score: 85,
        benchmark_score: 80,
        matched_reason: "表达清晰，能够将复杂算法逻辑通俗易懂地讲解给非技术人员。",
        missing_reason: "在跨团队冲突协调方面的经验尚浅。"
      },
      internship_experience: {
        score: 70,
        benchmark_score: 90,
        matched_reason: "有一段中型科技公司的算法实习经历。",
        missing_reason: "缺乏在一线大厂参与核心AI产品上线闭环的完整实习经历。"
      },
      teamwork_ability: {
        score: 80,
        benchmark_score: 85,
        matched_reason: "熟练使用协作工具，在校赛团队中担任核心开发者。",
        missing_reason: "对大型异地团队的协作流程（如Agile/Scrum）了解不够。"
      }
    }
  },
  {
    job_id: "db_id_9528",
    job_name: "助理建筑设计师",
    location: "上海·徐汇",
    salary_range: "18k-30k",
    salary_min: 18000,
    company_name: "顶级设计院",
    industry: "建筑/城市规划",
    company_size: "1000-5000人",
    company_type: "国企",
    update_date: "2026-04-08",
    source_url: "https://...",
    job_details: "岗位职责：...",
    company_details: "公司简介：...",
    match_score: 79.5,
    benchmark_total_score: 85.0,
    dimension_analysis: {
      professional_skill: { score: 80, benchmark_score: 85, matched_reason: "熟练掌握CAD/Rhino", missing_reason: "缺乏大型公建项目经验" },
      innovation_ability: { score: 85, benchmark_score: 80, matched_reason: "有多个先锋设计竞赛获奖", missing_reason: "落地性需加强" },
      learning_ability: { score: 90, benchmark_score: 85, matched_reason: "快速学习新技术", missing_reason: "无" },
      stress_resistance: { score: 75, benchmark_score: 85, matched_reason: "能适应一定加班", missing_reason: "抗压能力待验证" },
      communication_ability: { score: 80, benchmark_score: 80, matched_reason: "沟通顺畅", missing_reason: "汇报经验较少" },
      internship_experience: { score: 75, benchmark_score: 80, matched_reason: "有甲级院实习经历", missing_reason: "实习时间较短" },
      teamwork_ability: { score: 85, benchmark_score: 85, matched_reason: "团队协作良好", missing_reason: "无" }
    }
  },
  {
    job_id: "db_id_9529",
    job_name: "BIM研发工程师",
    location: "深圳·南山",
    salary_range: "30k-50k",
    salary_min: 30000,
    company_name: "智慧城市科技",
    industry: "科技/数字化",
    company_size: "500-1000人",
    company_type: "外企",
    update_date: "2026-04-07",
    source_url: "https://...",
    job_details: "岗位职责：...",
    company_details: "公司简介：...",
    match_score: 76.8,
    benchmark_total_score: 82.0,
    dimension_analysis: {
      professional_skill: { score: 70, benchmark_score: 90, matched_reason: "了解BIM基础", missing_reason: "缺乏二次开发经验" },
      innovation_ability: { score: 80, benchmark_score: 80, matched_reason: "思维活跃", missing_reason: "无" },
      learning_ability: { score: 85, benchmark_score: 85, matched_reason: "学习能力强", missing_reason: "无" },
      stress_resistance: { score: 75, benchmark_score: 80, matched_reason: "抗压一般", missing_reason: "无" },
      communication_ability: { score: 80, benchmark_score: 80, matched_reason: "沟通良好", missing_reason: "无" },
      internship_experience: { score: 70, benchmark_score: 80, matched_reason: "有相关实习", missing_reason: "非核心研发岗" },
      teamwork_ability: { score: 80, benchmark_score: 80, matched_reason: "团队协作良好", missing_reason: "无" }
    }
  }
];

export default function JobMatch() {
  const [selectedJob, setSelectedJob] = useState<JobData | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortConfig, setSortConfig] = useState<{ key: 'salary_min' | 'match_score', direction: 'asc' | 'desc' } | null>({ key: 'match_score', direction: 'desc' });
  const [jobList, setJobList] = useState<JobData[]>([]);

  // 从 localStorage 读取匹配结果
  useEffect(() => {
    if (jobList.length > 0) return;

    const savedResult = localStorage.getItem('matchResult');
    if (savedResult) {
      try {
        const parsed = JSON.parse(savedResult);
        // 支持单个对象或数组两种格式
        if (Array.isArray(parsed)) {
          setJobList(parsed);
        } else {
          setJobList([parsed]);
        }
      } catch (e) {
        console.error('解析匹配结果失败:', e);
      }
    }
  }, []);

  const filteredAndSortedJobs = useMemo(() => {
    // 如果有真实数据，使用它；否则使用 mockJobs
    let result: JobData[] = jobList.length > 0 ? jobList : [...mockJobs];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(job =>
        job.job_name.toLowerCase().includes(query) ||
        job.company_name.toLowerCase().includes(query) ||
        job.industry.toLowerCase().includes(query) ||
        job.location.toLowerCase().includes(query)
      );
    }

    if (sortConfig) {
      result.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }

    return result;
  }, [jobList, searchQuery, sortConfig]);

  const highestScore = filteredAndSortedJobs.length > 0 
    ? Math.max(...filteredAndSortedJobs.map(j => j.match_score))
    : 0;

  const handleSort = (key: 'salary_min' | 'match_score') => {
    let direction: 'asc' | 'desc' = 'desc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'desc') {
      direction = 'asc';
    }
    setSortConfig({ key, direction });
  };

  if (selectedJob) {
    // Deep Analysis View
    return (
      <PageDashboard
        title={`${selectedJob.job_name} - 深度解析`}
        subtitle="基于核心算法理解力、产品架构设计及跨团队协作维度的量化对比"
        showBreadcrumb
        breadcrumbItems={[
          { label: '首页', href: '/' },
          { label: '岗位匹配', href: '/job-match' },
          { label: '深度解析' },
        ]}
      >
      <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">

        {/* Analysis Header */}
        <header className="mb-8 flex flex-col md:flex-row md:items-end justify-end gap-6">
          <div className="bg-surface-container-low p-6 rounded-xl min-w-[280px] ring-1 ring-outline-variant/10">
            <div className="text-sm font-bold text-on-surface-variant uppercase tracking-widest mb-1">综合匹配度</div>
            <div className="text-5xl font-black text-secondary">{selectedJob.match_score}%</div>
            <div className="mt-2 flex items-center gap-2 text-sm text-secondary">
              <span className="material-symbols-outlined">trending_up</span>
              <span>高于 94% 的同岗位申请人</span>
            </div>
          </div>
        </header>

        {/* Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* 1. Professional Skill */}
          <section className="md:col-span-8 bg-surface-container-lowest p-8 rounded-xl ring-1 ring-outline-variant/15">
            <div className="flex justify-between items-start mb-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-primary/10 text-primary rounded-full flex items-center justify-center">
                  <span className="material-symbols-outlined">psychology</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-on-surface">专业技能</h3>
                  <p className="text-sm text-on-surface-variant">对核心技术栈与业务场景的掌握程度</p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-3xl font-black text-primary">{selectedJob.dimension_analysis.professional_skill.score}</span>
                <span className="text-sm text-on-surface-variant"> / 基准 {selectedJob.dimension_analysis.professional_skill.benchmark_score}</span>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between text-xs font-bold text-on-surface-variant">
                <span>个人表现</span>
                <span>{selectedJob.dimension_analysis.professional_skill.score}%</span>
              </div>
              <div className="h-2 w-full bg-surface-container-highest rounded-full overflow-hidden relative">
                <div className="h-full bg-primary rounded-full absolute left-0 top-0" style={{ width: `${selectedJob.dimension_analysis.professional_skill.score}%` }}></div>
                <div className="h-full w-1 bg-on-surface-variant absolute top-0 z-10" style={{ left: `${selectedJob.dimension_analysis.professional_skill.benchmark_score}%` }}></div>
              </div>
              <div className="text-[10px] text-on-surface-variant/60 text-right italic">竖线代表岗位建议基准线</div>
            </div>

            <div className="grid md:grid-cols-2 gap-8 mt-8">
              <div className="space-y-2">
                <h4 className="text-sm font-bold flex items-center gap-2 text-secondary">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  匹配理由
                </h4>
                <p className="text-sm text-on-surface-variant leading-relaxed">
                  {selectedJob.dimension_analysis.professional_skill.matched_reason}
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-bold flex items-center gap-2 text-primary">
                  <span className="material-symbols-outlined text-sm">info</span>
                  提升建议
                </h4>
                <p className="text-sm text-on-surface-variant leading-relaxed">
                  {selectedJob.dimension_analysis.professional_skill.missing_reason}
                </p>
              </div>
            </div>
          </section>

          {/* 2. Innovation Ability */}
          <section className="md:col-span-4 bg-surface-container-lowest p-8 rounded-xl ring-1 ring-outline-variant/15 flex flex-col gap-6">
            <div className="flex flex-col gap-4">
              <div className="w-10 h-10 bg-secondary/10 text-secondary rounded-lg flex items-center justify-center">
                <span className="material-symbols-outlined">lightbulb</span>
              </div>
              <div>
                <h3 className="text-lg font-bold text-on-surface">创新能力</h3>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-2xl font-black text-secondary">{selectedJob.dimension_analysis.innovation_ability.score}</span>
                  <span className="text-xs text-on-surface-variant">/ 基准 {selectedJob.dimension_analysis.innovation_ability.benchmark_score}</span>
                </div>
              </div>
            </div>
            <div className="flex-grow">
              <p className="text-xs font-bold text-secondary mb-2">匹配理由</p>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                {selectedJob.dimension_analysis.innovation_ability.matched_reason}
              </p>
            </div>
            <div className="pt-4 border-t border-surface-container-high">
              <p className="text-xs font-bold text-primary mb-2">提升建议</p>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                {selectedJob.dimension_analysis.innovation_ability.missing_reason}
              </p>
            </div>
          </section>

          {/* Small Dimension Cards */}
          <section className="md:col-span-4 bg-surface-container-low p-6 rounded-xl flex flex-col gap-4 ring-1 ring-outline-variant/5">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary">school</span>
              <h3 className="font-bold">学习能力</h3>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-2xl font-bold">{selectedJob.dimension_analysis.learning_ability.score}</div>
              <div className="h-1 flex-grow bg-surface-container-highest rounded-full relative">
                <div className="h-full bg-primary absolute left-0 top-0" style={{ width: `${selectedJob.dimension_analysis.learning_ability.score}%` }}></div>
                <div className="h-full w-1 bg-on-surface-variant absolute top-0 z-10" style={{ left: `${selectedJob.dimension_analysis.learning_ability.benchmark_score}%` }}></div>
              </div>
              <div className="text-sm text-on-surface-variant">基准 {selectedJob.dimension_analysis.learning_ability.benchmark_score}</div>
            </div>
            <div className="text-xs text-on-surface-variant leading-relaxed">
              <strong>理由：</strong> {selectedJob.dimension_analysis.learning_ability.matched_reason}<br/><br/>
              <strong>建议：</strong> {selectedJob.dimension_analysis.learning_ability.missing_reason}
            </div>
          </section>

          <section className="md:col-span-4 bg-surface-container-low p-6 rounded-xl flex flex-col gap-4 ring-1 ring-outline-variant/5">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary">diversity_3</span>
              <h3 className="font-bold">沟通表达</h3>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-2xl font-bold">{selectedJob.dimension_analysis.communication_ability.score}</div>
              <div className="h-1 flex-grow bg-surface-container-highest rounded-full relative">
                <div className="h-full bg-primary absolute left-0 top-0" style={{ width: `${selectedJob.dimension_analysis.communication_ability.score}%` }}></div>
                <div className="h-full w-1 bg-on-surface-variant absolute top-0 z-10" style={{ left: `${selectedJob.dimension_analysis.communication_ability.benchmark_score}%` }}></div>
              </div>
              <div className="text-sm text-on-surface-variant">基准 {selectedJob.dimension_analysis.communication_ability.benchmark_score}</div>
            </div>
            <div className="text-xs text-on-surface-variant leading-relaxed">
              <strong>理由：</strong> {selectedJob.dimension_analysis.communication_ability.matched_reason}<br/><br/>
              <strong>建议：</strong> {selectedJob.dimension_analysis.communication_ability.missing_reason}
            </div>
          </section>

          <section className="md:col-span-4 bg-surface-container-low p-6 rounded-xl flex flex-col gap-4 ring-1 ring-outline-variant/5">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary">groups</span>
              <h3 className="font-bold">团队协作</h3>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-2xl font-bold">{selectedJob.dimension_analysis.teamwork_ability.score}</div>
              <div className="h-1 flex-grow bg-surface-container-highest rounded-full relative">
                <div className="h-full bg-primary absolute left-0 top-0" style={{ width: `${selectedJob.dimension_analysis.teamwork_ability.score}%` }}></div>
                <div className="h-full w-1 bg-on-surface-variant absolute top-0 z-10" style={{ left: `${selectedJob.dimension_analysis.teamwork_ability.benchmark_score}%` }}></div>
              </div>
              <div className="text-sm text-on-surface-variant">基准 {selectedJob.dimension_analysis.teamwork_ability.benchmark_score}</div>
            </div>
            <div className="text-xs text-on-surface-variant leading-relaxed">
              <strong>理由：</strong> {selectedJob.dimension_analysis.teamwork_ability.matched_reason}<br/><br/>
              <strong>建议：</strong> {selectedJob.dimension_analysis.teamwork_ability.missing_reason}
            </div>
          </section>

          {/* Core Internship Experience Analysis */}
          <section className="md:col-span-12 bg-white p-8 rounded-2xl ring-1 ring-primary/20 relative overflow-hidden mt-4">
            <div className="absolute -right-20 -top-20 w-64 h-64 bg-primary/5 rounded-full blur-3xl"></div>
            <div className="relative z-10 flex flex-col md:flex-row gap-12">
              <div className="md:w-1/3">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center text-white">
                    <span className="material-symbols-outlined">work</span>
                  </div>
                  <h3 className="text-2xl font-bold">核心实习经历</h3>
                </div>
                <div className="bg-surface p-6 rounded-xl border border-surface-container-high">
                  <div className="text-sm font-bold text-on-surface-variant mb-4">得分差距分析</div>
                  <div className="flex items-end gap-1 mb-2">
                    <span className={`text-5xl font-black ${selectedJob.dimension_analysis.internship_experience.score < selectedJob.dimension_analysis.internship_experience.benchmark_score ? 'text-error' : 'text-secondary'}`}>
                      {selectedJob.dimension_analysis.internship_experience.score}
                    </span>
                    <span className="text-xl text-on-surface-variant pb-1">/ {selectedJob.dimension_analysis.internship_experience.benchmark_score}</span>
                  </div>
                  {selectedJob.dimension_analysis.internship_experience.score < selectedJob.dimension_analysis.internship_experience.benchmark_score && (
                    <div className="flex items-center gap-2 text-error font-bold text-sm">
                      <span className="material-symbols-outlined text-sm">warning</span>
                      <span>低于目标基准 {selectedJob.dimension_analysis.internship_experience.benchmark_score - selectedJob.dimension_analysis.internship_experience.score}分</span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="md:w-2/3 space-y-8">
                <div>
                  <h4 className="text-lg font-bold mb-3 flex items-center gap-2 text-on-surface">
                    <span className="w-1.5 h-6 bg-primary rounded-full"></span>
                    现状分析
                  </h4>
                  <div className="p-5 bg-surface-container-low rounded-xl text-on-surface-variant leading-relaxed italic border-l-4 border-primary">
                    “{selectedJob.dimension_analysis.internship_experience.matched_reason}”
                  </div>
                </div>
                <div>
                  <h4 className={`text-lg font-bold mb-3 flex items-center gap-2 ${selectedJob.dimension_analysis.internship_experience.score < selectedJob.dimension_analysis.internship_experience.benchmark_score ? 'text-error' : 'text-primary'}`}>
                    <span className={`w-1.5 h-6 rounded-full ${selectedJob.dimension_analysis.internship_experience.score < selectedJob.dimension_analysis.internship_experience.benchmark_score ? 'bg-error' : 'bg-primary'}`}></span>
                    核心缺失
                  </h4>
                  <div className={`p-5 rounded-xl text-on-surface-variant leading-relaxed ${selectedJob.dimension_analysis.internship_experience.score < selectedJob.dimension_analysis.internship_experience.benchmark_score ? 'bg-error-container/30' : 'bg-primary/5'}`}>
                    <p className={`font-bold mb-2 ${selectedJob.dimension_analysis.internship_experience.score < selectedJob.dimension_analysis.internship_experience.benchmark_score ? 'text-error' : 'text-primary'}`}>关键短板：</p>
                    “{selectedJob.dimension_analysis.internship_experience.missing_reason}”
                  </div>
                </div>
                <div className="flex flex-wrap gap-4">
                  <button className="bg-primary text-white px-8 py-3 rounded-lg font-bold flex items-center gap-2 hover:bg-primary-container transition-all">
                    <span className="material-symbols-outlined">rocket_launch</span>
                    获取专项提升计划
                  </button>
                  <button className="bg-surface-container-high text-on-surface-variant px-6 py-3 rounded-lg font-bold hover:bg-surface-container-highest transition-all">
                    查看对标案例
                  </button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
      </PageDashboard>
    );
  }

  // Job List View
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

      {/* Filter/Stats row */}
      <div className="mb-10 bg-surface-container-low rounded-xl p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex gap-8 items-center">
          <div className="flex flex-col">
            <span className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-1">最高匹配度</span>
            <span className="text-3xl font-bold text-secondary">
              {highestScore}%
            </span>
          </div>
        </div>
        <div className="flex gap-3 w-full sm:w-auto">
          <div className="relative flex-1 sm:flex-initial">
            <input 
              className="bg-surface-container-highest border-none rounded-lg py-2.5 pl-10 pr-4 text-sm focus:ring-2 focus:ring-primary/40 transition-all w-full sm:w-72 outline-none" 
              placeholder="搜索职位名称、公司..." 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">search</span>
          </div>
          <button className="flex items-center gap-2 px-5 py-2.5 bg-surface-container-high rounded-lg text-sm font-semibold hover:bg-surface-container-highest transition-colors">
            <span className="material-symbols-outlined text-lg">filter_list</span>
            筛选
          </button>
        </div>
      </div>

      {/* Job List Table */}
      <div className="bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm border border-outline-variant/10">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr className="bg-surface-container-low">
                <th className="px-6 py-4 text-sm font-bold text-on-surface-variant cursor-pointer group">
                  <div className="flex items-center gap-1">
                    岗位名称
                    <span className="material-symbols-outlined text-xs opacity-0 group-hover:opacity-100 transition-opacity">swap_vert</span>
                  </div>
                </th>
                <th className="px-6 py-4 text-sm font-bold text-on-surface-variant">公司名称</th>
                <th className="px-6 py-4 text-sm font-bold text-on-surface-variant">所属行业</th>
                <th className="px-6 py-4 text-sm font-bold text-on-surface-variant">工作地点</th>
                <th 
                  className="px-6 py-4 text-sm font-bold text-on-surface-variant cursor-pointer group text-right hover:text-primary transition-colors"
                  onClick={() => handleSort('salary_min')}
                >
                  <div className="flex items-center justify-end gap-1">
                    薪资水平
                    <span className={`material-symbols-outlined text-xs transition-opacity ${sortConfig?.key === 'salary_min' ? 'opacity-100 text-primary' : 'opacity-0 group-hover:opacity-50'}`}>
                      {sortConfig?.key === 'salary_min' && sortConfig.direction === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                    </span>
                  </div>
                </th>
                <th 
                  className="px-6 py-4 text-sm font-bold text-on-surface-variant cursor-pointer group hover:text-primary transition-colors"
                  onClick={() => handleSort('match_score')}
                >
                  <div className="flex items-center gap-1">
                    匹配得分
                    <span className={`material-symbols-outlined text-xs transition-opacity ${sortConfig?.key === 'match_score' ? 'opacity-100 text-primary' : 'opacity-0 group-hover:opacity-50'}`}>
                      {sortConfig?.key === 'match_score' && sortConfig.direction === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                    </span>
                  </div>
                </th>
                <th className="px-6 py-4 text-sm font-bold text-on-surface-variant text-center">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-container-low">
              {filteredAndSortedJobs.map((job, index) => (
                <tr key={job.job_id} className="hover:bg-surface transition-colors group">
                  <td className="px-6 py-5">
                    <a 
                      href={job.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary font-bold hover:underline decoration-2 underline-offset-4 text-left block"
                    >
                      {job.job_name}
                    </a>
                    {job.match_score >= 80 && (
                      <div className="flex gap-2 mt-1">
                        <span className="text-[10px] bg-primary-fixed text-on-primary-fixed-variant px-2 py-0.5 rounded-full font-bold">热门</span>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-5 text-on-surface font-medium">{job.company_name}</td>
                  <td className="px-6 py-5 text-on-surface-variant text-sm">{job.industry}</td>
                  <td className="px-6 py-5 text-on-surface-variant text-sm">{job.location}</td>
                  <td className="px-6 py-5 text-on-surface font-bold text-right">{job.salary_range}</td>
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-3">
                      <div className="w-20 h-1.5 bg-surface-container-high rounded-full overflow-hidden">
                        <div className="h-full bg-secondary rounded-full" style={{ width: `${job.match_score}%` }}></div>
                      </div>
                      <span className="text-secondary font-bold text-sm">{job.match_score}</span>
                    </div>
                  </td>
                  <td className="px-6 py-5 text-center">
                    <button 
                      onClick={() => setSelectedJob(job)}
                      className="text-xs font-bold text-primary hover:bg-primary/10 px-4 py-2 rounded-lg transition-colors inline-flex items-center gap-1 border border-primary/10"
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
        <div className="px-6 py-5 bg-surface-container-low/50 flex flex-col sm:flex-row justify-between items-center gap-4">
          <span className="text-sm text-on-surface-variant font-medium">显示第 1-{filteredAndSortedJobs.length} 项，共 {filteredAndSortedJobs.length} 项结果</span>
          <div className="flex gap-2">
            <button className="p-2 hover:bg-surface-container-high rounded-lg transition-colors">
              <span className="material-symbols-outlined text-sm">chevron_left</span>
            </button>
            <button className="w-9 h-9 flex items-center justify-center bg-primary text-white rounded-lg text-sm font-bold shadow-md shadow-primary/20">1</button>
            <button className="p-2 hover:bg-surface-container-high rounded-lg transition-colors">
              <span className="material-symbols-outlined text-sm">chevron_right</span>
            </button>
          </div>
        </div>
      </div>
      </div>
    </div>
    </PageDashboard>
  );
}

