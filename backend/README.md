# 后端功能实现

## 岗位关联图谱构建（偏后端，在processor实现）

### 构建过程已完成

### 垂直岗位图谱（数据清洗已完成）

### 换岗路径图谱（未完成）
- 获取岗位具体需求描述概述
> 由于岗位包含的岗位需求描述不一定是正面的需求，且不同岗位对不同需求的程度不同，因此需要实现对需求概述的提取，后面括号内容不需要（并对其打分（大模型干）便于不同岗位的相似度匹配）。

[//]: # (- 岗位聚集)
[//]: # (1. 根据岗位名称进行聚类（完成，岗位类别）)
[//]: # (2. 对综合素质、职业技能、证书、工作经验、工作内容、专业、行业进行频次分析)
[//]: # (3. 对上述属性进行同类聚集)

- 岗位关系构建

[//]: # (- 层次构建（模糊偏序算法）)
[//]: # (1. 根据岗位需求的多少确定层级)
[//]: # (2. 根据包含关系确定链路（垂直晋升）)
[//]: # (> 具体算法：)
[//]: # (> - 先根据相同需求分数占比确认是否有关系)
[//]: # (> - 再根据分数比较进行层次关系构建（横向或垂直）)

> 大模型两两匹配就行，并构建关系。
> 先得到每个岗位的简要概述，然后根据岗位需求描述进行匹配，得到岗位关系（晋升关系和横向换岗关系）（需要具体划分关系吗，应该只需要指定换岗需求和方案就行）。
> 大模型输出：（vertical：0为无关系，1为顺序晋升，2为逆序晋升；horizontal：0为无关系，1为横向换岗）（待定）
```json
{
  "vertical": 0,
  "horizontal": 0 
}
```

- 前端接口：
```typescript
interface JobProfile {
  vertical_paths: string[];        // 垂直晋升路径列表 (如: ["高级前端开发", "前端架构师"])
  horizontal_paths: string[];      // 横向换岗路径列表 (如: ["Java开发工程师", "产品专员"])
}
```
还有
> 岗位需求描述

## 学生就业能力画像构建（已在前端实现）

### 简历录入

### 就业能力构建

## 学生岗位信息匹配

### 选择适合的岗位类型

- embedding匹配：选择最适合的节点文字段，找到关联的岗位类型
- 匹配度分析：结合岗位（51个）的能力需求和学生的能力画像匹配，打分量化分析

### 推荐适合的岗位样例（来自赛题数据库）

- embedding匹配：选择前三生成专属报告，生成匹配得分进行排序

### 生成匹配报告

---

## 前端接口：

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