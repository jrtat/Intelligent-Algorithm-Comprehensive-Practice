后端FASTAPI依赖
```cmd
pip install fastapi uvicorn python-multipart
```
### 专业技能
具体细节：技能名称 
抽象评级：基于关键词加权计算技能深度评分（0-5）

### 证书要求
证书名称

### 学历要求
最低学历
专业方向（可空）

### 工作/实习经验
最低年限
工作领域

### 沟通能力
具体描述
评分（按照能力的大小）

### 抗压能力
具体描述
评分（抗压系数，直观）

### 学习能力
方向
评分
### 创新能力
方向
评分
### 团队协作能力



## 界面
### 基于AI的大学生职业规划智能体
#### 主界面

现在有一个招聘信息的xlsx文件，里面有许多列，其中两列分别为“岗位名称”、“省”。现在想使用ts和react-simple-maps设计一个Web前端界面，用户可选择岗位（从已有岗位中选择，一次只能选择一个），选择岗位并确认后会读取xlsx文件将所有这个岗位的省在GeoJSON地图(本地文件“china.json”放在public的map文件夹中)上标记出来，以方便用户直观的看到岗位在全国的分布情况。若“省”这一列为空则跳过，若存在省相同的情况，则以不同颜色的标记来直观感受数量多少（从绿到红渐变）且让数量更多的标记比数量更少的标记稍大，对数量占比大于10%的标记，添加一个脉动外圈，吸引用户注意力。鼠标悬停时标记会轻微放大（onMouseEnter 增加半径），提升交互感。给出完整可运行的.css和.tsx代码

现在想使用ts设计一个 “基于AI的大学生职业规划智能体” Web前端，用户可在输入栏中输入想给智能体发的消息。用户还可拖拽或者读取本地文件上传pdf简历，上传后会从这个pdf简历中提取结构化数据显示在右边供用户查看、添加与修改，对于右边的简历结构化信息栏用户可选则收起或者展开。点击发送后会将用户的消息和简历结构化信息通过后端接口传给数据处理模型，所以这部分只需要设计接口就行，模型我自己接入。给出完整可运行的.css和.tsx代码。
注意环境为：
{
  "name": "front_proj",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@types/d3-geo": "^3.1.0",
    "d3-geo": "^3.1.1",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-simple-maps": "^3.0.0",
    "xlsx": "^0.18.5"
  },
  "devDependencies": {
    "@eslint/js": "^9.39.4",
    "@types/node": "^24.12.2",
    "@types/react": "^18.3.18",
    "@types/react-dom": "^18.3.5",
    "@types/react-simple-maps": "^3.0.6",
    "@vitejs/plugin-react": "^6.0.1",
    "eslint": "^9.39.4",
    "eslint-plugin-react-hooks": "^7.0.1",
    "eslint-plugin-react-refresh": "^0.5.2",
    "globals": "^17.4.0",
    "typescript": "~6.0.2",
    "typescript-eslint": "^8.58.0",
    "vite": "^8.0.4"
  }
}

# 前端整合
1. 界面外观
2. 路由结构
3. 前后端数据接口（FASTAPI）
前端发送数据，等待（使用等待界面）后端处理并传回数据
> 岗位画像数据api
岗位画像数据用于在“职业探索”页面展示不同岗位的详细信息、技能要求以及职业发展路径。

### `JobProfile` 数据结构

```typescript
interface JobProfile {
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
```
> 简历结构化信息api
简历结构化信息用于在“能力分析”页面存储从用户上传的简历（或手动输入的文本）中通过 LLM 解析提取出的结构化数据。

### `ResumeData` 数据结构

```typescript
interface ResumeData {
  name: string;                    // 姓名
  age: string;                     // 年龄
  education: string;               // 学历
  major: string;                   // 就读专业
  skills: string[];                // 掌握的专业技能列表
  certificates: string[];          // 证书列表
  projectExperience: string[];     // 项目经历列表
  internshipExperience: string[];  // 实习经历列表
  practicalExperience: string[];   // 实践活动经历列表
  hobbies: string;                 // 兴趣爱好
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
```
> 职位匹配信息api
得传个JobData[]，数组回前端
匹配职位信息用于在“岗位匹配”页面展示系统为用户推荐的岗位列表，以及针对某个岗位的深度匹配分析报告。

### `JobData` 数据结构

```typescript
interface JobData {
  job_id: string;                  // 数据库原始ID，用于详情跳转
  job_name: string;                // 岗位名称
  location: string;                // 工作地点
  salary_range: string;            // 薪资范围展示文本 (如: "25k-40k")
  salary_min: number;              // 最低薪资，用于前端滑动条筛选和排序
  company_name: string;            // 公司名称
  industry: string;                // 所属行业
  company_size: string;            // 公司规模 (如: "10000人以上")
  company_type: string;            // 公司性质 (如: "民营企业")
  update_date: string;             // 更新日期 (如: "2026-04-09")
  source_url: string;              // 来源链接 (点击岗位名称跳转的超链接)
  job_details: string;             // 岗位职责详细描述
  company_details: string;         // 公司简介详细描述
  match_score: number;             // 综合匹配得分 (1-100)
  benchmark_total_score: number;   // 综合基准得分 (1-100)
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
interface DimensionScore {
  score: number;                   // 个人在该维度的得分 (1-100)
  benchmark_score: number;         // 该岗位在该维度的基准要求得分 (1-100)
  matched_reason: string;          // 匹配理由 (现状分析)
  missing_reason: string;          // 缺失理由 (提升建议/核心缺失)
}
```

api接口prompt :
现在请帮我在frontend/src/api里面写一个基于ts和axios的user数据接口，这个接口会将ResumeData数据传给后端进行处理，后端会将处理后的JobData数据传回。前端提交 ResumeData，后端立即返回 `taskId`（202 Accepted）， 然后前端每 2-5 秒轮询 `/api/task/{taskId}` 获取处理进度。

ResumeData数据传输的HTTP方法为POST，URL为'POST /api/resume/process'，请求体为frontend/src/types/job.ts中的ResumeData接口，响应体为frontend/src/types/job.ts中的TaskAcceptedResponse和ErrorResponse，其中ErrorResponse为错误响应。

轮询使用GET，响应体为frontend/src/types/job.ts中的TaskStatusResponse

前端轮询策略
间隔：2~5 秒（可动态调整，例如初始 2 秒，随后递增到 5 秒）

停止条件：收到 status === "completed" 或 "failed"，或达到最大轮询次数（如 120 次，对应最长 10 分钟）

超时处理：超过 10 分钟未完成，前端主动停止轮询并提示超时

# 前端界面
主界面Prompt：
修改frontend/src/pages里面的Home.css和Home.tsx代码，
# AI 精准测评，让职业选择更简单
AI 驱动的一站式职业测评平台。通过智能能力评估、岗位全景解析与精准匹配，帮你清晰定位竞争力，找到最适合的发展方向，生成专属职业成长报告。
# 全景洞察岗位，看清细节与发展关系
  ## 岗位看板

  ## 岗位画像

  ## 岗位地图

# 科学测评实力，找到最适配你的岗位
  ## 能力测评、竞争力分析
  能力测评

  ## 意愿匹配
  岗位匹配

# 定制你的专属报告，解锁清晰职业路径
  ## 职业报告生成
  分析报告

  