# 报告生成器
#
import os
import json

from processor.utils.FileProcessor import FileProcessor
from processor.utils.LLMInvoker import LLMInvoker


fp_jobs = FileProcessor("log/result.json")
dic_jobs = fp_jobs.read()

class Reporter:
    def __init__(self, resume_info):
        self.model = LLMInvoker()
        self.resume_info = resume_info

    def job_report(self, target):  # 职业规划
        """
        基于简历信息生成个人简历规划报告
        :param target: 目标职业类别名称（字符串）
        :return: 包含个性化职业规划建议的报告字典
        """
        candidate_name = self.resume_info["name"]

        # 构建个性化分析的提示词
        prompt = f'''
        你是一位资深的职业发展顾问。请基于我的简历信息和目标岗位，分析岗位的需求，为我定制一份个性化的职业规划评估报告。语气要专业、和蔼。

        # 核心原则（必须严格遵守）：
        1. **个性化定制**：所有建议必须严格按照规定的目标岗位的信息设立前提与目标，结合我的具体背景，避免泛泛而谈
        2. **实事求是**：客观评估我的优势和不足，不夸大也不贬低
        3. **可执行性**：提供的建议必须具体、可执行、有时间节点
        4. **鼓励性语言**：在指出不足的同时，给予我积极的改进方向

        # 输入数据：
        ## 目标岗位信息：
        {json.dumps(dic_jobs[target], ensure_ascii=False, indent=2)}

        ## 我的基本信息：
        {json.dumps(self.resume_info, ensure_ascii=False, indent=2)}

        # 任务要求：
        请生成一份完整的个性化职业规划报告，包含以下内容：

        ## 1. 我的概况
        - 当前职业背景总结
        - 核心优势识别
        - 待提升领域

        ## 2. 人岗匹配度分析
        - 技能匹配度评分（0-100分）
        - 经验匹配度评分（0-100分）
        - 教育背景适配度
        - 综合匹配度评分（加权平均）

        ## 3. 差距分析
        - 硬技能差距：技术能力、专业知识等方面的不足
        - 软技能差距：沟通能力、管理能力等方面的不足
        - 经验差距：项目经验、行业经验等方面的不足
        - 证书/资质差距：是否需要考取相关证书

        ## 4. 个性化发展路径
        - 第一阶段（1-2个月）：快速补齐核心短板
        - 第二阶段（3-4个月）：系统学习与实践
        - 第三阶段（5-6个月）：项目实战与经验积累
        - 第四阶段（7-12个月）：求职准备与面试冲刺

        ## 5. 资源推荐
        - 推荐学习的课程或书籍
        - 建议参与的项目类型
        - 值得关注的行业资讯
        - 可以加入的社群或组织

        ## 6. 风险评估与应对
        - 主要风险点
        - 应对策略
        - 备选方案

        ## 7. 成功概率评估
        - 基于当前条件的成功概率（0-100%）
        - 影响成功率的关键因素
        - 提升成功率的建议

        # 输出格式要求：
        仅返回一个标准的 JSON 对象，格式如下：
        {{
          "candidate_name": "{candidate_name}",
          "target_job": "{target}",
          "candidate_summary": {{
            "current_background": "当前职业背景总结（100-200字）",
            "core_strengths": ["优势1", "优势2", ...],
            "areas_for_improvement": ["待提升1", "待提升2", ...]
          }},
          "match_analysis": {{
            "skill_match_score": 技能匹配度（0-100）,
            "experience_match_score": 经验匹配度（0-100）,
            "education_fit": "教育背景适配度评价",
            "overall_match_score": 综合匹配度（0-100）,
            "match_level": "高/中/低"
          }},
          "gap_analysis": {{
            "hard_skills_gaps": [
              {{
                "skill": "技能名称",
                "importance": "高/中/低",
                "current_level": "当前水平",
                "target_level": "目标水平",
                "learning_resources": ["资源1", "资源2"]
              }}, ...
            ],
            "soft_skills_gaps": [
            {{
                "skill": "技能名称",
                "importance": "高/中/低",
                "current_level": "当前水平",
                "target_level": "目标水平",
                "learning_resources": ["资源1", "资源2"]
              }}, ...
            ],
            "experience_gaps": [
            {{
                "skill": "技能名称",
                "importance": "高/中/低",
                "current_level": "当前水平",
                "target_level": "目标水平",
                "learning_resources": ["资源1", "资源2"]
              }}, ...
            ],
            "certification_needs": ["证书1", "证书2", ...]
          }},
          "development_plan": {{
            "phase_1": {{
              "duration": "1-2个月",
              "goals": ["目标1", "目标2"],
              "actions": ["行动1", "行动2"],
              "milestones": ["里程碑1", "里程碑2"]
            }},
            "phase_2": {{...}},
            "phase_3": {{...}},
            "phase_4": {{...}}
          }},
          "resource_recommendations": {{
            "courses": ["课程1", "课程2"],
            "books": ["书籍1", "书籍2"],
            "projects": ["项目类型1", "项目类型2"],
            "communities": ["社群1", "社群2"]
          }},
          "risk_assessment": {{
            "major_risks": ["风险1", "风险2"],
            "mitigation_strategies": ["策略1", "策略2"],
            "backup_plans": ["备选方案1", "备选方案2"]
          }},
          "success_probability": {{
            "probability_percentage": 成功概率（0-100）,
            "key_factors": ["因素1", "因素2"],
            "improvement_suggestions": ["建议1", "建议2"]
          }},
          "final_recommendation": "最终建议总结（200-400字）"
        }}

        # 质量检查清单（生成前自检）：
        ✓ 所有评分都有明确的依据
        ✓ 建议与我的背景高度相关
        ✓ 发展路径具有时间线和可执行性
        ✓ 资源推荐具体且可获得
        ✓ JSON 格式正确，可被 json.loads() 直接解析
        ✓ 语言专业、鼓励性强、易于理解

        现在请开始分析，严格按照上述要求输出 JSON 结果：
        '''

        # 调用LLM进行个性化分析
        raw_response = self.model.call_ollama(prompt)

        if not raw_response:
            print(f"{candidate_name} 的职业规划报告生成失败")
            return None

        print(f"{candidate_name} 的 {target} 职业规划报告已完成")
        return raw_response

    def job_report_ex(self, target, match_info=None):  # 职业规划
        """
        基于简历信息和匹配信息生成个人简历规划报告
        :param target: 目标职业类别名称（字符串）
        :param match_info: 人岗匹配信息
        :return: 包含个性化职业规划建议的报告字典
        """
        candidate_name = self.resume_info["name"]

        # 构建个性化分析的提示词
        prompt = f'''
        你是一位资深的职业发展顾问。请基于我的目标岗位、简历信息、匹配信息，分析岗位的需求，为我定制一份个性化的职业规划评估报告。语气要专业、和蔼。

        # 核心原则（必须严格遵守）：
        1. **个性化定制**：所有建议必须严格按照规定的目标岗位的信息设立前提与目标，结合我的具体背景，避免泛泛而谈
        2. **实事求是**：客观评估我的优势和不足，不夸大也不贬低
        3. **可执行性**：提供的建议必须具体、详细、可执行、有时间节点
        4. **鼓励性语言**：在指出不足的同时，给予我积极的改进方向

        # 输入数据：
        ## 目标岗位名称：{target}
        
        ## 目标岗位信息：
        {json.dumps(dic_jobs[target], ensure_ascii=False, indent=2)}

        ## 我的简历信息：
        {json.dumps(self.resume_info, ensure_ascii=False, indent=2)}

        ## 人岗匹配信息：
        {json.dumps(match_info if match_info else {}, ensure_ascii=False, indent=2)}

        # 任务要求：
        请生成一份完整的个性化职业规划报告，包含以下内容：

        ## 1. 我的概况
        - 当前职业背景总结
        - 核心优势识别
        - 待提升领域

        ## 2. 人岗匹配度分析
        - 技能匹配度评分（0-100分）
        - 经验匹配度评分（0-100分）
        - 教育背景适配度
        - 综合匹配度评分（加权平均）

        ## 3. 差距分析
        - 硬技能差距：技术能力、专业知识等方面的不足
        - 软技能差距：沟通能力、管理能力等方面的不足
        - 经验差距：项目经验、行业经验等方面的不足
        - 证书/资质差距：是否需要考取相关证书

        ## 4. 职业目标设定与职业路径规划
        ### 4.1 职业目标设定
        - 短期职业目标（1-2年）：结合个人意愿和职业探索结果
        - 中期职业目标（3-5年）：结合行业发展趋势和个人擅长方向
        - 长期职业目标（5-10年）：结合社会需求和个人发展潜力

        ### 4.2 行业发展趋势分析
        - 本职业的社会需求现状与未来趋势
        - 行业技术发展动向
        - 市场需求变化预测
        - 薪资水平发展趋势

        ### 4.3 职业路径规划
        - 清晰的职业发展阶梯（如：初级UI设计师 → 资深UI设计师 → 设计组长 → 设计总监 → 创意总监）
        - 每个阶段的核心能力要求
        - 每个阶段的典型工作年限
        - 晋升关键节点和里程碑
        - 可能的职业分支和转型方向

        ## 5. 个性化发展路径
        - 第一阶段（1-2个月）：快速补齐核心短板
        - 第二阶段（3-4个月）：系统学习与实践
        - 第三阶段（5-6个月）：项目实战与经验积累
        - 第四阶段（7-12个月）：求职准备与面试冲刺

        ## 6. 行动计划与成果展示
        ### 6.1 短期行动计划（1-6个月）
        - 学习路径：具体课程、书籍、在线资源
        - 实践安排：项目类型、实习机会、竞赛参与
        - 技能认证：需要考取的证书或资质
        - 预期成果：可量化的学习目标

        ### 6.2 中期行动计划（6-12个月）
        - 深度学习：进阶课程和专业培训
        - 项目实战：独立项目或团队协作项目
        - 行业交流：参加行业会议、技术沙龙
        - 人脉建设：加入专业社群、建立导师关系
        - 预期成果：作品集、项目经验、行业认可

        ### 6.3 评估周期与指标
        - 评估周期：每月自我评估、每季度深度复盘
        - 量化指标：
          * 技能掌握度（0-100分）
          * 项目完成数量和质量
          * 证书获取情况
          * 面试邀约率
          * offer转化率
        - 动态调整机制：根据评估结果调整学习重点和时间分配
        - 风险预警：识别可能的障碍并制定应对策略

        ## 7. 资源推荐
        - 推荐学习的课程或书籍
        - 建议参与的项目类型
        - 值得关注的行业资讯
        - 可以加入的社群或组织

        ## 8. 风险评估与应对
        - 主要风险点
        - 应对策略
        - 备选方案

        ## 9. 成功概率评估
        - 基于当前条件的成功概率（0-100%）
        - 影响成功率的关键因素
        - 提升成功率的建议

        # 输出格式要求：
        仅返回一个标准的 JSON 对象，格式如下：
        {{
          "candidate_name": "{candidate_name}",
          "target_job": "{target}",
          "candidate_summary": {{
            "current_background": "当前职业背景总结（100-200字）",
            "core_strengths": ["优势1", "优势2", ...],
            "areas_for_improvement": ["待提升1", "待提升2", ...]
          }},
          "match_analysis": {{
            "skill_match_score": 技能匹配度（0-100）,
            "experience_match_score": 经验匹配度（0-100）,
            "education_fit": "教育背景适配度评价",
            "overall_match_score": 综合匹配度（0-100）,
            "match_level": "高/中/低"
          }},
          "gap_analysis": {{
            "hard_skills_gaps": [
              {{
                "skill": "技能名称",
                "importance": "高/中/低",
                "current_level": "当前水平",
                "target_level": "目标水平",
                "learning_resources": ["资源1", "资源2"]
              }}, ...
            ],
            "soft_skills_gaps": [
            {{
                "skill": "技能名称",
                "importance": "高/中/低",
                "current_level": "当前水平",
                "target_level": "目标水平",
                "learning_resources": ["资源1", "资源2"]
              }}, ...
            ],
            "experience_gaps": [
            {{
                "skill": "技能名称",
                "importance": "高/中/低",
                "current_level": "当前水平",
                "target_level": "目标水平",
                "learning_resources": ["资源1", "资源2"]
              }}, ...
            ],
            "certification_needs": ["证书1", "证书2", ...]
          }},
          "career_path_planning": {{
            "career_goals": {{
              "short_term": {{
                "duration": "1-6个月",
                "goal_description": "短期职业目标描述",
                "key_milestones": ["里程碑1", "里程碑2"],
                "success_criteria": ["成功标准1", "成功标准2"]
              }},
              "mid_term": {{
                "duration": "6-12个月",
                "goal_description": "中期职业目标描述",
                "key_milestones": ["里程碑1", "里程碑2"],
                "success_criteria": ["成功标准1", "成功标准2"]
              }},
              "long_term": {{
                "duration": "1年以上",
                "goal_description": "长期职业目标描述",
                "key_milestones": ["里程碑1", "里程碑2"],
                "success_criteria": ["成功标准1", "成功标准2"]
              }}
            }},
            "industry_trends": {{
              "social_demand": "社会需求现状与未来趋势分析（200-300字）",
              "technology_trends": "行业技术发展动向（150-250字）",
              "market_changes": "市场需求变化预测（150-250字）",
              "salary_trends": "薪资水平发展趋势（100-200字）"
            }},
            "development_path": {{
              "path_stages": [
                {{
                  "stage_name": "职位名称（如：初级UI设计师）",
                  "level": 1,
                  "typical_duration": "典型工作年限（如：1-2年）",
                  "core_requirements": ["核心能力要求1", "核心能力要求2"],
                  "key_responsibilities": ["主要职责1", "主要职责2"],
                  "promotion_criteria": "晋升到下一阶段的关键条件"
                }},
                {{
                  "stage_name": "职位名称（如：资深UI设计师）",
                  "level": 2,
                  "typical_duration": "典型工作年限",
                  "core_requirements": ["核心能力要求1", "核心能力要求2"],
                  "key_responsibilities": ["主要职责1", "主要职责2"],
                  "promotion_criteria": "晋升到下一阶段的关键条件"
                }},
                {{
                  "stage_name": "职位名称（如：设计组长）",
                  "level": 3,
                  "typical_duration": "典型工作年限",
                  "core_requirements": ["核心能力要求1", "核心能力要求2"],
                  "key_responsibilities": ["主要职责1", "主要职责2"],
                  "promotion_criteria": "晋升到下一阶段的关键条件"
                }}, ...
              ],
              "alternative_paths": [
                {{
                  "path_name": "备选职业路径名称",
                  "description": "路径描述和适用场景",
                  "transition_requirements": ["转型所需条件1", "转型所需条件2"]
                }}, ...
              ]
            }}
          }},
          "development_plan": {{
            "phase_1": {{
              "duration": "1-2个月",
              "goals": ["目标1", "目标2"],
              "actions": ["行动1", "行动2"],
              "milestones": ["里程碑1", "里程碑2"]
            }},
            "phase_2": {{...}},
            "phase_3": {{...}},
            "phase_4": {{...}}
          }},
          "action_plan": {{
            "short_term_plan": {{
              "duration": "1-6个月",
              "learning_path": {{
                "courses": ["课程1", "课程2"],
                "books": ["书籍1", "书籍2"],
                "online_resources": ["在线资源1", "在线资源2"],
                "expected_outcomes": ["预期学习成果1", "预期学习成果2"]
              }},
              "practice_arrangements": {{
                "projects": ["项目类型1", "项目类型2"],
                "internships": "实习机会建议",
                "competitions": ["可参与的竞赛1", "可参与的竞赛2"],
                "expected_outcomes": ["预期实践成果1", "预期实践成果2"]
              }},
              "certifications": ["需要考取的证书1", "需要考取的证书2"],
              "quantifiable_goals": [
                {{
                  "metric": "指标名称",
                  "target_value": "目标值",
                  "measurement_method": "测量方法"
                }}
              ]
            }},
            "mid_term_plan": {{
              "duration": "6-12个月",
              "advanced_learning": {{
                "advanced_courses": ["进阶课程1", "进阶课程2"],
                "professional_training": ["专业培训1", "专业培训2"],
                "expected_outcomes": ["预期学习成果1", "预期学习成果2"]
              }},
              "project_experience": {{
                "independent_projects": ["独立项目类型1", "独立项目类型2"],
                "team_projects": ["团队协作项目类型1", "团队协作项目类型2"],
                "portfolio_building": "作品集建设建议",
                "expected_outcomes": ["预期项目成果1", "预期项目成果2"]
              }},
              "industry_engagement": {{
                "conferences": ["行业会议1", "行业会议2"],
                "tech_meetups": ["技术沙龙1", "技术沙龙2"],
                "networking": "人脉建设策略",
                "mentorship": "导师关系建立建议"
              }},
              "quantifiable_goals": [
                {{
                  "metric": "指标名称",
                  "target_value": "目标值",
                  "measurement_method": "测量方法"
                }}, ...
              ]
            }},
            "evaluation_framework": {{
              "evaluation_cycles": {{
                "self_assessment": "每月自我评估",
                "deep_review": "每季度深度复盘",
                "annual_review": "年度全面评估"
              }},
              "quantitative_metrics": [
                {{
                  "metric_name": "技能掌握度",
                  "scale": "0-100分",
                  "assessment_method": "评估方法",
                  "target_progression": "预期进步曲线"
                }},
                {{
                  "metric_name": "项目完成数量",
                  "unit": "个",
                  "assessment_method": "评估方法",
                  "target_progression": "预期进度"
                }},
                {{
                  "metric_name": "证书获取情况",
                  "unit": "个",
                  "assessment_method": "评估方法",
                  "target_progression": "预期进度"
                }},
                {{
                  "metric_name": "面试邀约率",
                  "scale": "百分比",
                  "assessment_method": "评估方法",
                  "target_progression": "预期进步曲线"
                }},
                {{
                  "metric_name": "offer转化率",
                  "scale": "百分比",
                  "assessment_method": "评估方法",
                  "target_progression": "预期进步曲线"
                }}
              ],
              "dynamic_adjustment": {{
                "adjustment_triggers": ["触发调整的条件1", "触发调整的条件2"],
                "adjustment_process": "调整流程和决策机制",
                "feedback_loop": "反馈循环机制说明"
              }},
              "risk_warning": {{
                "potential_obstacles": ["可能的障碍1", "可能的障碍2"],
                "early_warning_signs": ["预警信号1", "预警信号2"],
                "contingency_plans": ["应急预案1", "应急预案2"]
              }}
            }}
          }},
          "resource_recommendations": {{
            "courses": ["课程1", "课程2"],
            "books": ["书籍1", "书籍2"],
            "projects": ["项目类型1", "项目类型2"],
            "communities": ["社群1", "社群2"]
          }},
          "risk_assessment": {{
            "major_risks": ["风险1", "风险2"],
            "mitigation_strategies": ["策略1", "策略2"],
            "backup_plans": ["备选方案1", "备选方案2"]
          }},
          "success_probability": {{
            "probability_percentage": 成功概率（0-100）,
            "key_factors": ["因素1", "因素2"],
            "improvement_suggestions": ["建议1", "建议2"]
          }},
          "final_recommendation": "最终建议总结（200-400字）"
        }}

        # 质量检查清单（生成前自检）：
        ✓ 所有评分都有明确的依据
        ✓ 建议与我的背景高度相关
        ✓ 职业路径清晰且具有可操作性
        ✓ 行动计划具有时间线和可执行性
        ✓ 评估指标具体且可量化
        ✓ 资源推荐具体且可获得
        ✓ JSON 格式正确，可被 json.loads() 直接解析
        ✓ 语言专业、鼓励性强、易于理解

        现在请开始分析，严格按照上述要求输出 JSON 结果：
        '''
        print("开始生成报告")
        # 调用LLM进行个性化分析
        raw_response = self.model.call_ollama(prompt)

        if not raw_response:
            print(f"{candidate_name} 的职业规划报告生成失败")
            return None

        print(f"{candidate_name} 的 {target} 职业规划报告已完成")
        print(raw_response)
        return raw_response

    # def batch_extract_info_report(self, source, target): # 有必要吗🤔
    #     """
    #     基于简历信息生成个性化换岗报告
    #
    #     :param source: 源职业类别名称（字符串）
    #     :param target: 目标职业类别名称（字符串）
    #     :param resume_info: 简历信息字典，包含个人技能、经验等
    #     :return: 包含个性化换岗建议的报告字典
    #     """
    #     candidate_name = self.resume_info["name"]
    #
    #     # 构建结果文件名
    #
    #     # safe_name = candidate_name.replace(" ", "_").replace("/", "_")
    #     # result_filename = f"results/report_{safe_name}_{source}_to_{target}.json"
    #     #
    #     # # 检查是否已存在报告
    #     # if os.path.exists(result_filename):
    #     #     print(f"{candidate_name} 的 {source} -> {target} 换岗报告已生成")
    #     #     fp_existing = FileProcessor(result_filename)
    #     #     return fp_existing.read()
    #
    #     # 构建个性化分析的提示词
    #     prompt = f'''
    #     你是一位资深的职业发展顾问。请基于我的简历信息和职业换岗分析，思考换岗的逻辑与需求，为我定制一份个性化的换岗评估报告。语气要专业、和蔼。
    #
    #     # 核心原则（必须严格遵守）：
    #     1. **个性化定制**：所有建议必须严格按照规定的原岗位和目标岗位的信息设立前提与目标，结合我的具体背景，避免泛泛而谈
    #     2. **实事求是**：客观评估我的优势和不足，不夸大也不贬低
    #     3. **可执行性**：提供的建议必须具体、可执行、有时间节点
    #     4. **鼓励性语言**：在指出不足的同时，给予积极的改进方向
    #
    #     # 输入数据：
    #     ## 原岗位信息：
    #     {json.dumps(dic_jobs[source], ensure_ascii=
    #     False, indent=2)}
    #
    #     ## 目标岗位信息：
    #     {json.dumps(dic_jobs[target], ensure_ascii=
    #     False, indent=2)}
    #
    #     ## 我的基本信息：
    #     {json.dumps(self.resume_info, ensure_ascii=
    #     False, indent=2)}
    #
    #     # 任务要求：
    #     请生成一份完整的个性化换岗报告，包含以下内容：
    #
    #     ## 1. 我的概况
    #     - 当前职业背景总结
    #     - 核心优势识别
    #     - 待提升领域
    #
    #     ## 2. 人岗匹配度分析
    #     - 技能匹配度评分（0-100分）
    #     - 经验匹配度评分（0-100分）
    #     - 教育背景适配度
    #     - 综合匹配度评分（加权平均）
    #
    #     ## 3. 差距分析
    #     - 硬技能差距：技术能力、专业知识等方面的不足
    #     - 软技能差距：沟通能力、管理能力等方面的不足
    #     - 经验差距：项目经验、行业经验等方面的不足
    #     - 证书/资质差距：是否需要考取相关证书
    #
    #     ## 4. 个性化发展路径
    #     - 第一阶段（1-2个月）：快速补齐核心短板
    #     - 第二阶段（3-4个月）：系统学习与实践
    #     - 第三阶段（5-6个月）：项目实战与经验积累
    #     - 第四阶段（7-12个月）：求职准备与面试冲刺
    #
    #     ## 5. 资源推荐
    #     - 推荐学习的课程或书籍
    #     - 建议参与的项目类型
    #     - 值得关注的行业资讯
    #     - 可以加入的社群或组织
    #
    #     ## 6. 风险评估与应对
    #     - 主要风险点
    #     - 应对策略
    #     - 备选方案
    #
    #     ## 7. 成功概率评估
    #     - 基于当前条件的成功概率（0-100%）
    #     - 影响成功率的关键因素
    #     - 提升成功率的建议
    #
    #     # 输出格式要求：
    #     仅返回一个标准的 JSON 对象，格式如下：
    #     {{
    #       "candidate_name": "{candidate_name}",
    #       "source_job": "{source}",
    #       "target_job": "{target}",
    #       "candidate_summary": {{
    #         "current_background": "当前职业背景总结（100-200字）",
    #         "core_strengths": ["优势1", "优势2", ...],
    #         "areas_for_improvement": ["待提升1", "待提升2", ...]
    #       }},
    #       "match_analysis": {{
    #         "skill_match_score": 技能匹配度（0-100）,
    #         "experience_match_score": 经验匹配度（0-100）,
    #         "education_fit": "教育背景适配度评价",
    #         "overall_match_score": 综合匹配度（0-100）,
    #         "match_level": "高/中/低"
    #       }},
    #       "gap_analysis": {{
    #         "hard_skills_gaps": [
    #           {{
    #             "skill": "技能名称",
    #             "importance": "高/中/低",
    #             "current_level": "当前水平",
    #             "target_level": "目标水平",
    #             "learning_resources": ["资源1", "资源2"]
    #           }}, ...
    #         ],
    #         "soft_skills_gaps": [
    #         {{
    #             "skill": "技能名称",
    #             "importance": "高/中/低",
    #             "current_level": "当前水平",
    #             "target_level": "目标水平",
    #             "learning_resources": ["资源1", "资源2"]
    #           }}, ...
    #         ],
    #         "experience_gaps": [
    #         {{
    #             "skill": "技能名称",
    #             "importance": "高/中/低",
    #             "current_level": "当前水平",
    #             "target_level": "目标水平",
    #             "learning_resources": ["资源1", "资源2"]
    #           }}, ...
    #         ],
    #         "certification_needs": ["证书1", "证书2", ...]
    #       }},
    #       "development_plan": {{
    #         "phase_1": {{
    #           "duration": "1-2个月",
    #           "goals": ["目标1", "目标2"],
    #           "actions": ["行动1", "行动2"],
    #           "milestones": ["里程碑1", "里程碑2"]
    #         }},
    #         "phase_2": {{...}},
    #         "phase_3": {{...}},
    #         "phase_4": {{...}}
    #       }},
    #       "resource_recommendations": {{
    #         "courses": ["课程1", "课程2"],
    #         "books": ["书籍1", "书籍2"],
    #         "projects": ["项目类型1", "项目类型2"],
    #         "communities": ["社群1", "社群2"]
    #       }},
    #       "risk_assessment": {{
    #         "major_risks": ["风险1", "风险2"],
    #         "mitigation_strategies": ["策略1", "策略2"],
    #         "backup_plans": ["备选方案1", "备选方案2"]
    #       }},
    #       "success_probability": {{
    #         "probability_percentage": 成功概率（0-100）,
    #         "key_factors": ["因素1", "因素2"],
    #         "improvement_suggestions": ["建议1", "建议2"]
    #       }},
    #       "final_recommendation": "最终建议总结（200-400字）"
    #     }}
    #
    #     # 质量检查清单（生成前自检）：
    #     ✓ 所有评分都有明确的依据
    #     ✓ 建议与我的背景高度相关
    #     ✓ 发展路径具有时间线和可执行性
    #     ✓ 资源推荐具体且可获得
    #     ✓ JSON 格式正确，可被 json.loads() 直接解析
    #     ✓ 语言专业、鼓励性强、易于理解
    #
    #     现在请开始分析，严格按照上述要求输出 JSON 结果：
    #     '''
    #
    #     # 调用LLM进行个性化分析
    #     raw_response = model.call_ollama(prompt)
    #
    #     if not raw_response:
    #         print(f"{candidate_name} 的换岗报告生成失败")
    #         return None
    #
    #     # # 保存个性化报告
    #     # fp_report.save(raw_response)
    #
    #     # 同时保存到总报告文件
    #     # if os.path.exists("results/report.json"):
    #     #     fp_total_report = FileProcessor("results/report.json")
    #     #     dic_report = fp_total_report.read()
    #     # else:
    #     #     dic_report = {}
    #     #
    #     # report_key = f"{candidate_name}_{source}_to_{target}"
    #     # dic_report[report_key] = raw_response
    #     #
    #     # fp_total = FileProcessor("results/report.json")
    #     # fp_total.save(dic_report)
    #
    #     print(f"{candidate_name} 的 {source} -> {target} 换岗报告已完成")
    #     return raw_response


