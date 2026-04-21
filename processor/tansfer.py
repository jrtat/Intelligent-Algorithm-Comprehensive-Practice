# 换岗数据
from processor.utils.FileProcessor import FileProcessor
import json
from processor.utils.LLMInvoker import LLMInvoker
model = LLMInvoker()

fp_map = FileProcessor("maps/affinity_matrix.json")
dic_map = fp_map.read()

fp_num2jt = FileProcessor("maps/num2jt.json")
dic_num2jt = fp_num2jt.read()

class_names = dic_map["class_names"]
affinity_matrix = dic_map["affinity_matrix"]

dic_jt2num = {}
for i in range(len(class_names)):
    dic_jt2num[class_names[i]] = i

fp_report = FileProcessor("results/report.json")

fp_result = FileProcessor("results/transfer.json")

fp_jt_info = FileProcessor("log/result.json")
dic_jt_info = fp_jt_info.read()
#
# class Transfer:
#     def __init__(self, num): # 可以存储换岗信息配合简历数据得到换岗报告
#         self.similarity_lst = []
#     def transfer(self, source): # 获取不同方面的报告
#         pass
#
#     def get_similarity(self): # 获取总相似度
#         for key in dic_map.keys():
#             self.similarity_lst.append(1)

# ... existing code ...

def batch_extract_info(source, target):
    """
    批量提取两个职业类别之间的换岗信息

    :param source: 源职业类别名称（字符串）
    :param target: 目标职业类别名称（字符串）
    :return: 包含换岗分析结果的字典，包括相似度、技能迁移建议等
    """
    # 构建提示词
    prompt = f'''
    你是一个专业的职业规划分析师。请基于以下两个职业类别的信息，分析从【{source}】转向【{target}】的可行性与建议。

    # 核心原则（必须严格遵守）：
    1. **数据驱动**：所有分析必须基于提供的相似度数据和职业特征，严禁无中生有
    2. **客观评估**：准确反映转岗难度，不夸大也不低估
    3. **实用导向**：提供的建议必须具有可操作性
    4. **结构化输出**：严格按照JSON格式返回，确保可解析

    # 输入数据：
    - {source}职业信息：{dic_jt_info[source]}
    - {target}职业信息：{dic_jt_info[target]}

    # 任务要求：
    请分析并生成岗位转换规划，包括以下内容：

    ## 转岗难度评估
    ## 技能迁移分析
    ## 转岗建议
    ## 风险提示

    # 输出格式要求：
    仅返回一个标准的 JSON 对象，格式如下：
    {{
      "source_job": "{source}",
      "target_job": "{target}",
      "description": "岗位转换规划的详细说明（100-200字）",
    }}

    # 质量检查清单（生成前自检）：
    ✓ 所有字段都已填充，没有空值
    ✓ 难度等级与相似度数值匹配
    ✓ 建议具有针对性和可操作性
    ✓ JSON 格式正确，可被 json.loads() 直接解析
    ✓ 语言专业、简洁、准确

    现在请开始分析，严格按照上述要求输出 JSON 结果
    '''

    # 调用LLM进行分析

    raw_response = model.call_ollama(prompt)

    if not raw_response:
        print(f"职业类别 ({source} -> {target}) 换岗信息解析失败")
        return None

    print(f"{source} -> {target} 换岗信息已完成")
    return raw_response


