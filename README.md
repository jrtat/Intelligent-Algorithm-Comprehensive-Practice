# 项目使用手册
- （需要提前安装cuda环境）

## 配置环境

```cmd
git clone https://github.com/oQAQo233/Intelligent-Algorithm-Comprehensive-Practice.git
cd Intelligent-Algorithm-Comprehensive-Practice
python -m venv .venv
.venv\Scripts\activate

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
pip install -r requirements.txt
pip install -e .
```

### 此外还需要提前在根目录下创建.env文件，至少包含以下信息

- DATABASE_NAME
- GRAPH_URL
- GRAPH_USERNAME
- GRAPH_PASSWORD

- LOCAL_MODEL_NAME
- LOCAL_BASE_URL
- SILICONFLOW_API

## 前端
- （需要提前安装bun环境）

```cmd
cd frontend
bun install
bun run dev
```

## 后端

```
cd src/FASTAPI_FrameWork
python APIRun.py
```
# 开发文档

本文档旨在说明系统中几个核心业务模块的数据结构，以便于后续开发和维护。

待做：
1. 岗位画像展示
2. 整个客户端（在Wev端）
3. 对接用户各种需求的大语言模型
    - 匹配岗位
    - 构建职业生涯规划
    - 设定阶段目标
4. 算法微调
小小demo：https://github.com/WZC-66/agentdemo/tree/main/frontend-app
暂定的接口信息：

## 1. 岗位画像 (Career Explorer)

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

---

## 2. 简历结构化信息 (Capability Analysis)

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

---

## 3. 匹配职位信息 (Job Match)
得传个JobData[]数组回前端
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
