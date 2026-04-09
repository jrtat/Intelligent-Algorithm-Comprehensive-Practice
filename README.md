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
  "code": 200, // 状态码
  "message": "success", 
  "data": [
    {
      /* --- 1. 基础识别与筛选字段 --- */
      "job_id": "db_id_9527", // 数据库原始ID，用于详情跳转
      "job_name": "AI产品经理(校招)", // 岗位名称
      "location": "北京·海淀", // 地点
      "salary_range": "25k-40k", // 展示文本
      "salary_min": 25000, // 用于前端滑动条筛选最低薪资
      "company_name": "某科技巨头", // 公司名
      "industry": "人工智能/互联网", // 行业
      "company_size": "10000人以上", // 规模
      "company_type": "民营企业", // 性质
      "update_date": "2026-04-09", // 更新日期
      "source_url": "https://...", // 来源链接
      "job_details": "岗位职责：1. 负责AI模型产品化... 要求：计算机背景，对LLM有深入理解...", // JD全文
      "company_details": "公司简介：全球领先的AI研发机构...", 

      /* --- 2. 核心量化分 (已按7维度计算平均值) --- */
      "match_score": 82.1, // 学生综合得分 = 七个维度得分之和 / 7
      "benchmark_total_score": 88.0, // 岗位要求综合基准分 = 七个维度基准分之和 / 7

      /* --- 3. 七大能力维度深度解析 --- */
      "dimension_analysis": {
        "professional_skill": {
          "score": 75, // 学生得分
          "benchmark_score": 95, // 岗位基准：此岗对专业要求极高
          "matched_reason": "具备计算机专业背景，熟悉基础机器学习算法。",
          "missing_reason": "缺乏大型语言模型（LLM）的实际调优经验，对Transformer架构理解不够深入。"
        },
        "innovation_ability": {
          "score": 90,
          "benchmark_score": 85, // 岗位基准：产品岗需要高创新
          "matched_reason": "在校期间发表过一篇顶会论文，提出过创新的数据清洗算法。",
          "missing_reason": "无明显缺失，建议继续保持发散性思维。"
        },
        "learning_ability": {
          "score": 95,
          "benchmark_score": 90,
          "matched_reason": "自主考取了多项AI证书，并快速掌握了最新的提示词工程技术。",
          "missing_reason": "无明显缺失。"
        },
        "stress_resistance": {
          "score": 80,
          "benchmark_score": 85,
          "matched_reason": "有在创业团队高强度工作的经历。",
          "missing_reason": "面对复杂业务波动时的情绪管理经验相对较少。"
        },
        "communication_ability": {
          "score": 85,
          "benchmark_score": 80,
          "matched_reason": "表达清晰，能够将复杂算法逻辑通俗易懂地讲解给非技术人员。",
          "missing_reason": "在跨团队冲突协调方面的经验尚浅。"
        },
        "internship_experience": {
          "score": 70,
          "benchmark_score": 90,
          "matched_reason": "有一段中型科技公司的算法实习经历。",
          "missing_reason": "缺乏在一线大厂参与核心AI产品上线闭环的完整实习经历。"
        },
        "teamwork_ability": {
          "score": 80,
          "benchmark_score": 85,
          "matched_reason": "熟练使用协作工具，在校赛团队中担任核心开发者。",
          "missing_reason": "对大型异地团队的协作流程（如Agile/Scrum）了解不够。"
        }
      }
    }
  ]
}
