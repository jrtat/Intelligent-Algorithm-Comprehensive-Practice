import json

from processor.utils.FileProcessor import FileProcessor
from processor.utils.LLMInvoker import LLMInvoker

model = LLMInvoker()

fp_map = FileProcessor("maps/num2jt.json")
dic_map = fp_map.read()

fp_result = FileProcessor("need_data/result.json")
# dic_result = fp_result.read()
dic_result = {}

# 需求类型 → 对应的关系类型
KNOWLEDGE_REL_MAP = {
    "综合素质": "需要具有", # 数值
    "职业技能": "需要掌握",
    "证书": "需要持有",
    "工作内容": "负责",
    "工作经验": "需要拥有",
    "专业": "需要来自",
    "福利待遇": "提供"
}

def batch_extract_info_neo4j(num: str, source_value: str, target: str, prompt: str):
    """
    从 neo4j 获取 Chunk 数据，提取信息后写回职业类别节点属性。

    :param num: 职业类别节点 ID
    :param source_type: 来源类型，"knowledge"（知识类型）或 "property"（属性类型）
    :param source_value: 具体值
                         - knowledge: 知识类型（综合素质、职业技能、证书、工作内容、专业、工作经验）
                         - property: 属性类型（学历要求、晋升路径）
    :param target: 目标属性名，将作为职业类别节点的新属性
    :param prompt: 提示词
    :return: 处理后的信息
    """
    fp = FileProcessor(f"need_data/{num}_{source_value}.json")
    dic = fp.read()

    jt = dic_map[num]

    # Step 2: 构建 prompt 并调用 LLM
    p = f'''
    你是一个专业的岗位画像分析助手。你的任务是从多个岗位的原始描述中，提取并生成【{target}】的准确描述和标签。
    
    ### 核心原则（必须严格遵守）：
    1. **真实性第一**：所有提取的内容必须有明确的原文依据，严禁无中生有、臆想编造
    2. **证据链完整**：每个特征/标签都必须能追溯到至少一条原文描述
    3. **过滤噪声**：自动识别并忽略无效内容（如："这是一个招聘信息"、空字符串、纯标点等）
    4. **宁缺毋滥**：如果原文信息不足以支撑某个特征，宁可放弃也不要强行提取
    
    ### 任务要求：
    {prompt}
    
    ### 输入数据说明：
    你将收到一个 JSON 对象，其中：
    - **键（Key）**：初步提取的特征/标签名称
    - **值（Value）**：该特征对应的多条原始岗位描述文本数组
    
    ### 处理步骤：
    
    #### 第一步：数据清洗与验证
    对每个特征进行严格验证：
    1. **过滤无效原文**：剔除以下类型的原文：
       - 包含"这是一个招聘信息"的文本
       - 纯空白、纯标点符号的文本
       - 长度小于5个字符的文本
       - 与特征明显无关的文本（如特征是"Python编程"，原文是"团队合作精神"）
    
    2. **特征有效性判断**：
       - 检查特征是否有至少1条有效原文支撑
       - 如果没有有效原文，直接丢弃该特征
       - 标记每个特征的置信度（高/中/低）
    
    #### 第二步：特征整合与去重
    1. **合并相似特征**：将语义相近的特征合并（如"React开发"和"React框架使用"）
    2. **消除矛盾**：如果同一特征的不同原文存在矛盾，标注冲突点
    3. **频次统计**：记录每个特征在多少条原文中出现
    
    #### 第三步：生成岗位画像描述
    基于验证后的特征，生成一段连贯的岗位画像描述：
    - 突出高频、高置信度的核心要求
    - 区分"必备技能"和"加分项"
    - 保持语言专业、简洁、准确
    - 控制在200-500字之间
    
    #### 第四步：提取标准化标签
    从有效特征中提取5-15个关键标签：
    - 标签应该是名词短语或动宾结构（如："React开发"、"团队协作"）
    - 避免过于宽泛的标签（如："技术能力"）
    - 避免过于具体的实现细节（如："使用Axios发起GET请求"）
    - 按重要性排序
    
    ### 输出格式要求：
    仅返回一个标准的 JSON 对象，格式如下：
    {{
      "{target}_description": "岗位画像的具体描述文本（200-500字）",
      "{target}_tags": ["标签1", "标签2", "标签3", ...],
      "{target}_features": [
        {{
          "feature_name": "特征名称",
          "confidence": "high/medium/low",
          "frequency": 出现次数,
          "evidence_count": 有效原文数量,
          "sample_evidence": ["原文1", "原文2"]
        }}
      ],
      "_metadata": {{
        "total_raw_items": 原始特征总数,
        "valid_features": 有效特征数,
        "filtered_noise_count": 过滤的噪声数量,
        "processing_notes": "处理说明（如有特殊情况）"
      }}
    }}
    
    ### 质量检查清单（生成前自检）：
    ✓ 每个标签都能在 {target}_features 中找到对应特征
    ✓ 描述中没有出现原文中不存在的信息
    ✓ 已过滤所有"这是一个招聘信息"等噪声数据
    ✓ 特征与原文的相关性经过人工可验证
    ✓ JSON 格式正确，可被 json.loads() 直接解析
    
    ### 提供的信息：
    {json.dumps(dic, ensure_ascii=False, indent=2)}
    
    现在请开始分析，严格按照上述要求输出 JSON 结果：
    '''

    raw_response = model.call_ollama(p)

    if not raw_response:
        print(f"职业类别 (key={jt}) 信息解析失败")
        return

    # Step 3: 将结果写入职业类别节点
    result_value = raw_response.get(f"{target}_description")
    if result_value is not None:
        if jt not in dic_result:
            dic_result[jt] = {}
        dic_result[jt][f"{target}_description"] = result_value
    else:
        print(f"LLM 返回结果中未找到 {target} 字段")

    fp_result.save(dic_result)
    fp_log = FileProcessor(f"log/{num}_{target}.json")
    fp_log.save(raw_response)

