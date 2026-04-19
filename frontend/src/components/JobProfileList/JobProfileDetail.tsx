import { useState, useMemo, useRef, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import resultData from '../../data/log/result.json';
import './JobProfileDetail.css';

interface ProfileData {
  jobName: string;
  scores: {
    name: string;
    score: number;
    icon: string;
  }[];
  descriptions: {
    skill: string;
    comprehensive: string;
    work: string;
    major: string;
    experience: string;
    certificate: string;
    welfare: string;
    education: string;
    promotion: string;
  };
  transferPaths: TransferPath[];
}

interface TransferPath {
  source_job: string;
  target_job: string;
  description: string;
  similarity: number;
}

// 预加载所有标签数据
const allTagsData: Record<number, Record<string, string[]>> = {};
const allTransferData: Record<number, TransferPath[]> = {};

// 初始化标签数据
const initTagsData = async () => {
  const tagFiles = [
    { key: 'skillTags', file: '职业技能概述.json' },
    { key: 'comprehensiveTags', file: '综合素质概述.json' },
    { key: 'workTags', file: '工作内容概述.json' },
    { key: 'majorTags', file: '专业背景概述.json' },
    { key: 'experienceTags', file: '工作经验概述.json' },
    { key: 'certificateTags', file: '证书要求概述.json' },
    { key: 'welfareTags', file: '福利待遇概述.json' },
    { key: 'educationTags', file: '学历要求概述.json' },
    { key: 'promotionTags', file: '晋升路径概述.json' },
  ];

  for (let jobIndex = 0; jobIndex <= 50; jobIndex++) {
    allTagsData[jobIndex] = {};
    for (const { key, file } of tagFiles) {
      try {
        const module = await import(/* @vite-ignore */ `../../data/log/${jobIndex}_${file}`);
        const tagKey = `${file.replace('.json', '')}_tags`;
        if (module.default && module.default[tagKey]) {
          allTagsData[jobIndex][key] = module.default[tagKey];
        }
      } catch {
        // Ignore missing files
      }
    }
    // 加载换岗路径数据
    try {
      const transferModule = await import(/* @vite-ignore */ `../../data/log/${jobIndex}_换岗路径信息.json`);
      if (transferModule.default) {
        const paths: TransferPath[] = Object.values(transferModule.default);
        allTransferData[jobIndex] = paths.sort((a, b) => b.similarity - a.similarity);
      }
    } catch {
      allTransferData[jobIndex] = [];
    }
  }
};

// 立即初始化
initTagsData();

// 获取指定岗位的标签数据
const loadProfileTags = (jobIndex: number): Record<string, string[]> => {
  return allTagsData[jobIndex] || {};
};

// 获取指定岗位的换岗路径数据
const loadTransferPaths = (jobIndex: number): TransferPath[] => {
  return allTransferData[jobIndex] || [];
};

// 获取分数颜色
const getScoreColor = (score: number) => {
  if (score >= 75) return '#10b981';
  if (score >= 65) return '#3b82f6';
  if (score >= 55) return '#f59e0b';
  return '#ef4444';
};

const getLevelText = (score: number) => {
  if (score >= 80) return '优秀';
  if (score >= 70) return '良好';
  if (score >= 60) return '中等';
  return '一般';
};

const scoreIcons: Record<string, string> = {
  '创新能力评分_score': 'fas fa-lightbulb',
  '抗压能力评分_score': 'fas fa-shield-heart',
  '沟通能力评分_score': 'fas fa-comments',
  '学习能力评分_score': 'fas fa-brain',
  '实践能力评分_score': 'fas fa-hands',
  '团队合作能力评分_score': 'fas fa-people-arrows',
};

const scoreKeys = [
  '创新能力评分_score',
  '抗压能力评分_score',
  '沟通能力评分_score',
  '学习能力评分_score',
  '实践能力评分_score',
  '团队合作能力评分_score',
];

const categories = [
  { id: 'core', label: '核心能力评估', icon: 'fas fa-chart-simple' },
  { id: 'skills', label: '技能标签云', icon: 'fas fa-tags' },
  { id: 'welfare', label: '薪酬福利', icon: 'fas fa-gift' },
  { id: 'education', label: '学历要求&成长阶梯', icon: 'fas fa-graduation-cap' },
  { id: 'skillDetail', label: '职业技能 · 深度要求', icon: 'fas fa-laptop-code' },
  { id: 'work', label: '工作内容 · 核心挑战', icon: 'fas fa-tasks' },
  { id: 'comprehensive', label: '综合实力 · 软实力', icon: 'fas fa-users' },
  { id: 'major', label: '专业背景', icon: 'fas fa-diploma' },
  { id: 'experience', label: '经验要求', icon: 'fas fa-briefcase-clock' },
  { id: 'transfer', label: '换岗路径', icon: 'fas fa-route' },
];

export function JobProfileDetail() {
  const navigate = useNavigate();
  const params = useParams<{ jobName?: string }>();
  const contentRef = useRef<HTMLDivElement>(null);

  const initialJobName = params.jobName ? decodeURIComponent(params.jobName) : '';

  const [searchQuery, setSearchQuery] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('core');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // 获取所有岗位名称
  const jobNames = useMemo(() => Object.keys(resultData as Record<string, unknown>), []);

  // 初始化 selectedJobName，确保默认显示第一个岗位
  const [selectedJobName, setSelectedJobName] = useState(initialJobName || (jobNames.length > 0 ? jobNames[0] : ''));

  const dropdownRef = useRef<HTMLDivElement>(null);

  // 点击外部关闭下拉框
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 监听滚动以更新当前活跃的分类
  useEffect(() => {
    const handleScroll = () => {
      if (!contentRef.current) return;

      const scrollTop = contentRef.current.scrollTop;
      const cards = contentRef.current.querySelectorAll('.category-card');

      for (let i = cards.length - 1; i >= 0; i--) {
        const card = cards[i] as HTMLElement;
        if (card.offsetTop <= scrollTop + 100) {
          setActiveSection(card.id);
          break;
        }
      }
    };

    const content = contentRef.current;
    if (content) {
      content.addEventListener('scroll', handleScroll);
      return () => content.removeEventListener('scroll', handleScroll);
    }
  }, []);

  // 过滤岗位
  const filteredJobs = useMemo(() => {
    if (!searchQuery.trim()) return jobNames;
    const query = searchQuery.toLowerCase();
    return jobNames.filter(name => name.toLowerCase().includes(query));
  }, [searchQuery, jobNames]);

  // 获取岗位索引
  const jobIndex = useMemo(() => jobNames.indexOf(selectedJobName), [jobNames, selectedJobName]);

  // 解析数据
  const profileData = useMemo<ProfileData | null>(() => {
    if (!selectedJobName) return null;
    const data = resultData as Record<string, Record<string, unknown>>;
    const jobInfo = data[selectedJobName];
    if (!jobInfo) return null;

    const scores = scoreKeys
      .filter(key => key in jobInfo)
      .map(key => ({
        name: key.replace('评分_score', ''),
        score: jobInfo[key] as number,
        icon: scoreIcons[key] || 'fas fa-chart-simple',
      }));

    const descriptions = {
      skill: (jobInfo['职业技能概述_description'] as string) || '',
      comprehensive: (jobInfo['综合素质概述_description'] as string) || '',
      work: (jobInfo['工作内容概述_description'] as string) || '',
      major: (jobInfo['专业背景概述_description'] as string) || '',
      experience: (jobInfo['工作经验概述_description'] as string) || '',
      certificate: (jobInfo['证书要求概述_description'] as string) || '',
      welfare: (jobInfo['福利待遇概述_description'] as string) || '',
      education: (jobInfo['学历要求概述_description'] as string) || '',
      promotion: (jobInfo['晋升路径概述_description'] as string) || '',
    };

    const transferPaths = jobIndex !== -1 ? loadTransferPaths(jobIndex) : [];

    return { jobName: selectedJobName, scores, descriptions, transferPaths };
  }, [selectedJobName, jobIndex]);

  // 获取标签数据
  const tagsData = useMemo(() => {
    if (jobIndex === -1) return {};
    return loadProfileTags(jobIndex);
  }, [jobIndex]);

  // 选择岗位
  const handleSelectJob = (jobName: string) => {
    setSelectedJobName(jobName);
    setSearchQuery('');
    setIsDropdownOpen(false);
    navigate(`/profile-list/${encodeURIComponent(jobName)}`, { replace: true });
  };

  // 滚动到指定卡片
  const scrollToCard = (id: string) => {
    const element = document.getElementById(id);
    if (element && contentRef.current) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const renderAllCards = () => {
    if (!profileData) {
      return (
        <div className="empty-state">
          <i className="fas fa-search"></i>
          <p>请在上方搜索框选择岗位</p>
        </div>
      );
    }

    return (
      <>
        {/* 核心能力评估 */}
        <div id="core" className="category-card">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-chart-simple"></i>
              <h2>核心能力评估</h2>
            </div>
            <div className="card-body">
              {profileData.scores.map((item) => {
                const fillColor = getScoreColor(item.score);
                const level = getLevelText(item.score);
                const scorePercent = (item.score / 100) * 100;
                return (
                  <div key={item.name} className="score-item">
                    <div className="score-meta">
                      <div className="score-name">
                        <i className={item.icon}></i> {item.name}
                      </div>
                      <div>
                        <span className="score-value">{item.score}</span>
                        <span className="level-tag">{level}</span>
                      </div>
                    </div>
                    <div className="progress-bar-bg">
                      <div
                        className="progress-fill"
                        style={{ width: `${scorePercent}%`, background: fillColor }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* 技能标签云 */}
        <div id="skills" className="category-card">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-tags"></i>
              <h2>技能标签云</h2>
            </div>
            <div className="card-body">
              <div className="tags-cloud">
                {(tagsData.skillTags || []).map((tag, idx) => (
                  <span key={idx} className="tag">{tag}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 薪酬福利 */}
        <div id="welfare" className="category-card">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-gift"></i>
              <h2>薪酬福利</h2>
            </div>
            <div className="card-body">
              <div className="tags-cloud">
                {(tagsData.welfareTags || []).map((tag, idx) => (
                  <span key={idx} className="tag">{tag}</span>
                ))}
              </div>
              {profileData.descriptions.welfare && (
                <p className="desc-text">{profileData.descriptions.welfare}</p>
              )}
            </div>
          </div>
        </div>

        {/* 学历要求&成长阶梯 */}
        <div id="education" className="category-card">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-graduation-cap"></i>
              <h2>学历要求 & 成长阶梯</h2>
            </div>
            <div className="card-body">
              <div style={{ marginBottom: '16px' }}>
                <div className="sub-section-title">
                  <i className="fas fa-university"></i> 学历门槛
                </div>
                <div className="tags-cloud">
                  {(tagsData.educationTags || []).map((tag, idx) => (
                    <span key={idx} className="tag">{tag}</span>
                  ))}
                </div>
                {profileData.descriptions.education && (
                  <p className="info-text">{profileData.descriptions.education}</p>
                )}
              </div>
              <hr />
              <div style={{ marginTop: '16px' }}>
                <div className="sub-section-title">
                  <i className="fas fa-chart-line"></i> 晋升体系
                </div>
                <div className="tags-cloud">
                  {(tagsData.promotionTags || []).map((tag, idx) => (
                    <span key={idx} className="tag">{tag}</span>
                  ))}
                </div>
                {profileData.descriptions.promotion && (
                  <p className="info-text">{profileData.descriptions.promotion}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 职业技能 · 深度要求 */}
        <div id="skillDetail" className="category-card">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-laptop-code"></i>
              <h2>职业技能 · 深度要求</h2>
            </div>
            <div className="card-body">
              {profileData.descriptions.skill && (
                <p className="desc-text">{profileData.descriptions.skill}</p>
              )}
              <div className="tags-cloud">
                {(tagsData.skillTags || []).map((tag, idx) => (
                  <span key={idx} className="tag">{tag}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 工作内容 · 核心挑战 */}
        <div id="work" className="category-card">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-tasks"></i>
              <h2>工作内容 · 核心挑战</h2>
            </div>
            <div className="card-body">
              {profileData.descriptions.work && (
                <p className="desc-text">{profileData.descriptions.work}</p>
              )}
              <div className="tags-cloud">
                {(tagsData.workTags || []).map((tag, idx) => (
                  <span key={idx} className="tag">{tag}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 综合实力 · 软实力 */}
        <div id="comprehensive" className="category-card">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-users"></i>
              <h2>综合素质 · 软实力</h2>
            </div>
            <div className="card-body">
              {profileData.descriptions.comprehensive && (
                <p className="desc-text">{profileData.descriptions.comprehensive}</p>
              )}
              <div className="tags-cloud">
                {(tagsData.comprehensiveTags || []).map((tag, idx) => (
                  <span key={idx} className="tag">{tag}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 专业背景 */}
        <div id="major" className="category-card">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-diploma"></i>
              <h2>专业背景</h2>
            </div>
            <div className="card-body">
              {profileData.descriptions.major && (
                <p className="desc-text">{profileData.descriptions.major}</p>
              )}
              <div className="tags-cloud">
                {(tagsData.majorTags || []).map((tag, idx) => (
                  <span key={idx} className="tag">{tag}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 经验要求 */}
        <div id="experience" className="category-card">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-briefcase-clock"></i>
              <h2>经验要求</h2>
            </div>
            <div className="card-body">
              {profileData.descriptions.experience && (
                <p className="desc-text">{profileData.descriptions.experience}</p>
              )}
              <div className="tags-cloud">
                {(tagsData.experienceTags || []).map((tag, idx) => (
                  <span key={idx} className="tag">{tag}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 换岗路径 */}
        <div id="transfer" className="category-card">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-route"></i>
              <h2>换岗路径</h2>
              {profileData.transferPaths.length > 0 && (
                <span className="transfer-count">共 {profileData.transferPaths.length} 条可转路径</span>
              )}
            </div>
            <div className="card-body">
              {profileData.transferPaths.length === 0 ? (
                <p className="empty-hint">暂无推荐换岗路径</p>
              ) : (
                <div className="transfer-paths">
                  {profileData.transferPaths.map((path, idx) => (
                    <div key={idx} className="transfer-item">
                      <div className="transfer-arrow">
                        <span className="source-job">{path.source_job}</span>
                        <i className="fas fa-arrow-right"></i>
                        <span
                          className="target-job"
                          onClick={() => handleSelectJob(path.target_job)}
                          title={`跳转到 ${path.target_job}`}
                        >
                          {path.target_job}
                        </span>
                      </div>
                      <div className="similarity-row">
                        <span className="similarity-label">岗位相似度</span>
                        <div className="similarity-bar">
                          <div
                            className="similarity-fill"
                            style={{ width: `${path.similarity * 100}%` }}
                          ></div>
                        </div>
                        <span className="similarity-value">{(path.similarity * 100).toFixed(1)}%</span>
                      </div>
                      {path.description && (
                        <p className="transfer-desc">{path.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </>
    );
  };

  return (
    <div className="job-profile-view">
      {/* 面包屑导航 */}
      <div className="breadcrumb">
        <Link to="/" className="breadcrumb-item">
          <i className="fas fa-home"></i> 首页
        </Link>
        <i className="fas fa-chevron-right breadcrumb-separator"></i>
        <span className="breadcrumb-item current">岗位画像</span>
      </div>

      {/* 顶部导航 */}
      <header className="top-nav">
        <div className="nav-left">
          <i className="fas fa-briefcase"></i>
          <span className="job-title">岗位画像</span>
        </div>

        {/* 搜索框 */}
        <div className="nav-search" ref={dropdownRef}>
          <div className="search-box" onClick={() => setIsDropdownOpen(!isDropdownOpen)}>
            <i className="fas fa-search"></i>
            <input
              type="text"
              placeholder="搜索岗位名称..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setIsDropdownOpen(true);
              }}
              onFocus={() => setIsDropdownOpen(true)}
            />
            {searchQuery && (
              <button
                className="clear-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setSearchQuery('');
                }}
              >
                <i className="fas fa-times"></i>
              </button>
            )}
            <i className={`fas fa-chevron-${isDropdownOpen ? 'up' : 'down'} dropdown-arrow`}></i>
          </div>

          {isDropdownOpen && (
            <div className="search-dropdown">
              {filteredJobs.length === 0 ? (
                <div className="dropdown-empty">未找到匹配的岗位</div>
              ) : (
                filteredJobs.map((name) => (
                  <div
                    key={name}
                    className={`dropdown-item ${selectedJobName === name ? 'active' : ''}`}
                    onClick={() => handleSelectJob(name)}
                  >
                    {name}
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <div className="nav-actions">
          <Link to="/dashboard" className="back-btn">
            <i className="fas fa-arrow-left"></i> 返回看板
          </Link>
        </div>
      </header>

      <div className="main-container">
        {/* 左侧分类栏 */}
        <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
          <button
            className="collapse-btn"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          >
            <i className={`fas fa-chevron-${sidebarCollapsed ? 'right' : 'left'}`}></i>
          </button>
          {!sidebarCollapsed && (
            <>
              <div className="sidebar-header">
                <h3>岗位画像维度</h3>
              </div>
              <nav className="category-nav">
                {categories.map((cat) => (
                  <a
                    key={cat.id}
                    href={`#${cat.id}`}
                    className={`category-item ${activeSection === cat.id ? 'active' : ''}`}
                    onClick={(e) => {
                      e.preventDefault();
                      scrollToCard(cat.id);
                    }}
                  >
                    <i className={cat.icon}></i>
                    <span>{cat.label}</span>
                  </a>
                ))}
              </nav>
            </>
          )}
        </aside>

        {/* 右侧内容区 */}
        <main className="content-area" ref={contentRef}>
          {selectedJobName && (
            <div className="selected-job-banner">
              当前查看: <strong>{selectedJobName}</strong>
            </div>
          )}
          <div className="cards-container">
            {renderAllCards()}
          </div>
        </main>
      </div>
    </div>
  );
}
