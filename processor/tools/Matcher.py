# 岗位匹配器
import json

from KnowledgeGraph.func.build_vec import get_vector
from KnowledgeGraph.func.utils.get_models import get_local_embedding
from processor.utils.FileProcessor import FileProcessor
from processor.utils.LLMInvoker import LLMInvoker

# education --> 学历要求概述
# major --> 专业背景概述
# skills --> 职业技能概述 证书要求概述
# certificates --> 证书要求概述
# projectExperience --> 实践能力评分
# internshipExperience --> 工作经验概述
# practicalExperience -->
# hobbies --> 福利待遇概述
# summary -->

model = LLMInvoker()

fp_map = FileProcessor("maps/num2jt.json")
dic_map = fp_map.read()

match_map = { # 岗位的什么信息要看简历的什么
    "综合素质": ["summary", "scoreExplanations"],
    "职业技能": ["skills"],
    "证书": ["certificates"],
    "工作内容": ["targetRole"],
    "工作经验": ["projectExperience", "internshipExperience", "practicalExperience"],
    "福利待遇": ["hobbies"]
}

class Matcher:
    def __init__(self, resume_info):
        self.scores = []
        self.resume_info = resume_info
        self.jobs = [] # 得分和对应岗位名称
        self.rate = {
            "professional_skill": 0.3,
            "innovation_ability": 0.1,
            "learning_ability": 0.15,
            "stress_resistance": 0.1,
            "communication_ability": 0.1,
            "internship_experience": 0.15,
            "teamwork_ability": 0.1
        }

    def match(self, resume_keys, job_num, job_keys, prompt):
        """
        通用简历-岗位匹配函数，对比简历信息与岗位要求，返回匹配度和分析

        :param rate: 权重系数（0-1之间），表示该维度在整体匹配中的重要程度
        :param resume_keys: 简历信息字段名
        :param job_num: 岗位的对应编号
        :param job_keys: 岗位要求字段名
        :param prompt: 匹配评价标准和任务要求，需包含：
                       - 该维度的定义和内涵
                       - 评分标准（0-100分的具体划分）
                       - 关键词参考（可选）
                       - 其他特殊要求
        :return: 匹配结果字典，符合 DimensionScore 接口规范
        """
        # Step 1: 提取简历和岗位的相关信息
        resume_data = self._extract_resume_fields(resume_keys)
        job_data = self._extract_job_fields(job_num, job_keys)

        if not resume_data or not job_data:
            return {
                "score": 0,
                "benchmark_score": 60,
                "matched_reason": "简历或岗位信息缺失，无法进行匹配评估",
                "missing_reason": "请补充完整的简历信息或岗位要求"
            }

        # Step 2: 构建匹配评估 prompt
        p = f'''
        你是一个专业的简历-岗位匹配评估专家。请根据我提供的简历信息和岗位要求，按照给定的评价标准进行量化匹配评分，最终仅返回一个标准的 JSON 对象。

        # 核心原则（必须严格遵守）：
        1. **客观公正**：基于事实进行评判，避免主观臆断
        2. **证据导向**：每个评分结论都必须有明确的原文依据
        3. **全面考量**：综合考虑要求的强制性和我的满足程度
        4. **建设性反馈**：提供具体、可操作的提升建议

        # 输入数据：

        ## 简历信息：
        {resume_data}

        ## 岗位要求：
        {job_data}

        # 评价标准和要求：
        {prompt}

        # 评估流程：

        ## 第一步：确定岗位基准要求得分 (benchmark_score)
        岗位基准要求得分统一为60分

        ## 第二步：评估个人在该维度的得分 (score)
        基于简历信息，评估我实际满足程度，给出 1-100 的得分：
        - **90-100分**：完全满足或超出岗位要求，具备显著优势
        - **75-89分**：较好满足岗位要求，仅有少量差距
        - **60-74分**：基本满足岗位要求，但存在一定不足
        - **40-59分**：部分满足要求，差距较明显
        - **1-39分**：几乎不满足要求，差距很大

        ## 第三步：生成匹配理由 (matched_reason)
        提供清晰的现状分析（100-200字）：
        - 总结我在该维度的优势和劣势
        - 引用简历中的具体证据说明匹配情况
        - 对比岗位要求，说明满足程度
        - 语言专业、客观、具体

        ## 第四步：生成缺失理由/提升建议 (missing_reason)
        提供具体的提升建议或指出核心缺失（100-200字）：
        - 明确指出与岗位要求的差距
        - 给出2-4条具体、可操作的改进建议
        - 如果是完全匹配的维度，可以写"无明显缺失，建议继续保持"
        - 建议要具有针对性和可执行性

        # 输出格式要求：
        仅返回一个标准的 JSON 对象，严格符合以下结构：
        {{
          "score": 个人在该维度的得分（1-100的整数）,
          "benchmark_score": 该岗位在该维度的基准要求得分（1-100的整数）,
          "matched_reason": "匹配理由/现状分析文本（100-200字）",
          "missing_reason": "缺失理由/提升建议文本（100-200字）"
        }}

        # 质量检查清单（生成前自检）：
        ✓ score 和 benchmark_score 都是 1-100 之间的整数
        ✓ matched_reason 中有具体的原文引用作为证据
        ✓ missing_reason 提供了具体可操作的建议或明确指出无明显缺失
        ✓ 两个 reason 字段的内容不重复，各有侧重
        ✓ JSON 格式正确，可被 json.loads() 直接解析
        ✓ 不包含任何额外的字段或解释文本

        现在请开始评估，严格按照上述要求输出 JSON 结果：
        '''

        # Step 3: 调用 LLM 进行评估
        try:
            raw_response = model.call_ollama(p)

            if not raw_response:
                return {
                    "score": 0,
                    "benchmark_score": 60,
                    "matched_reason": "模型调用失败，未获取到评估结果",
                    "missing_reason": "请稍后重试"
                }

            # 验证返回数据的完整性
            required_fields = ["score", "benchmark_score", "matched_reason", "missing_reason"]
            for field in required_fields:
                if field not in raw_response:
                    raw_response[field] = 0 if "score" in field else "数据不完整"

            print(raw_response)

            return raw_response

        except Exception as e:
            return {
                "score": 0,
                "benchmark_score": 60,
                "matched_reason": f"评估过程中发生错误：{str(e)}",
                "missing_reason": "请检查输入数据格式是否正确"
            }

    def _extract_resume_fields(self, keys):
        """
        从简历信息中提取指定字段

        :param keys: 字段名或字段名列表
        :return: 提取的信息（字符串或字典）
        """
        if isinstance(keys, str):
            keys = [keys]

        extracted = {}
        for key in keys:
            if key in self.resume_info:
                extracted[key] = self.resume_info[key]

        return extracted if extracted else None

    @staticmethod
    def _extract_job_fields(num, keys):
        """
        从岗位信息中提取指定字段（需要结合 Neo4j 或其他数据源）
        :param num: 岗位类别编号
        :param keys: 字段名或字段名列表
        :return: 提取的信息（字符串或字典）
        """
        extracted = {}
        for key in keys:
            fp_job_info = FileProcessor(f"log/{num}_{key}.json")
            extracted[key] = fp_job_info.read()

        return extracted if extracted else None

    def cal_score(self, job_num: str = "0"):
        """
        计算简历与岗位的七维度匹配评分

        :param job_num: 职业类别节点ID，用于读取对应的岗位信息文件（默认"0"）
        :return: 包含七个维度评分结果的字典
        """

        # 维度1: 专业技能 (professional_skill)
        professional_skill_result = self.match(
            resume_keys=["skills", "certificates", "projectExperience"],
            job_num=job_num,
            job_keys=["职业技能概述", "证书要求概述"],
            prompt="""请评估我的专业技能与岗位要求的匹配程度。

    评价标准：
    1. **核心技术栈匹配度**（权重40%）：
       - 90-100分：完全掌握岗位要求的核心技术栈，且有相关项目经验
       - 75-89分：掌握大部分核心技术，缺少1-2项次要技术
       - 60-74分：掌握基础技术，但缺少关键核心技术
       - 40-59分：仅掌握少量相关技术，差距较大
       - 0-39分：几乎不掌握岗位要求的技术

    2. **技术深度与广度**（权重30%）：
       - 90-100分：在多个技术领域有深入理解，能解决复杂问题
       - 75-89分：在主要技术领域有较好理解，能独立完成开发
       - 60-74分：具备基本开发能力，但深度不足
       - 40-59分：仅了解表面概念，实践经验有限
       - 0-39分：缺乏实际应用能力

    3. **工程化能力**（权重20%）：
       - 包括代码规范、性能优化、测试用例编写、工具链使用等
       - 根据项目经历中体现的工程化意识评分

    4. **加分技能**（权重10%）：
       - GIS开发、视频编解码、AI辅助调试等岗位特定技能
       - 作为额外加分项考虑

    关键词参考：React、Vue、HTML5、CSS3、JavaScript、TypeScript、Webpack、性能优化、组件化开发、响应式布局"""
        )

        # 维度2: 创新能力 (innovation_ability)
        innovation_ability_result = self.match(
            resume_keys=["projectExperience", "summary", "other"],
            job_num=job_num,
            job_keys=["创新能力评分"],
            prompt="""请评估我的创新能力与岗位要求的匹配程度。

    评价标准：
    1. **问题解决能力**（权重35%）：
       - 90-100分：能通过创新方法解决复杂技术问题，有独立研发经验
       - 75-89分：能提出改进方案，优化现有解决方案
       - 60-74分：能解决常规问题，但缺乏创新思维
       - 40-59分：依赖现成方案，解决问题能力一般
       - 0-39分：缺乏独立思考和问题解决能力

    2. **新技术探索与应用**（权重30%）：
       - 90-100分：主动学习并应用前沿技术，有技术博客或开源贡献
       - 75-89分：关注技术动态，能快速学习新工具
       - 60-74分：愿意学习新技术，但主动性一般
       - 40-59分：被动接受新技术，学习速度较慢
       - 0-39分：抗拒变化，固守旧技术

    3. **产品思维与用户体验优化**（权重20%）：
       - 能否从用户角度思考，提出创新性交互方案
       - 在项目经历中是否体现产品优化意识

    4. **技术创新成果**（权重15%）：
       - 是否有专利、技术文章、开源项目等创新成果
       - 是否在项目中引入新技术提升效率

    关键词参考：创新思维、技术钻研、主动性强、学习能力、技术博客、开源贡献"""
        )

        # 维度3: 学习能力 (learning_ability)
        learning_ability_result = self.match(
            resume_keys=["education", "major", "skills", "projectExperience", "summary"],
            job_num=job_num,
            job_keys=["学习能力评分"],
            prompt="""请评估我的学习能力与岗位要求的匹配程度。

    评价标准：
    1. **学历背景与专业相关性**（权重25%）：
       - 90-100分：名校计算机相关专业，理论基础扎实
       - 75-89分：本科及以上学历，专业相关或自学能力强
       - 60-74分：学历达标，专业不完全相关但有转行经历
       - 40-59分：学历较低或专业完全不相关
       - 0-39分：缺乏系统学习背景

    2. **技术成长轨迹**（权重35%）：
       - 90-100分：项目经历显示快速掌握多项新技术，技术栈持续升级
       - 75-89分：能在学习后应用新技术，有明显的进步轨迹
       - 60-74分：学习速度一般，需要较长时间适应
       - 40-59分：技术栈长期不变，缺乏成长
       - 0-39分：无法胜任新任务

    3. **自主学习意识**（权重25%）：
       - 90-100分：有系统性学习计划，参与培训/认证，有技术分享
       - 75-89分：主动学习，关注技术社区
       - 60-74分：按需学习，缺乏系统性
       - 40-59分：被动学习，依赖他人指导
       - 0-39分：缺乏学习动力

    4. **知识迁移能力**（权重15%）：
       - 能否将已有知识应用到新领域
       - 跨领域项目的成功经验

    关键词参考：好学、主动性强、钻研精神、技术培训、认证证书、技术分享"""
        )

        # 维度4: 抗压能力 (stress_resistance)
        stress_resistance_result = self.match(
            resume_keys=["internshipExperience", "projectExperience", "practicalExperience", "summary"],
            job_num=job_num,
            job_keys=["抗压能力评分"],
            prompt="""请评估我的抗压能力与岗位要求的匹配程度。

    评价标准：
    1. **高强度工作经历**（权重35%）：
       - 90-100分：有互联网大厂或创业公司高强度工作经历，能适应加班和紧急交付
       - 75-89分：有项目管理经验，能在压力下按时交付
       - 60-74分：有一定压力下的工作经验
       - 40-59分：主要在轻松环境下工作
       - 0-39分：无任何压力环境工作经历

    2. **多任务处理能力**（权重25%）：
       - 90-100分：能同时处理多个复杂项目，优先级管理出色
       - 75-89分：能有效管理2-3个并行任务
       - 60-74分：能处理多任务但效率一般
       - 40-59分：单任务处理尚可，多任务易混乱
       - 0-39分：无法应对多任务

    3. **挫折应对与情绪管理**（权重25%）：
       - 90-100分：面对技术难题和客户压力能保持冷静，积极寻求解决方案
       - 75-89分：能承受一定压力，偶尔需要支持
       - 60-74分：压力下表现波动较大
       - 40-59分：容易焦虑，影响工作效率
       - 0-39分：无法承受工作压力

    4. **沟通协调中的抗压表现**（权重15%）：
       - 在与客户、团队成员沟通时的表现
       - 处理冲突和分歧的能力

    关键词参考：加班、紧急交付、多项目并行、客户沟通、团队协作、deadline"""
        )

        # 维度5: 沟通表达 (communication_ability)
        communication_ability_result = self.match(
            resume_keys=["internshipExperience", "projectExperience", "practicalExperience", "hobbies"],
            job_num=job_num,
            job_keys=["沟通能力评分"],
            prompt="""请评估我的沟通表达能力与岗位要求的匹配程度。

    评价标准：
    1. **团队协作经验**（权重35%）：
       - 90-100分：有大型团队（15人以上）管理经验，跨部门协作经验丰富
       - 75-89分：有小团队（5-15人）协作经验，能有效沟通
       - 60-74分：有基本的团队合作经验
       - 40-59分：主要以个人工作为主，协作经验有限
       - 0-39分：缺乏团队合作经验

    2. **客户/需求方沟通能力**（权重30%）：
       - 90-100分：有丰富的客户需求对接经验，能准确理解并传达技术方案
       - 75-89分：能与非技术人员有效沟通技术概念
       - 60-74分：基本能完成需求沟通
       - 40-59分：沟通存在障碍，需要他人协助
       - 0-39分：缺乏对外沟通经验

    3. **文档与表达能力**（权重20%）：
       - 90-100分：技术文档清晰规范，有技术分享或演讲经验
       - 75-89分：能编写清晰的技术文档
       - 60-74分：文档质量一般
       - 40-59分：表达能力较弱
       - 0-39分：缺乏书面表达能力

    4. **冲突解决能力**（权重15%）：
       - 在团队分歧中的协调能力
       - 处理意见不合的技巧

    关键词参考：团队协作、跨部门沟通、客户需求、技术分享、文档编写、团队管理"""
        )

        # 维度6: 核心实习经历 (internship_experience)
        internship_experience_result = self.match(
            resume_keys=["internshipExperience", "projectExperience"],
            job_num=job_num,
            job_keys=["工作经验概述", "实践能力评分"],
            prompt="""请评估我的实习/工作经历与岗位要求的匹配程度。

    评价标准：
    1. **实习时长与连续性**（权重30%）：
       - 90-100分：有6个月以上连续实习经历，或多段相关实习累计1年以上
       - 75-89分：有3-6个月实习经历
       - 60-74分：有1-3个月短期实习
       - 40-59分：仅有课程项目，无实际实习
       - 0-39分：完全无相关经历

    2. **工作内容相关性**（权重35%）：
       - 90-100分：实习内容与目标岗位高度相关，承担核心开发任务
       - 75-89分：工作内容较为相关，参与主要功能开发
       - 60-74分：有一定相关性，但多为辅助性工作
       - 40-59分：相关性较低
       - 0-39分：完全不相关

    3. **实习公司平台**（权重20%）：
       - 90-100分：知名互联网公司或行业领先企业实习经历
       - 75-89分：中型企业或 startups 实习经历
       - 60-74分：小型公司实习
       - 40-59分：非相关行业实习
       - 0-39分：无实习经历

    4. **成果与影响力**（权重15%）：
       - 实习期间的项目成果、获得的认可
       - 是否有转正offer或推荐信

    关键词参考：实习时长、前端开发、项目经验、互联网公司、转正机会、核心功能"""
        )

        # 维度7: 团队协作 (teamwork_ability)
        teamwork_ability_result = self.match(
            resume_keys=["projectExperience", "internshipExperience", "practicalExperience"],
            job_num=job_num,
            job_keys=["团队合作能力评分"],
            prompt="""请评估我的团队协作能力与岗位要求的匹配程度。

    评价标准：
    1. **团队合作经验**（权重35%）：
       - 90-100分：有多个大型团队协作项目经验，担任过Team Leader或核心角色
       - 75-89分：有稳定的团队合作经验，能有效配合他人
       - 60-74分：有基本的团队合作经历
       - 40-59分：主要以个人工作为主
       - 0-39分：缺乏团队合作经验

    2. **协作工具使用**（权重25%）：
       - 90-100分：熟练使用Git、Jira、Confluence等协作工具，有良好的代码审查习惯
       - 75-89分：能使用主流协作工具
       - 60-74分：会使用基本工具
       - 40-59分：工具使用不熟练
       - 0-39分：不熟悉协作工具

    3. **团队贡献意识**（权重25%）：
       - 90-100分：主动帮助团队成员，分享知识，推动团队进步
       - 75-89分：愿意协助他人，积极参与团队活动
       - 60-74分：完成本职工作，较少主动贡献
       - 40-59分：较为被动
       - 0-39分：缺乏团队意识

    4. **集体活动参与**（权重15%）：
       - 通过兴趣爱好、实践活动判断团队合作精神
       - 体育团队、社团活动等经历

    关键词参考：团队协作、代码审查、知识分享、敏捷开发、Git协作、团队精神"""
        )

        # 汇总结果
        dimension_analysis = {
            "professional_skill": professional_skill_result,
            "innovation_ability": innovation_ability_result,
            "learning_ability": learning_ability_result,
            "stress_resistance": stress_resistance_result,
            "communication_ability": communication_ability_result,
            "internship_experience": internship_experience_result,
            "teamwork_ability": teamwork_ability_result
        }

        score = 0

        for key, value in dimension_analysis.items():
            score += value["score"] * self.rate[key]


        return score, dimension_analysis

    def cal_score_simple(self, job_num: str = "0"):
        """
        计算简历与岗位的七维度匹配评分（优化版：仅调用一次模型）

        :param job_num: 职业类别节点ID，用于读取对应的岗位信息文件（默认"0"）
        :return: 包含七个维度评分结果的字典
        """

        # Step 1: 提取所有简历字段
        resume_data = self._extract_resume_fields([
            "skills", "certificates", "projectExperience",
            "summary", "other", "education", "major",
            "internshipExperience", "practicalExperience", "hobbies"
        ])

        # Step 2: 提取所有岗位字段
        job_data = self._extract_job_fields(job_num, [
            "职业技能概述", "证书要求概述", "创新能力评分",
            "学习能力评分", "抗压能力评分", "沟通能力评分",
            "工作经验概述", "实践能力评分", "团队合作能力评分"
        ])

        if not resume_data or not job_data:
            default_result = {
                "score": 0,
                "benchmark_score": 60,
                "matched_reason": "简历或岗位信息缺失，无法进行匹配评估",
                "missing_reason": "请补充完整的简历信息或岗位要求"
            }
            dimension_analysis = {
                "professional_skill": default_result.copy(),
                "innovation_ability": default_result.copy(),
                "learning_ability": default_result.copy(),
                "stress_resistance": default_result.copy(),
                "communication_ability": default_result.copy(),
                "internship_experience": default_result.copy(),
                "teamwork_ability": default_result.copy()
            }
            return 0, dimension_analysis

        # Step 3: 构建统一的评估 prompt（一次性评估所有维度）
        p = f'''
        你是一个专业的简历-岗位匹配评估专家。请根据我提供的简历信息和岗位要求，对以下7个维度进行量化匹配评分。

        # 核心原则（必须严格遵守）：
        1. **客观公正**：基于事实进行评判，避免主观臆断
        2. **证据导向**：每个评分结论都必须有明确的原文依据
        3. **全面考量**：综合考虑要求的强制性和候选人的满足程度
        4. **建设性反馈**：提供具体、可操作的提升建议

        # 输入数据：

        ## 简历信息：
        {json.dumps(resume_data, ensure_ascii=False, indent=2)}

        ## 岗位要求：
        {json.dumps(job_data, ensure_ascii=False, indent=2)}

        # 评估任务：
        请对以下7个维度分别进行评估，每个维度都需要给出：
        - score: 个人在该维度的得分（1-100的整数）
        - benchmark_score: 该岗位在该维度的基准要求得分（统一为60分）
        - matched_reason: 匹配理由/现状分析（100-150字）
        - missing_reason: 缺失理由/提升建议（100-150字）

        ## 维度1: professional_skill（专业技能）
        评价标准：
        1. **核心技术栈匹配度**（权重40%）：完全掌握(90-100)、大部分掌握(75-89)、基础掌握(60-74)、少量掌握(40-59)、几乎不掌握(0-39)
        2. **技术深度与广度**（权重30%）：深入理解多领域(90-100)、主要领域较好(75-89)、基本开发能力(60-74)、表面概念(40-59)、缺乏应用能力(0-39)
        3. **工程化能力**（权重20%）：代码规范、性能优化、测试用例、工具链使用等
        4. **加分技能**（权重10%）：岗位特定技能作为额外加分
        关键词参考：React、Vue、HTML5、CSS3、JavaScript、TypeScript、Webpack、性能优化、组件化开发

        ## 维度2: innovation_ability（创新能力）
        评价标准：
        1. **问题解决能力**（权重35%）：创新解决复杂问题(90-100)、提出改进方案(75-89)、解决常规问题(60-74)、依赖现成方案(40-59)、缺乏独立思考(0-39)
        2. **新技术探索与应用**（权重30%）：主动应用前沿技术(90-100)、关注技术动态(75-89)、愿意学习(60-74)、被动接受(40-59)、抗拒变化(0-39)
        3. **产品思维与用户体验优化**（权重20%）：从用户角度思考，提出创新性交互方案
        4. **技术创新成果**（权重15%）：专利、技术文章、开源项目等
        关键词参考：创新思维、技术钻研、主动性强、技术博客、开源贡献

        ## 维度3: learning_ability（学习能力）
        评价标准：
        1. **学历背景与专业相关性**（权重25%）：名校相关专业(90-100)、本科及以上相关(75-89)、学历达标但专业不完全相关(60-74)、学历较低或不相关(40-59)、缺乏系统学习背景(0-39)
        2. **技术成长轨迹**（权重35%）：快速掌握多项新技术(90-100)、能应用新技术有进步(75-89)、学习速度一般(60-74)、技术栈长期不变(40-59)、无法胜任新任务(0-39)
        3. **自主学习意识**（权重25%）：系统性学习计划(90-100)、主动学习(75-89)、按需学习(60-74)、被动学习(40-59)、缺乏学习动力(0-39)
        4. **知识迁移能力**（权重15%）：将已有知识应用到新领域的能力
        关键词参考：好学、主动性强、钻研精神、技术培训、认证证书、技术分享

        ## 维度4: stress_resistance（抗压能力）
        评价标准：
        1. **高强度工作经历**（权重35%）：大厂或创业公司高强度经历(90-100)、项目管理经验(75-89)、一定压力下工作(60-74)、轻松环境工作(40-59)、无压力环境经历(0-39)
        2. **多任务处理能力**（权重25%）：同时处理多个复杂项目(90-100)、有效管理2-3个并行任务(75-89)、能处理多任务但效率一般(60-74)、单任务尚可(40-59)、无法应对多任务(0-39)
        3. **挫折应对与情绪管理**（权重25%）：保持冷静积极寻求方案(90-100)、能承受一定压力(75-89)、压力下表现波动(60-74)、容易焦虑(40-59)、无法承受压力(0-39)
        4. **沟通协调中的抗压表现**（权重15%）：与客户、团队沟通时的表现
        关键词参考：加班、紧急交付、多项目并行、客户沟通、团队协作、deadline

        ## 维度5: communication_ability（沟通表达）
        评价标准：
        1. **团队协作经验**（权重35%）：大型团队(15人以上)管理经验(90-100)、小团队(5-15人)协作经验(75-89)、基本团队合作经验(60-74)、个人工作为主(40-59)、缺乏团队合作经验(0-39)
        2. **客户/需求方沟通能力**（权重30%）：丰富客户需求对接经验(90-100)、能与非技术人员有效沟通(75-89)、基本完成需求沟通(60-74)、沟通存在障碍(40-59)、缺乏对外沟通经验(0-39)
        3. **文档与表达能力**（权重20%）：技术文档清晰规范且有分享经验(90-100)、能编写清晰文档(75-89)、文档质量一般(60-74)、表达能力较弱(40-59)、缺乏书面表达能力(0-39)
        4. **冲突解决能力**（权重15%）：在团队分歧中的协调能力
        关键词参考：团队协作、跨部门沟通、客户需求、技术分享、文档编写、团队管理

        ## 维度6: internship_experience（核心实习经历）
        评价标准：
        1. **实习时长与连续性**（权重30%）：6个月以上或多段累计1年以上(90-100)、3-6个月实习(75-89)、1-3个月短期实习(60-74)、仅有课程项目(40-59)、完全无相关经历(0-39)
        2. **工作内容相关性**（权重35%）：高度相关承担核心任务(90-100)、较为相关参与主要功能(75-89)、有一定相关性多为辅助(60-74)、相关性较低(40-59)、完全不相关(0-39)
        3. **实习公司平台**（权重20%）：知名互联网公司或行业领先企业(90-100)、中型企业或startups(75-89)、小型公司(60-74)、非相关行业(40-59)、无实习经历(0-39)
        4. **成果与影响力**（权重15%）：实习期间的项目成果、获得的认可、转正offer或推荐信
        关键词参考：实习时长、项目经验、互联网公司、转正机会、核心功能

        ## 维度7: teamwork_ability（团队协作）
        评价标准：
        1. **团队合作经验**（权重35%）：多个大型团队协作项目且担任核心角色(90-100)、稳定团队合作经验(75-89)、基本团队合作经历(60-74)、个人工作为主(40-59)、缺乏团队合作经验(0-39)
        2. **协作工具使用**（权重25%）：熟练使用Git/Jira/Confluence等有代码审查习惯(90-100)、能使用主流协作工具(75-89)、会使用基本工具(60-74)、工具使用不熟练(40-59)、不熟悉协作工具(0-39)
        3. **团队贡献意识**（权重25%）：主动帮助团队成员分享知识(90-100)、愿意协助他人积极参与(75-89)、完成本职工作较少主动(60-74)、较为被动(40-59)、缺乏团队意识(0-39)
        4. **集体活动参与**（权重15%）：通过兴趣爱好、实践活动判断团队合作精神
        关键词参考：团队协作、代码审查、知识分享、敏捷开发、Git协作、团队精神

        # 输出格式要求：
        仅返回一个标准的 JSON 对象，严格符合以下结构（不要有任何额外文本）：
        {{
          "professional_skill": {{
            "score": 整数(1-100),
            "benchmark_score": 60,
            "matched_reason": "字符串(100-150字)",
            "missing_reason": "字符串(100-150字)"
          }},
          "innovation_ability": {{
            "score": 整数(1-100),
            "benchmark_score": 60,
            "matched_reason": "字符串(100-150字)",
            "missing_reason": "字符串(100-150字)"
          }},
          "learning_ability": {{
            "score": 整数(1-100),
            "benchmark_score": 60,
            "matched_reason": "字符串(100-150字)",
            "missing_reason": "字符串(100-150字)"
          }},
          "stress_resistance": {{
            "score": 整数(1-100),
            "benchmark_score": 60,
            "matched_reason": "字符串(100-150字)",
            "missing_reason": "字符串(100-150字)"
          }},
          "communication_ability": {{
            "score": 整数(1-100),
            "benchmark_score": 60,
            "matched_reason": "字符串(100-150字)",
            "missing_reason": "字符串(100-150字)"
          }},
          "internship_experience": {{
            "score": 整数(1-100),
            "benchmark_score": 60,
            "matched_reason": "字符串(100-150字)",
            "missing_reason": "字符串(100-150字)"
          }},
          "teamwork_ability": {{
            "score": 整数(1-100),
            "benchmark_score": 60,
            "matched_reason": "字符串(100-150字)",
            "missing_reason": "字符串(100-150字)"
          }}
        }}

        # 质量检查清单（生成前自检）：
        ✓ 所有7个维度都已评估
        ✓ 每个维度的score都是1-100之间的整数
        ✓ 每个维度的benchmark_score都是60
        ✓ matched_reason和missing_reason都有具体内容且不重复
        ✓ JSON格式正确，可被json.loads()直接解析
        ✓ 不包含任何额外的字段或解释文本

        现在请开始评估，严格按照上述要求输出JSON结果：
        '''

        # Step 4: 调用 LLM 进行一次性的综合评估
        try:
            raw_response = model.call_ollama(p)

            if not raw_response:
                default_result = {
                    "score": 0,
                    "benchmark_score": 60,
                    "matched_reason": "模型调用失败，未获取到评估结果",
                    "missing_reason": "请稍后重试"
                }
                dimension_analysis = {
                    "professional_skill": default_result.copy(),
                    "innovation_ability": default_result.copy(),
                    "learning_ability": default_result.copy(),
                    "stress_resistance": default_result.copy(),
                    "communication_ability": default_result.copy(),
                    "internship_experience": default_result.copy(),
                    "teamwork_ability": default_result.copy()
                }
                return 0, 0, dimension_analysis

            # 验证返回数据的完整性
            required_dimensions = [
                "professional_skill", "innovation_ability", "learning_ability",
                "stress_resistance", "communication_ability", "internship_experience",
                "teamwork_ability"
            ]

            for dim in required_dimensions:
                if dim not in raw_response:
                    raw_response[dim] = {
                        "score": 0,
                        "benchmark_score": 60,
                        "matched_reason": "数据不完整",
                        "missing_reason": "请检查输入数据格式是否正确"
                    }
                else:
                    # 确保每个维度都有必需的字段
                    for field in ["score", "benchmark_score", "matched_reason", "missing_reason"]:
                        if field not in raw_response[dim]:
                            raw_response[dim][field] = 0 if field == "score" or field == "benchmark_score" else "数据不完整"

            print(f"岗位 {job_num} 综合评估完成")
            print(json.dumps(raw_response, ensure_ascii=False, indent=2))

            dimension_analysis = raw_response

        except Exception as e:
            print(f"岗位 {job_num} 评估过程中发生错误：{str(e)}")
            default_result = {
                "score": 0,
                "benchmark_score": 60,
                "matched_reason": f"评估过程中发生错误：{str(e)}",
                "missing_reason": "请检查输入数据格式是否正确"
            }
            dimension_analysis = {
                "professional_skill": default_result.copy(),
                "innovation_ability": default_result.copy(),
                "learning_ability": default_result.copy(),
                "stress_resistance": default_result.copy(),
                "communication_ability": default_result.copy(),
                "internship_experience": default_result.copy(),
                "teamwork_ability": default_result.copy()
            }

        # Step 5: 计算加权总分
        score = 0
        for key, value in dimension_analysis.items():
            if key in self.rate:
                score += value["score"] * self.rate[key]

        return dic_map[job_num], score, dimension_analysis

    def get_result(self):
        for i in range(6): # [6,15,30,39,50]
            self.scores.append(self.cal_score_simple(str(i)))

        self.scores.sort(key=lambda x: x[1], reverse=True)
        return self.scores


    # def get_embedding(self):
    #
    #     id = get_vector()

    def get_job_nums(self): # 从51个岗位中初步筛选较合适的
        return


    def get_jobs(self): # 获取前几个最匹配的具体岗位
        embedding = get_local_embedding()
        for key in match_map:
            vector_store_eg = get_vector(key, embedding)
            query = ""
            for i in match_map[key]:
                # 可能是字符串、列表、字典
                if isinstance(self.resume_info[i], str):
                    query += self.resume_info[i] + " "
                elif isinstance(self.resume_info[i], list):
                    query += " ".join(self.resume_info[i]) + " "
                elif isinstance(self.resume_info[i], dict):
                    for k, v in self.resume_info[i].items():
                        query += v + " "
            for doc, score in vector_store_eg.similarity_search_with_score(query=query, k=1):
                print(key)
                print("文本:", doc.page_content)
                print("关联岗位列表:", doc.metadata.get("关联岗位列表"))
                print("相似度分数:", round(score, 4))  # 分数越小越相似（通常0~1之间）
                print("---")


    # def match_single_job(self): # 找出简历最接近的几个岗位（从不同方面分析）
    #     # 新开一个，前面的可能没什么用
    #     embedding = get_local_embedding()
    #     vector_store_eg = get_vector("职业技能", embedding)
    #     for doc, score in vector_store_eg.similarity_search_with_score(query="你的问题", k=5):
    #         print("文本:", doc.page_content)
    #         print("职业类型列表:", doc.metadata.get("职业类型列表")) # 相似度从高到低
    #         print("相似度分数:", round(score, 4))  # 分数越小越相似（通常0~1之间）
    #         print("---")

