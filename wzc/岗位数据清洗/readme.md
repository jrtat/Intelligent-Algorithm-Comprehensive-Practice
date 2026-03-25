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