def batch_score_neo4j(num, source_value, target, prompt): # 打分函数
    pass


if __name__ == '__main__':

    # for i in dic_map.keys():
    i = "0"

    # for i in dic_map.keys():
    batch_extract_info_neo4j(
        num=i,
        # source_type="knowledge",
        source_value="职业技能",
        target="职业技能概述",
        prompt="""根据岗位信息，请提取该职业类别所需的核心技能要求。

    重点关注：
    1. 编程语言和框架（如 Python、React、Vue 等）
    2. 开发工具和技术栈（如 Git、Webpack、Docker 等）
    3. 专业能力领域（如前端开发、数据分析、系统设计等）
    4. 行业特定技能（如 GIS 开发、视频编解码等）

    要求：
    - 区分基础技能和高级技能
    - 标注技能的熟练程度要求（了解/熟悉/精通）
    - 合并重复或相似的技能项"""
        )

    # for i in dic_map.keys():
    batch_extract_info_neo4j(
        num=i,
        # source_type="knowledge",
        source_value="综合素质",
        target="综合素质概述",
        prompt="""根据岗位信息，请提取该职业类别所需的综合素质要求。

    重点关注：
    1. 沟通协作能力（团队合作、跨部门沟通等）
    2. 学习与适应能力（学习能力、抗压能力等）
    3. 工作态度与责任心（主动性、严谨性等）
    4. 问题解决能力（逻辑思维、创新能力等）

    要求：
    - 区分核心素质和加分项
    - 注意识别噪声数据（如"这是一个招聘信息"）
    - 合并语义相近的素质描述"""
        )

    # for i in dic_map.keys():
    batch_extract_info_neo4j(
        num=i,
        # source_type="knowledge",
        source_value="工作内容",
        target="工作内容概述",
        prompt="""根据岗位信息，请提取该职业类别的核心工作职责。

    重点关注：
    1. 日常开发任务（编码、调试、测试等）
    2. 项目参与角色（主导、协助、独立负责等）
    3. 技术实现内容（功能开发、性能优化、架构设计等）
    4. 协作工作内容（与产品、设计、后端的配合）

    要求：
    - 按重要性排序工作职责
    - 区分常规工作和专项工作
    - 过滤无效内容（如面试流程、公司介绍等）"""
        )

    # for i in dic_map.keys():
    batch_extract_info_neo4j(
        num=i,
        # source_type="knowledge",
        source_value="专业",
        target="专业背景概述",
        prompt="""根据岗位信息，请提取该职业类别的专业背景要求。

    重点关注：
    1. 核心专业（计算机科学与技术、软件工程等）
    2. 相关专业（电子信息、自动化、数学等）
    3. 专业限制程度（必须/优先/不限）
    4. 特殊专业要求（GIS、数字媒体等细分领域）

    要求：
    - 统计各专业的出现频次
    - 区分硬性要求和优先考虑
    - 注意识别无关内容（如公司产品介绍中的"自动化设备"）"""
        )

    # for i in dic_map.keys():
    batch_extract_info_neo4j(
        num=i,
        # source_type="knowledge",
        source_value="工作经验",
        target="工作经验概述",
        prompt="""根据岗位信息，请提取该职业类别的工作经验要求。

    重点关注：
    1. 工作年限要求（应届/1-3年/3-5年/5年以上）
    2. 项目经验类型（B端/C端/大型项目/完整周期等）
    3. 行业经验要求（电商/金融/GIS等行业背景）
    4. 特殊经验要求（带团队/开源项目/技术博客等）

    要求：
    - 明确最低年限要求
    - 区分必需经验和优先经验
    - 过滤噪声数据（大量"这是一个招聘信息"）"""
        )

    # for i in dic_map.keys():
    batch_extract_info_neo4j(
        num=i,
        # source_type="knowledge",
        source_value="证书",
        target="证书要求概述",
        prompt="""根据岗位信息，请提取该职业类别的证书和资质要求。

    重点关注：
    1. 职业资格证书（软考、PMP、AWS认证等）
    2. 职称要求（初级/中级/高级职称）
    3. 行业特定证书（电工证、教师资格证等）
    4. 语言证书（英语四六级、托福雅思等）

    要求：
    - 区分必须持有和优先考虑
    - 注意数据量可能较少
    - 如无明确要求，返回空列表而非编造"""
        )

    # for i in dic_map.keys():
    batch_extract_info_neo4j(
        num=i,
        # source_type="knowledge",
        source_value="福利待遇",
        target="福利待遇概述",
        prompt="""根据岗位信息，请提取该职业类别的福利待遇情况。

    重点关注：
    1. 薪酬结构（基本工资、绩效奖金、年终奖、股票期权等）
    2. 法定福利（五险一金、带薪年假、法定节假日等）
    3. 补充福利（餐补、交通补、住房补贴、体检等）
    4. 特色福利（团建旅游、培训机会、弹性工作等）

    要求：
    - 分类整理福利项目
    - 标注福利的具体标准（如有）
    - 过滤噪声数据（大量无关的公司介绍）"""
        )

    # for i in dic_map.keys():
    batch_extract_info_neo4j(
        num=i,
        # source_type="property",
        source_value="学历要求",
        target="学历要求概述",
        prompt="""根据岗位信息，请提取该职业类别的学历要求情况。

    重点关注：
    1. 最低学历门槛（大专/本科/硕士/博士）
    2. 院校偏好（985/211优先/海外学历等）
    3. 应届生政策（是否接受应届/实习转正等）
    4. 学历与经验的替代关系（如"学历不足可用经验弥补"）

    要求：
    - 统计不同学历层次的占比
    - 区分硬性要求和优先考虑
    - 注意是否有弹性空间"""
        )

    # for i in dic_map.keys():
    batch_extract_info_neo4j(
        num=i,
        # source_type="property",
        source_value="晋升路径",
        target="晋升路径概述",
        prompt="""根据岗位信息，请提取该职业类别的职业发展和晋升路径。

    重点关注：
    1. 晋升通道（技术通道/管理通道/双通道）
    2. 职级体系（助理→专员→组长→主管→经理等）
    3. 培养机制（导师制、培训计划、轮岗机会等）
    4. 发展空间（内部转岗、跨部门发展等）

    要求：
    - 描述清晰的职业发展路径
    - 突出公司提供的成长支持
    - 如信息不足，不要编造具体职级名称"""
        )

    print("所有数据处理完成")
