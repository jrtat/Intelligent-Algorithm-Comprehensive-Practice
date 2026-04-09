小小demo：https://github.com/WZC-66/agentdemo/tree/main/frontend-app

待做：
1. 岗位画像展示
2. 整个客户端（在Wev端）
3. 对接用户各种需求的大语言模型
    - 匹配岗位
    - 构建职业生涯规划
    - 设定阶段目标
4. 算法微调


简历接口：
interface ResumeData {
  name: string;
  age: string;
  education: string;
  major: string;
  skills: string[];
  certificates: string[];
  projectExperience: string[];
  internshipExperience: string[];
  practicalExperience: string[];
  hobbies: string;
  summary: string;
  other: string;
  targetRole: string;
  completeness: number;
  scores: {
    adaptability: number;
    technicalDepth: number;
    communication: number;
    stressTolerance: number;
    innovation: number;
  };
  scoreExplanations?: {
    completeness: string;
    technicalDepth: string;
    adaptability: string;
    communication: string;
    stressTolerance: string;
    innovation: string;
    competitiveness: string;
  };
}


传给前端的匹配topk接口：
{
  "code": 200, 
  "message": "success", 
  "data": [
    {
      /* --- 1. 基础数据字段（后端直接从数据库/网盘提供的数据集中映射） --- */
      "job_id": "db_id_9527", // 【后端注意】必须使用数据库原始主键 ID，用于后续关联路径图谱
      "job_name": "AI产品经理(校招)", 
      "location": "北京·海淀", 
      "salary_range": "25k-40k", 
      "salary_min": 25000, // 【后端注意】需解析 salary_range，提取最小值作为整型，供前端 Filter 逻辑调用
      "company_name": "某科技巨头", 
      "industry": "人工智能/互联网", 
      "company_size": "10000人以上", 
      "company_type": "民营企业", 
      "update_date": "2026-04-09", 
      "source_url": "https://...", 
      "job_details": "岗位职责：...", // 原文 JD，用于前端 Agent 深度分析时的上下文
      "company_details": "公司简介：...", 

      /* --- 2. 核心量化指标（后端通过 LLM 打分后在接口层计算平均值） --- */
      "match_score": 82.1, // 【后端逻辑】综合得分 = dimension_analysis 中 7 个维度 score 的算术平均分
      "benchmark_total_score": 88.0, // 【后端逻辑】岗位基准 = dimension_analysis 中 7 个维度 benchmark_score 的算术平均分

      /* --- 3. 七大能力维度深度解析（后端通过 LLM 对比学生 Resume 与岗位 JD 产出） --- */
      "dimension_analysis": {
        /* 【LLM 任务提示】后端在 Prompt 中需指定 7 个固定 key。
           每一个维度包含：
           - benchmark_score: LLM 根据 JD 设定该岗位的理想分数（作为基准）
           - score: LLM 根据 Resume 给出学生实际分
           - matched_reason: 匹配点（学生哪做得好）
           - missing_reason: 缺口点（学生哪还不够）*/
        
        "professional_skill": { // 1. 专业技能
          "score": 75,
          "benchmark_score": 95, 
          "matched_reason": "具备计算机专业背景，熟悉基础机器学习算法。",
          "missing_reason": "缺乏大型语言模型（LLM）的实际调优经验，对Transformer架构理解不够深入。"
        },
        "innovation_ability": { // 2. 创新能力
          "score": 90,
          "benchmark_score": 85,
          "matched_reason": "在校期间发表过一篇顶会论文，提出过创新的数据清洗算法。",
          "missing_reason": "无明显缺失，建议继续保持发散性思维。"
        },
        "learning_ability": { // 3. 学习能力
          "score": 95,
          "benchmark_score": 90,
          "matched_reason": "自主考取了多项AI证书，并快速掌握了最新的提示词工程技术。",
          "missing_reason": "无明显缺失。"
        },
        "stress_resistance": { // 4. 抗压能力
          "score": 80,
          "benchmark_score": 85,
          "matched_reason": "有在创业团队高强度工作的经历。",
          "missing_reason": "面对复杂业务波动时的情绪管理经验相对较少。"
        },
        "communication_ability": { // 5. 沟通能力
          "score": 85,
          "benchmark_score": 80,
          "matched_reason": "表达清晰，能够将复杂算法逻辑通俗易懂地讲解给非技术人员。",
          "missing_reason": "在跨团队冲突协调方面的经验尚浅。"
        },
        "internship_experience": { // 6. 实习能力
          "score": 70,
          "benchmark_score": 90,
          "matched_reason": "有一段中型科技公司的算法实习经历。",
          "missing_reason": "缺乏在一线大厂参与核心AI产品上线闭环的完整实习经历。"
        },
        "teamwork_ability": { // 7. 团队合作能力
          "score": 80,
          "benchmark_score": 85,
          "matched_reason": "熟练使用协作工具，在校赛团队中担任核心开发者。",
          "missing_reason": "对大型异地团队的协作流程（如Agile/Scrum）了解不够。"
        }
      }
    }
  ]
}