def batch_extract_info_report(source, target, resume_info):
    """
    基于简历信息生成个性化换岗报告

    :param source: 源职业类别名称（字符串）
    :param target: 目标职业类别名称（字符串）
    :param resume_info: 简历信息字典，包含个人技能、经验等
    :return: 包含个性化换岗建议的报告字典
    """
    candidate_name = resume_info.get("name", "未知候选人")

    # 构建结果文件名
    import os
    safe_name = candidate_name.replace(" ", "_").replace("/", "_")
    result_filename = f"results/report_{safe_name}_{source}_to_{target}.json"

    # 检查是否已存在报告
    if os.path.exists(result_filename):
        print(f"{candidate_name} 的 {source} -> {target} 换岗报告已生成")
        fp_existing = FileProcessor(result_filename)
        return fp_existing.read()

    # 首先获取基础换岗信息
    base_transfer_info = batch_extract_info(source, target)

    if base_transfer_info is None:
        print(f"无法获取基础换岗信息，报告生成失败")
        return None

    # 构建个性化分析的提示词
    prompt = f'''
    你是一位资深的职业发展顾问。请基于候选人的简历信息和职业换岗分析，生成一份个性化的换岗评估报告。

    # 核心原则（必须严格遵守）：
    1. **个性化定制**：所有建议必须结合候选人的具体背景，避免泛泛而谈
    2. **实事求是**：客观评估候选人的优势和不足，不夸大也不贬低
    3. ** actionable**：提供的建议必须具体、可执行、有时间节点
    4. **鼓励性语言**：在指出不足的同时，给予积极的改进方向

    # 输入数据：

    ## 候选人基本信息：
    {json.dumps(resume_info, ensure_ascii=
    False, indent = 2)}

    ## 职业换岗基础分析：
    {json.dumps(base_transfer_info, ensure_ascii=False, indent=2)}

    # 任务要求：
    请生成一份完整的个性化换岗报告，包含以下内容：

    ## 1. 候选人概况
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
      "source_job": "{source}",
      "target_job": "{target}",
      "report_date": "生成日期（YYYY-MM-DD）",
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
          }}
        ],
        "soft_skills_gaps": [...],
        "experience_gaps": [...],
        "certification_needs": [...]
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
    ✓ 建议与候选人背景高度相关
    ✓ 发展路径具有时间线和可执行性
    ✓ 资源推荐具体且可获得
    ✓ JSON 格式正确，可被 json.loads() 直接解析
    ✓ 语言专业、鼓励性强、易于理解

    现在请开始分析，严格按照上述要求输出 JSON 结果：
    '''

    # 调用LLM进行个性化分析
    raw_response = model.call_ollama(prompt)

    if not raw_response:
        print(f"{candidate_name} 的换岗报告生成失败")
        return None

    # 保存个性化报告
    fp_report.save(raw_response)

    # 同时保存到总报告文件
    # if os.path.exists("results/report.json"):
    #     fp_total_report = FileProcessor("results/report.json")
    #     dic_report = fp_total_report.read()
    # else:
    #     dic_report = {}
    #
    # report_key = f"{candidate_name}_{source}_to_{target}"
    # dic_report[report_key] = raw_response
    #
    # fp_total = FileProcessor("results/report.json")
    # fp_total.save(dic_report)

    print(f"{candidate_name} 的 {source} -> {target} 换岗报告已完成")
    return raw_response

if __name__ == '__main__':

    # 阈值
    threshold = 0.25

    affinity_matrix_new = [[0 for i in range(len(class_names))] for j in range(len(class_names))]
    for i in range(len(class_names)):
        total = sum(affinity_matrix[i]) - affinity_matrix[i][i]
        for j in range(i):
            affinity_matrix_new[i][j] = affinity_matrix[i][j] / total
        for j in range(i+1, len(class_names)):
            affinity_matrix_new[i][j] = affinity_matrix[i][j] / total

    print(" affinity_matrix_new: ")
    print(affinity_matrix_new)

    for i in range(len(class_names)):
        # print(sum(affinity_matrix[i]))
        for j in range(i):
            if affinity_matrix_new[i][j] > threshold:
                print(class_names[i], class_names[j], affinity_matrix_new[i][j])
        #         batch_extract_info(class_names[i], class_names[j])
        # for j in range(i+1, len(class_names)):
        #     if affinity_matrix_new[i][j] > threshold:
        #         batch_extract_info(class_names[i], class_names[j])


    for i in range(len(class_names)):
        fp_jt = FileProcessor(f"log/{i}_换岗路径信息.json")
        dic_jt = {}

        for j in range(len(class_names)):
            s = affinity_matrix_new[dic_jt2num[dic_num2jt[str(i)]]][dic_jt2num[dic_num2jt[str(j)]]]
            if s > threshold:
                t = batch_extract_info(dic_num2jt[str(i)], dic_num2jt[str(j)])
                t["similarity"] = s
                dic_jt[dic_num2jt[str(j)]] = t

        fp_jt.save(dic_jt)
