import { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import jobsData from '../../data/jobs.json';
import citiesData from '../../data/cities.json';
import industriesData from '../../data/industries.json';
import { AbilityBar } from '../JobDetail/AbilityBar';
import type { Job, City, Industry, FilterState } from '../../types/job';
import './job-dashboard.css';

const PAGE_SIZE = 50;

const jobsList: Job[] = Object.values(jobsData);
const allCities = Object.keys(citiesData);
const allLevels = [...new Set(Object.values(citiesData as Record<string, City>).map((c: City) => c.城市水平))].sort();
const allDegrees = [...new Set(jobsList.map(j => j.学历要求))].sort();
const allIndustries = Object.keys(industriesData);

const getCityInfo = (address: string) => (citiesData as unknown as Record<string, City>)[address];
const getIndustryInfo = (industry: string) => (industriesData as unknown as Record<string, Industry>)[industry];

export function JobDashboard() {
  const [searchParams] = useSearchParams();
  const [filter, setFilter] = useState<FilterState>({
    keyword: '',
    城市: '',
    城市水平: '',
    行业: '',
    学历: '',
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const filteredJobs = useMemo(() => {
    return jobsList.filter((job) => {
      if (filter.keyword) {
        const kw = filter.keyword.toLowerCase();
        const matchKeyword =
          job.岗位名称.toLowerCase().includes(kw) ||
          job.公司名称.toLowerCase().includes(kw) ||
          job.职业技能.some(s => s.toLowerCase().includes(kw));
        if (!matchKeyword) return false;
      }
      if (filter.城市 && job.地址 !== filter.城市) return false;
      if (filter.城市水平) {
        const cityInfo = getCityInfo(job.地址);
        if (!cityInfo || cityInfo.城市水平 !== filter.城市水平) return false;
      }
      if (filter.学历 && job.学历要求 !== filter.学历) return false;
      if (filter.行业) {
        const industry = getIndustryInfo(filter.行业);
        if (!industry || !industry.companies.includes(job.公司名称)) return false;
      }
      return true;
    });
  }, [filter]);

  const totalPages = Math.ceil(filteredJobs.length / PAGE_SIZE);
  const paginatedJobs = filteredJobs.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);
  const selectedJob = useMemo(() => filteredJobs.find(j => j.岗位编码 === selectedJobId), [filteredJobs, selectedJobId]);

  // Handle job selection from URL params - only on initial mount
  useEffect(() => {
    const jobIdFromUrl = searchParams.get('job');
    if (jobIdFromUrl) {
      setSelectedJobId(jobIdFromUrl);
      setFilter({ keyword: '', 城市: '', 城市水平: '', 行业: '', 学历: '' });
      setCurrentPage(1);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // 只在挂载时执行一次

  // Auto-select first job when filter changes or when paginated jobs change
  useEffect(() => {
    if (searchParams.get('job')) return; // 如果有 URL job 参数，跳过自动选择

    if (paginatedJobs.length > 0) {
      const firstJobId = paginatedJobs[0].岗位编码;
      if (!selectedJobId || !paginatedJobs.some(j => j.岗位编码 === selectedJobId)) {
        setSelectedJobId(firstJobId);
      }
    } else {
      setSelectedJobId(null);
    }
  }, [paginatedJobs, selectedJobId, searchParams]);

  // Reset to first page and select first job when filter changes
  const handleFilterChange = useCallback((key: keyof FilterState, value: string) => {
    setFilter(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  }, []);

  const handleResetFilters = useCallback(() => {
    setFilter({ keyword: '', 城市: '', 城市水平: '', 行业: '', 学历: '' });
    setCurrentPage(1);
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
    // Select first job of the new page
    const startIdx = (page - 1) * PAGE_SIZE;
    if (filteredJobs[startIdx]) {
      setSelectedJobId(filteredJobs[startIdx].岗位编码);
    }
  }, [filteredJobs]);

  const handleSelectJob = useCallback((jobId: string) => {
    setSelectedJobId(jobId);
  }, []);

  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const pages: (number | '...')[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push('...');
      for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
        pages.push(i);
      }
      if (currentPage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }

    return (
      <div className="pagination">
        <button
          className="page-btn"
          disabled={currentPage === 1}
          onClick={() => handlePageChange(currentPage - 1)}
        >
          ‹
        </button>
        {pages.map((page, idx) =>
          page === '...' ? (
            <span key={`ellipsis-${idx}`} className="page-ellipsis">...</span>
          ) : (
            <button
              key={page}
              className={`page-btn ${currentPage === page ? 'active' : ''}`}
              onClick={() => handlePageChange(page as number)}
            >
              {page}
            </button>
          )
        )}
        <button
          className="page-btn"
          disabled={currentPage === totalPages}
          onClick={() => handlePageChange(currentPage + 1)}
        >
          ›
        </button>
      </div>
    );
  };

  return (
    <div className="job-dashboard">
      {/* Breadcrumb */}
      <div className="dashboard-breadcrumb">
        <Link to="/" className="breadcrumb-link">首页</Link>
        <span className="breadcrumb-sep">/</span>
        <span className="breadcrumb-current">岗位看板</span>
      </div>

      {/* Main Content */}
      <div className="dashboard-main">
        {/* Left Sidebar */}
        <div className="dashboard-left">
          {/* Filter Bar */}
          <div className="filter-card">
            <div className="filters">
              <input
                type="text"
                className="filter-input"
                placeholder="🔍 搜索岗位名称 / 公司名 / 技能..."
                value={filter.keyword}
                onChange={(e) => handleFilterChange('keyword', e.target.value)}
              />
              <select
                className="filter-select"
                value={filter.城市}
                onChange={(e) => handleFilterChange('城市', e.target.value)}
              >
                <option value="">全部城市</option>
                {allCities.map((city) => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
              <select
                className="filter-select"
                value={filter.城市水平}
                onChange={(e) => handleFilterChange('城市水平', e.target.value)}
              >
                <option value="">全部等级</option>
                {allLevels.map((level) => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
              <select
                className="filter-select"
                value={filter.学历}
                onChange={(e) => handleFilterChange('学历', e.target.value)}
              >
                <option value="">全部学历</option>
                {allDegrees.map((deg) => (
                  <option key={deg} value={deg}>{deg}</option>
                ))}
              </select>
              <select
                className="filter-select"
                value={filter.行业}
                onChange={(e) => handleFilterChange('行业', e.target.value)}
              >
                <option value="">全部行业</option>
                {allIndustries.map((ind) => (
                  <option key={ind} value={ind}>{ind}</option>
                ))}
              </select>
              <button className="reset-btn" onClick={handleResetFilters}>重置</button>
            </div>
          </div>

          {/* Job List */}
          <div className="job-list-card">
            <div className="job-list-header">
              <span className="job-count">共 {filteredJobs.length} 条岗位</span>
            </div>
            <div className="job-list">
              {paginatedJobs.length === 0 ? (
                <p className="empty">没有找到匹配的岗位 😢</p>
              ) : (
                paginatedJobs.map(job => (
                  <div
                    key={job.岗位编码}
                    className={`job-item ${selectedJobId === job.岗位编码 ? 'selected' : ''}`}
                    onClick={() => handleSelectJob(job.岗位编码)}
                  >
                    <div className="job-item-header">
                      <span className="job-item-title">{job.岗位名称}</span>
                      <span className="job-item-salary">{job.薪资范围}</span>
                    </div>
                    <div className="job-item-info">
                      <span className="company">{job.公司名称}</span>
                      <span className="location">{job.地址}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
            {renderPagination()}
          </div>
        </div>

        {/* Right Sidebar - Job Detail */}
        <div className="dashboard-right">
          {selectedJob ? (
            <div className="detail-card">
              <div className="job-detail-page">
                <div className="job-card">
                  <div className="job-header">
                    <h3 className="job-title">{selectedJob.岗位名称}</h3>
                    <span className="job-salary">{selectedJob.薪资范围}</span>
                  </div>
                  <div className="job-info">
                    <span className="company">{selectedJob.公司名称}</span>
                    <span className="location">{selectedJob.地址}</span>
                  </div>
                  <div className="job-tags">
                    {selectedJob.学历要求 !== '无任何要求' && (
                      <span className="tag tag-edu">{selectedJob.学历要求}</span>
                    )}
                  </div>

                  <div className="ability-section">
                    <h4>能力等级要求</h4>
                    <AbilityBar label="沟通能力" level={selectedJob.沟通能力} />
                    <AbilityBar label="学习能力" level={selectedJob.学习能力} />
                    <AbilityBar label="抗压能力" level={selectedJob.抗压能力} />
                    <AbilityBar label="创新能力" level={selectedJob.创新能力} />
                    <AbilityBar label="实习能力" level={selectedJob.实习能力} />
                  </div>

                  <div className="job-actions">
                    <Link to={`/profile-list/${encodeURIComponent(selectedJob.岗位名称)}`} className="action-btn">查看岗位画像</Link>
                    <Link to="/map" state={{ jobName: selectedJob.岗位名称 }} className="action-btn">查看地图分布</Link>
                  </div>
                </div>

                <div className="job-detail-full">
                  <h2>岗位详情</h2>
                  <p className="job-desc">{selectedJob.岗位详情}</p>

                  {selectedJob.职业技能.length > 0 && (
                    <div className="job-section">
                      <h3>职业技能</h3>
                      <div className="skill-list">
                        {selectedJob.职业技能.map((skill, i) => (
                          <span key={i} className="skill-tag">{skill}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedJob.证书要求.length > 0 && (
                    <div className="job-section">
                      <h3>证书要求</h3>
                      <div className="skill-list">
                        {selectedJob.证书要求.map((cert, i) => (
                          <span key={i} className="skill-tag">{cert}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedJob.职位晋升.length > 0 && (
                    <div className="job-section">
                      <h3>职位晋升</h3>
                      <div className="skill-list">
                        {selectedJob.职位晋升.map((path, i) => (
                          <span key={i} className="skill-tag">{path}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  <a
                    href={selectedJob.岗位来源地址}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="job-link"
                  >
                    查看原始链接 →
                  </a>
                </div>
              </div>
            </div>
          ) : (
            <div className="detail-empty">
              <p>选择一个岗位查看详情</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
