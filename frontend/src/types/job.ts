// 单条岗位数据
export interface Job {
  岗位编码: string
  岗位名称: string
  公司名称: string
  地址: string
  薪资范围: string
  岗位详情: string
  岗位来源地址: string
  学历要求: string
  毕业院校要求: string
  创新能力: number
  抗压能力: number
  沟通能力: number
  学习能力: number
  实习能力: number
  职业技能: string[]
  证书要求: string[]
  职位晋升: string[]
  月薪范围: number[]
}

// 岗位集合（JSON 格式为对象，key 是岗位编码）
export type JobsMap = Record<string, Job>

// 城市数据
export interface City {
  地址: string
  jobs: string[]
  城市坐标: number[]
  城市水平: string
}
export type CitiesMap = Record<string, City>

// 城市索引签名辅助类型
export interface CitiesByAddress {
  [address: string]: City
}

// 行业数据
export interface Industry {
  所属行业: string
  companies: string[]
}
export type IndustriesMap = Record<string, Industry>

// 行业索引签名辅助类型
export interface IndustriesByName {
  [name: string]: Industry
}

// 筛选条件
export interface FilterState {
  keyword: string
  城市: string
  城市水平: string
  行业: string
  学历: string
}

export interface ResumeData {
  name: string;                    // 姓名
  age: string;                     // 年龄
  education: string;               // 学历
  major: string;                   // 就读专业
  skills: string[];                // 掌握的专业技能列表
  certificates: string[];          // 证书列表
  projectExperience: string[];     // 项目经历列表
  internshipExperience: string[];  // 实习经历列表
  practicalExperience: string[];   // 实践活动经历列表
  hobbies: string[];                // 兴趣爱好列表
  summary: string;                 // 个人总结
  other: string;                   // 其他提取出的杂项信息
  targetRole: string;              // 主攻路径/目标岗位 (根据简历推断)
  completeness: number;            // 简历完整度评分 (1-100)
  scores: {                        // 五维能力评分 (1-100)
    adaptability: number;          // 适应能力
    technicalDepth: number;        // 技术深度
    communication: number;         // 沟通表达能力
    stressTolerance: number;       // 抗压能力
    innovation: number;            // 创新能力
  };

  scoreExplanations?: {            // 各项评分的解释性说明
    completeness: string;          // 简历完整度说明
    technicalDepth: string;        // 技术深度说明
    adaptability: string;          // 适应能力说明
    communication: string;         // 沟通表达能力说明
    stressTolerance: string;       // 抗压能力说明
    innovation: string;            // 创新能力说明
    competitiveness: string;       // 就业竞争力综合评价说明
  };
}

export interface JobData {
  job_id: string;                  // 数据库原始ID，用于详情跳转
  job_name: string;                // 岗位名称
  location: string;                // 工作地点
  salary_range: string;            // 薪资范围展示文本 (如: "25k-40k")
  salary_min: number;              // 最低薪资，用于前端滑动条筛选和排序
  company_name: string;            // 公司名称
  industry: string;                // 所属行业
  company_size: string;            // 公司规模 (如: "10000人以上")
  company_type: string;            // 公司性质 (如: "民营企业")
  source_url: string;              // 来源链接 (点击岗位名称跳转的超链接)
  job_details: string;             // 岗位职责详细描述
  company_details: string;         // 公司简介详细描述
  
  match_score: number;             // 综合匹配得分 (1-100)
  benchmark_total_score: 60;   // 综合基准得分 (1-100)
  
  dimension_analysis: {            // 七大维度深度解析
    professional_skill: DimensionScore;    // 专业技能
    innovation_ability: DimensionScore;    // 创新能力
    learning_ability: DimensionScore;      // 学习能力
    stress_resistance: DimensionScore;     // 抗压能力
    communication_ability: DimensionScore; // 沟通表达
    internship_experience: DimensionScore; // 核心实习经历
    teamwork_ability: DimensionScore;      // 团队协作
  };
}

// 维度得分详情
export interface DimensionScore {
  score: number;                   // 个人在该维度的得分 (1-100)
  benchmark_score: number;         // 该岗位在该维度的基准要求得分 (1-100)
  matched_reason: string;          // 匹配理由 (现状分析)
  missing_reason: string;          // 缺失理由 (提升建议/核心缺失)
}

export interface JobProfile {
  id: string;                      // 岗位唯一标识 (如: 'frontend', 'java')
  title: string;                   // 岗位名称 (如: "前端开发")
  description: string;             // 岗位职责描述
  education: string;               // 学历要求 (如: "本科及以上")
  major: string;                   // 专业要求 (如: "计算机相关专业优先")
  hard_skills: string[];           // 硬技能/专业技能列表 (如: ["HTML/CSS", "JavaScript", "Vue/React"])
  certifications: string[];        // 证书要求列表
  soft_skills: {                   // 软技能/综合能力评分 (1-100)
    innovation: number;            // 创新能力
    learning: number;              // 学习能力
    stress_tolerance: number;      // 抗压能力
    communication: number;         // 沟通能力
    teamwork: number;              // 团队合作
    internship: number;            // 实习能力
  };
  vertical_paths: string[];        // 垂直晋升路径列表 (如: ["高级前端开发", "前端架构师"])
  horizontal_paths: string[];      // 横向换岗路径列表 (如: ["Java开发工程师", "产品专员"])
  x: number;                       // 节点在画布上的 X 坐标
  y: number;                       // 节点在画布上的 Y 坐标
}

export interface ErrorResponse {
  code: number;
  message: string;
}

export interface TaskAcceptedResponse {
  taskId: string;        // 任务唯一标识
  status: "pending";     // 或 "processing"
  estimatedTime?: number; // 可选，预估处理时间（秒）
}

export interface TaskStatusResponse {
  taskId: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress?: number;          // 0-100，可选
  result?: JobData;           // 当 status = "completed" 时返回
  error?: string;             // 当 status = "failed" 时返回错误信息
}