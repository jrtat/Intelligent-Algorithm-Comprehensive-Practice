### 4.3 数据格式

#### 岗位画像格式 (job_profiles.jsonl)
```json
{
  "profile_type": "JOB_POSTING",
  "title": "前端开发",
  "hard_skills": [
    {"skill_name": "HTML", "category": "编程语言/框架/工具/理论"},
    {"skill_name": "CSS", "category": "编程语言/框架/工具/理论"},
    {"skill_name": "JavaScript", "category": "编程语言/框架/工具/理论"},
    {"skill_name": "Vue.js", "category": "编程语言/框架/工具/理论"},
    {"skill_name": "React", "category": "编程语言/框架/工具/理论"}
  ],
  "certifications": [],
  "soft_skills": {
    "innovation": {"score": 3, "evidence": "对新技术有好奇心，并愿意持续学习和提高"},
    "learning": {"score": 3, "evidence": "具备良好的学习能力和解决问题的思维能力"},
    "stress_tolerance": {"score": 3, "evidence": "能够承受一定工作压力"},
    "communication": {"score": 3, "evidence": "具备良好的沟通能力和团队协作精神"}
  },
  "experience": {
    "internship_priority": false,
    "core_module_depth": "期望参与核心模块的程度描述"
  },
  "domain_preference": ["互联网", "IT服务", "专业技术服务", "云计算"]
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| profile_type | string | 画像类型，固定为"JOB_POSTING" |
| title | string | 岗位名称 |
| hard_skills | array | 硬技能列表，每项包含skill_name和category |
| certifications | array | 证书要求列表 |
| soft_skills | object | 软技能评分，包含innovation、learning、stress_tolerance、communication |
| soft_skills.*.score | number | 技能评分(1-5分) |
| soft_skills.*.evidence | string | 评分依据/证据 |
| experience | object | 经验要求 |
| experience.internship_priority | boolean | 是否优先实习经历 |
| experience.core_module_depth | string | 核心模块参与深度描述 |
| domain_preference | array | 适用行业/领域列表 |

##提取画像需求

提取逻辑与判定依据（基于 岗位详情，公司特质 ，所属所属行业）

--需要评分的能力promp需要设计好一点，不能让大部分不同的岗位都差不多分数

0.一级维度

-子维度

-子维度


1. 专业技能-from岗位详情，用数组枚举比如[Java, Spring Boot, Redis]

-核心技术栈

识别 JD 中高频出现的编程语言、框架、中间件（如 Java, Spring Boot, Redis）。



-工具使用能力

识别开发辅助工具的要求（如 Git, Docker, Linux 命令行, Jenkins）。



-基础理论深度

识别对底层原理的要求（如 计算机网络、操作系统原理、算法复杂度分析）。

2. 证书要求-from岗位详情，用数组量化

-语言等级要求

明确提及的 CET-4/6、雅思/托福等外语能力门槛。



-专业技术认证

提及的所属行业准入或加分证书（如 软考、AWS/华为云认证、CPA 等）。



-竞赛获奖偏好

JD 中是否明确提到“有 ACM、蓝桥杯、数学建模等奖项者优先”。

3. 创新能力-from岗位详情 and 公司特质.设置对该能力的需求评分（1-5）

-技术探索意愿

文本中是否包含“关注前沿技术”、“对新技术有浓厚兴趣”、“自主钻研”等描述。



-方案优化能力

识别“参与架构优化”、“解决复杂难题”、“提供创新性解决方案”等职责描述。

4. 学习能力-设置对该能力的需求评分（1-5）

-知识迁移要求

识别“能够快速上手新业务”、“具备良好的自学能力”等关键词。



-学术背景深度

结合公司特质（如研究院/实验室），判定对学术研究、文献阅读能力的潜在要求。

5. 抗压能力

-任务交付强度

识别“适应高强度工作”、“抗压能力强”、“能应对紧急交付任务”等描述。



-环境适应力

结合公司特质（如互联网大厂、初创公司），判定对节奏适应、心理韧性的要求。

6. 沟通能力

-团队协作密度

识别“跨部门沟通”、“团队协作”、“具备良好的团队意识”等描述。



-需求表达/文档

识别“需求对接”、“技术文档撰写”、“方案陈述报告”等具体职责。

7. 实习经验

-相关背景要求

识别 JD 中对“知名企业实习经历”、“相关项目实战经验”的显性要求。


-角色深度要求

判定岗位是否期待候选人曾深度参与过核心模块（如“有大型系统开发经验者优先”）。

8.领域倾向（从 所属行业 中提取）
（有些）


###留个种子：岗位要有核心技能和加分技能
