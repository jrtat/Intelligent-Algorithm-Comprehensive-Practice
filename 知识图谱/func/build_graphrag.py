from .utils.get_models import get_llm_silicon_flow,get_embedding_temp
from 知识图谱.func.utils.conn_neo4j import connect_neo4j

from langchain_community.callbacks import get_openai_callback
from langchain_core.documents import Document
from LLMGraphTransformer import LLMGraphTransformer
from LLMGraphTransformer.schema import NodeSchema, RelationshipSchema
from collections import defaultdict
from rapidfuzz import fuzz
from tqdm import tqdm
import numpy as np
import time

#--- 全局变量 ---#

node_schemas = [
    NodeSchema("职业类别"),
    NodeSchema("岗位", ["工作地点", "薪资范围", "学历要求","晋升路径", "福利待遇", "工作经验", "专业", "综合素质", "职业技能", "证书", "工作内容"]),
    NodeSchema("公司", ["行业", "公司描述", "企业规模", "融资阶段"])
]
relationship_schemas = [
    RelationshipSchema("岗位", "属于", "职业类别"),
    RelationshipSchema("岗位", "来自", "公司")
]

additional_instructions = """
请严格按照以下规则从文本中提取与“岗位”相关的属性这段内容：
- "岗位" 节点：是一个编号，例如 “CCL1464680980J40789256308”。
    - "学历要求"：提取专科、本科、硕士、博士、双一流、985、211 等学历或学校要求。
    - "专业"：提取要求毕业的专业，例如“植物保护等相关专业”、“计算机科学与技术、软件工程、通信工程等相关专业”。
    - "工作经验"：提取岗位对工作经历的要求，例如“经验不限”、“具备技术方案制定经验”、“两年以上工作经验”。
    - "晋升路径"：提取入职后的发展描述，例如“双通道（技术和管理）”、“纵向提升（普通员工→储备主管→中高层）”、“每年2次调薪机会”，“有效地竞聘晋升制度”、“职业发展路径：外派服务期为2年，期满后可根据意愿选择：1.继续驻外发展；2.调回国内从事国际服务管理岗位（如技术支持、培训协调等）”。
    - "福利待遇"：提取入职后除了薪资外的福利待遇，例如“五险一金”、“医疗、养老、工伤保险”、“春假”、“入职包住”、“组织组织员工参与旅游，体育等业余活动”。
    - "综合素质"节点：提取岗位需求的综合素质，例如“接受全国出差”、“强力的自驱力”、“沟通协调能力和团队合作精神”、“工作负责细心、学习能力强、责任心强”。
    - "职业技能"节点：提取岗位所需的具体能力，例如“了解FPGA/CPLD/AD/DA/FLASH”、“精通SpringCloud、SpringBoot、MyBatis”、“有丰富驾驶经验”，“掌据C/C++/Java/python/Go/JS一种或多种编程语言”。
    - "证书"节点：提取岗位要求的证书，例如“具备C1驾照”、“日语N3或以上”、“ORACLE、SQLServer 等 IT 资格认证”、“相关证书（如ISTQB）”。
    - "工作内容"节点：提取该岗位负责的具体工作内容，例如“为客户提供售后服务支持”、“按照测试计划搭建测试环境”、“配合负责人掌握工程进度情况”、“使用缺陷管理工具提交和跟踪问题”。

请格外注意遵守以下几点：
- 只提取 NodeSchema 和 RelationshipSchema 中已定义的节点和关系类型，不要 hallucinate 新类型。
- 属性值尽量保持原文表述，不要随意改写或总结。
"""

job_transforms = [
    {"prop": "综合素质", "label": "综合素质", "rel": "需要具有"},
    {"prop": "职业技能", "label": "职业技能", "rel": "需要掌握"},
    {"prop": "证书", "label": "证书", "rel": "需要持有"},
    {"prop": "工作内容", "label": "工作内容", "rel": "负责"},
    {"prop": "工作经验", "label": "工作经验", "rel": "需要拥有"},
    {"prop": "福利待遇", "label": "福利待遇", "rel": "提供"},
    {"prop": "专业", "label": "专业", "rel": "需要来自"},
]

company_transforms = [
    {"prop": "行业", "label": "行业", "rel": "涉及"},
]
job_remove = "p.综合素质, p.职业技能, p.证书, p.工作内容, p.福利待遇, p.专业, p.工作经验"
company_remove = "c.行业"

embedding_threshold_by_type = {
    "行业": 0.95,
    "专业": 0.88,
    "职业技能": 0.78
}
fuzzy_threshold_by_type = {
    "行业": 90,
    "专业": 88,
    "职业技能": 78
}
no_merge_type = { '岗位', '职业类别', '公司', '行业', '专业' } # 不判重的节点类型

def build_graphrag(raw_texts: list, init_type = 'add'): # 初始化整个 GraphRAG 系统
    """
    从文档中提取出节点和关联并写入知识图谱
    :param raw_texts: 字符串列表，其中每个字符串是一条招聘信息
    :param init_type: 为 'add' 表示向知识图谱中添加 raw_texts 提取出的节点和关联；
                      为 'rewrite' 表示清空知识图谱后再添加 raw_texts 提取出的节点和关联。
    :return: 无返回值
    """

    # Step 0：使用全局变量
    global node_schemas, relationship_schemas, additional_instructions

    # Step 1：把原始文本转成 LangChain Document 对象
    split_docs = [Document(page_content=text) for text in raw_texts]

    # Step 2：初始化 LLM 和 Embedding 模型
    rag_llm = get_llm_silicon_flow("deepseek-ai/DeepSeek-V2.5")

    # Step 4：创建 LLMGraphTransformer（把文本变成图结构）
    graph_transformer = LLMGraphTransformer(
        llm=rag_llm,
        allowed_nodes=node_schemas,  # 使用 NodeSchema 列表
        allowed_relationships=relationship_schemas,  # 使用 RelationshipSchema 列表
        strict_mode=True,  # 保持严格模式
        additional_instructions = additional_instructions # 增加一些解释
    )

    # Step 5：调用算法，把文本转成知识图谱的点和边（现已加入重试机制）
    graph_documents = [] # 存储结果
    max_retries = 3  # 配置最大重试次数
    retry_delay = 1  # 配置重试间隔（秒）

    for idx, doc in enumerate(tqdm(split_docs, desc="提取图谱")):
        for attempt in range(max_retries):
            try:
                with get_openai_callback() as cb:
                    graph_doc = graph_transformer.convert_to_graph_document(doc)  # 调用单个文档的转换方法
                    print(f"本次调用总计消耗Token: {cb.total_tokens}")
                    print(f"输入Token: {cb.prompt_tokens}")
                    print(f"输出Token: {cb.completion_tokens}")
                    graph_documents.append(graph_doc)
                break  # 成功则跳出重试循环

            except Exception as e:
                print(f"文档 {idx} 处理失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:  # 判断是否重试
                    time.sleep(retry_delay)
                else:
                    print(f"文档 {idx} 最终失败，已跳过。")

    print(f"成功提取 {len(graph_documents)} 个 GraphDocument（共 {len(split_docs)} 个文档）")

    # Step 6：连接 Neo4j 数据库 & 把图数据写入 Neo4j
    graph = connect_neo4j()

    if init_type == 'rewrite': # 是否要先清空数据库中原有信息
        graph.query("MATCH (n) DETACH DELETE n")

    graph.add_graph_documents(
        graph_documents,
        baseEntityLabel=True,  # 给所有实体节点加 __Entity__ 标签
        include_source=True  # 把原始文本也存成 Document 节点，建立 MENTIONS 关系
    )

    print("GraphRAG 初始化完成！")

def transform_properties_to_nodes():
    """
        负责复杂化知识图谱的结构，将以下属性提取为独立节点：
        - 岗位的：综合素质、职业技能、证书、工作经验、工作内容
        - 公司的：行业
        并建立对应关系：
        - 岗位的：需要具有、需要掌握、需要持有、需要拥有、负责
        - 公司的：涉及
        最后删除原属性
    """

    # Step 0： 声明全局变量
    global job_transforms, company_transforms, job_remove, company_remove

    # Step 1：与数据库建立连接
    graph = connect_neo4j()

    # Step 2：独立出岗位的属性
    for t in job_transforms:
        cypher_create = f"""
            MATCH (p:岗位)
            WHERE p.`{t['prop']}` IS NOT NULL
            WITH p,
                CASE 
                    WHEN valueType(p.`{t['prop']}`) STARTS WITH 'LIST' 
                    THEN p.`{t['prop']}`
                    ELSE 
                        [x IN 
                            split(
                                replace(
                                    replace(
                                        replace(
                                            replace(coalesce(p.`{t['prop']}`, ''), ',', '、'),
                                        '，', '、'),
                                    '；', '、'),
                                ';', '、'),
                            '、'
                        ) | trim(x)
                        ]
                END AS items
            UNWIND items AS item
            WITH p, trim(item) AS cleaned_value
            WHERE cleaned_value <> '' AND cleaned_value IS NOT NULL
            MERGE (n:{t['label']}:`__Entity__` {{__entity__: '{t['label']}', id: cleaned_value}})
            MERGE (p)-[:{t['rel']}]->(n)
        """
        # 1. 匹配所有标签为 岗位 的节点，并过滤出那些属性 t['prop'] 不为 null 的节点
        # 2. 首先尝试判断 p.属性 是否已经是一个列表：
        #        判断该属性值的类型是否以 'LIST' 开头（例如 'LIST' 或 'LIST??'）。
        #   如果已经是列表，直接使用原值。否则，需要按分隔符拆分：
        #        先用 coalesce 处理 null 值，将其转为空字符串 ''。
        #        然后连续使用 replace 将英文逗号 ,、中文逗号 ，、中文分号 ；、英文分号 ; 全部替换为顿号 、（统一分隔符）。
        #        最后用 split(..., '、') 按顿号拆分成字符串列表，再对每个元素执行 trim(x) 去除首尾空格，得到清理后的列表 items。
        # 3. 将列表展开为多行，每行一个 item。再次 trim 确保无首尾空格，命名为 cleaned_value。过滤掉空字符串或 NULL。
        # 4. 创建或匹配一个标签为 t['label']、属性 id 为 cleaned_value（属性 __entity__ 为 t['label']）的节点 n。
        # 5. 然后 MERGE 创建或匹配 p 到 n 的指定关系类型 t['rel']。使用 MERGE 避免重复创建。
        graph.query(cypher_create)
        print(f"已处理岗位属性：{t['prop']} → {t['label']} 节点")

    # 独立出公司的属性
    for t in company_transforms:
        cypher_create = f"""
            MATCH (c:公司)
            WHERE c.`{t['prop']}` IS NOT NULL
            WITH c,
                 CASE 
                     WHEN valueType(c.`{t['prop']}`) STARTS WITH 'LIST' 
                     THEN c.`{t['prop']}`
                     ELSE 
                         [x IN 
                             split(
                                 replace(
                                     replace(
                                         replace(
                                             replace(coalesce(c.`{t['prop']}`, ''), ',', '、'),
                                         '，', '、'),
                                     '；', '、'),
                                 ';', '、'),
                             '、'
                         ) | trim(x)
                         ]
                 END AS items
            UNWIND items AS item
            WITH c, trim(item) AS cleaned_value
            WHERE cleaned_value <> '' AND cleaned_value IS NOT NULL
            MERGE (i:{t['label']}:`__Entity__` {{__entity__: '{t['label']}', id: cleaned_value}})
            MERGE (c)-[:{t['rel']}]->(i)
        """
        # 1. 匹配所有标签为 公司 的节点，并过滤出那些属性 t['prop'] 不为 null 的节点
        # 2. 首先尝试判断 c.属性 是否已经是一个列表：
        #        判断该属性值的类型是否以 'LIST' 开头（例如 'LIST' 或 'LIST??'）。
        #   如果已经是列表，直接使用原值。否则，需要按分隔符拆分：
        #        先用 coalesce 处理 null 值，将其转为空字符串 ''。
        #        然后连续使用 replace 将英文逗号 ,、中文逗号 ，、中文分号 ；、英文分号 ; 全部替换为顿号 、（统一分隔符）。
        #        最后用 split(..., '、') 按顿号拆分成字符串列表，再对每个元素执行 trim(x) 去除首尾空格，得到清理后的列表 items。
        # 3. 将列表展开为多行，每行一个 item。再次 trim 确保无首尾空格，命名为 cleaned_value。过滤掉空字符串或 NULL。
        # 4. 创建或匹配一个标签为 t['label']、属性 id 为 cleaned_value （属性 __entity__ 为 t['label']）的节点 i。
        # 5. 然后 MERGE 创建或匹配 c 到 i 的指定关系类型 t['rel']。使用 MERGE 避免重复创建。
        graph.query(cypher_create)
        print(f"已处理公司属性：{t['prop']} → {t['label']} 节点")

    # Step 3：删除已提取的属性
    cypher_remove = f"""
    MATCH (p:岗位)
    REMOVE {job_remove}

    WITH 1 AS dummy
    MATCH (c:公司)
    REMOVE {company_remove}
    """
    graph.query(cypher_remove)
    print("已删除原属性")

    # Step 4：刷新schema
    graph.refresh_schema()
    print("当前 schema 已刷新。")

def deduplication(embedding_threshold = 0.82 , fuzzy_threshold = 82 ):
    """
    用来把知识图谱中含义相近的节点进行合并。

    .. warning::
    **【注意】** 如果要采用分批次写入知识图谱的策略，则要知道“在所有批次写入完后执行一次该函数”和“每批次都执行该函数”的结果会略有不同。

    :param embedding_threshold: 余弦相似度阈值
    :param fuzzy_threshold: 字符串模糊匹配阈值
    :return: 无返回值
    """

    # Step 0：声明全局变量
    global no_merge_type, embedding_threshold_by_type, fuzzy_threshold_by_type

    # Step 1：初始化 llm Embedding 模型 & 连接 Neo4j 数据库
    embeddings = get_embedding_temp()
    graph = connect_neo4j()

    # Step 2：查询并存储所有节点信息
    entities_query = """
            MATCH (n:__Entity__)
            RETURN 
                elementId(n) AS internal_id, 
                n.id AS name,
                labels(n) AS labels
            """
    # 定义一个 Cypher 查询字符串：匹配所有带有 __Entity__ 标签的节点，返回：
    # 1. elementId(n)：节点的内部 ID。
    # 2. n.id：节点的 id 属性，此处用作实体的名称（name）。
    # 3. labels(n)：节点拥有的所有标签（列表形式）。
    entity_records = graph.query(entities_query)
    # 执行查询，获得所有匹配节点的记录列表，每条记录是一个字典，包含 internal_id、name、labels。

    entity_list = [] # 用于存储处理后的节点信息
    for r in entity_records: # 遍历每条记录（一条记录是一个实体）

        if not r.get("name"): # 若 name 字段为空（None 或空字符串），则跳过该节点（无效实体）
            continue

        node_labels = r["labels"] # 获取记录（节点）的类型列表
        entity_type = "__Entity__" # 提取记录（节点）的类型（如果没有别的标签就用"__Entity__"，否则优先其他类型）
        for label in node_labels:
            if label != "__Entity__":
                entity_type = label
                break

        entity_list.append({
            "internal_id": r["internal_id"],
            "name": r["name"],
            "type": entity_type
        }) # 将每个记录（节点）的内部 ID、名称、类型作为字典追加到 entity_list 中。

    names = [e["name"] for e in entity_list] # 提取所有节点的名称列表 names。
    vectors = embeddings.embed_documents(names) # 调用 embeddings 模型为所有名称批量生成向量表示，结果 vectors 是一个列表，每个元素是对应名称的向量。

    # Step 3：遍历每个节点，尝试找到能被合并的点，组成族群
    groups = defaultdict(list) # 字典，键为“代表节点”的索引，值为该族群包含的所有节点索引列表（初始为空列表）。用于记录哪些节点应合并到同一组。
    visited = set() # 记录节点是否已经被分到一个族群
    for i in range(len(entity_list)): # 遍历所有节点索引 i
        if i in visited: # 若 i 已经被访问过，跳过
            continue

        current_type = entity_list[i]["type"] # 获取当前节点 i 的类型 current_type。
        emb_thresh = embedding_threshold_by_type.get(current_type, embedding_threshold)  # 从字典中获取该类型对应的余弦相似度阈值，若不存在则使用默认值 embedding_threshold。
        fuzzy_thresh = fuzzy_threshold_by_type.get(current_type, fuzzy_threshold) # 从字典中获取该类型对应的模糊匹配阈值，若不存在则使用默认值 fuzzy_threshold。

        groups[i].append(i) # 初始化当前族群：将节点 i 自身加入 groups[i] 列表中
        visited.add(i) # 标记 i 为已访问

        for j in range(i + 1, len(entity_list)): # 遍历从 i+1 到末尾的所有节点索引 j
            if j in visited: # 若 j 已属于其他族群，跳过
                continue

            if current_type in no_merge_type or entity_list[j]["type"] in no_merge_type: # 避免合并 no_merge_type 中的类型
                continue

            if current_type != entity_list[j]["type"]: # 避免两个不同类型的节点合并
                continue

            is_similar_to_group = False # 初始化标志 is_similar_to_group 为 False。
            for member_idx in groups[i]: # 对当前族群中的每个已有成员（member_idx），依次检查节点 j 与该成员的相似度（只要有一个就算）
                vec_member = np.array(vectors[member_idx])
                vec_j = np.array(vectors[j]) # 将两个节点的向量转换为 NumPy 数组。
                cos_sim = np.dot(vec_member, vec_j) / (
                        np.linalg.norm(vec_member) * np.linalg.norm(vec_j) + 1e-8) # 计算余弦相似度
                fuzzy_score = fuzz.ratio(entity_list[member_idx]["name"], entity_list[j]["name"]) # 调用 fuzz.ratio 计算两个节点名称的字符串相似度

                if cos_sim >= emb_thresh or fuzzy_score >= fuzzy_thresh: # 使用当前类型对应的阈值进行判断
                    is_similar_to_group = True
                    break

            if is_similar_to_group: # 若 j 与族群中的至少一个成员相似
                groups[i].append(j) # 则将 j 加入当前族群（groups[i]）
                visited.add(j) # 将 j 标记为已访问

    # Step 4：合并找到的族群，并将修改同步到Neo4j
    merged_count = 0 # 统计总共合并的重复实体数量
    for canonical_idx, dup_indices in groups.items(): # 遍历每个族群：canonical_idx 是代表节点的索引，dup_indices 是该族群所有节点索引列表
        if len(dup_indices) <= 1: # 若族群长度 ≤ 1，无需合并，跳过
            continue

        node_element_ids = [entity_list[idx]["internal_id"] for idx in dup_indices] # 收集该族群中所有节点的内部 ID 列表。
        canonical_name = entity_list[canonical_idx]["name"] # 代表节点的名称（canonical_name）将作为合并后保留的名称
        entity_type = entity_list[canonical_idx]["type"] # 代表节点的类型作为该族群类型（用于打印信息）

        print(f"  合并 → {canonical_name}  (类型: {entity_type}, 合并 {len(dup_indices) - 1} 个)")

        merge_cypher = """
                MATCH (n:__Entity__)
                WHERE elementId(n) IN $nodeElementIds
                WITH collect(n) AS nodes
                CALL apoc.refactor.mergeNodes(nodes, {
                    properties: 'combine',
                    mergeRels: true
                })
                YIELD node
                SET node.id = $canonicalName
                RETURN node
            """ # 定义 Cypher 查询，使用 APOC 库的 apoc.refactor.mergeNodes 过程合并一组节点：
                #   1. 匹配所有内部 ID 在 $nodeElementIds 列表中的 __Entity__ 节点。
                #   2. 将匹配到的节点收集到列表 nodes。
                #   3. 调用 mergeNodes，参数
                #        properties: 'combine' 表示合并时属性冲突则组合（保留非空值或合并列表等）
                #        mergeRels: true 表示同时合并关系（重复关系去重）。
                #   4. YIELD node：返回合并后的代表节点。
                #   5. 将该节点的 id 属性设置为 $canonicalName（即保留的代表名称）。
                #   6. RETURN node 返回节点（实际上仅用于执行）

        graph.query(merge_cypher, {
            "nodeElementIds": node_element_ids,
            "canonicalName": canonical_name
        }) # 执行上述 Cypher 查询，传入参数：节点内部 ID 列表和规范名称。

        merged_count += len(dup_indices) - 1  # 累计合并的实体数量（除代表节点外的节点数）。

    print(f"实体去重完成！共合并 {merged_count} 个重复实体")



#--- 最终我们期望达到的图结构 ---#

'''
node_schemas = [
    NodeSchema("职业类别"),
    NodeSchema("岗位", ["工作地点", "薪资范围", "学历要求","晋升路径", "福利待遇"]),
    NodeSchema("公司", ["行业", "公司描述", "企业规模", "融资阶段"]),
    NodeSchema("证书"),
    NodeSchema("综合素质"),
    NodeSchema("职业技能"),
    NodeSchema("工作内容"),
    NodeSchema("专业")
]

relationship_schemas = [
    RelationshipSchema("岗位", "属于", "职业类别"),
    RelationshipSchema("岗位", "来自", "公司"),
    RelationshipSchema("岗位", "需要具有", "综合素质"),
    RelationshipSchema("岗位", "需要掌握", "职业技能"),
    RelationshipSchema("岗位", "需要持有", "证书"),
    RelationshipSchema("岗位", "需要拥有", "工作经验"),
    RelationshipSchema("岗位", "负责", "工作内容"),
    RelationshipSchema("岗位", "需要来自", "专业"),
    RelationshipSchema("公司", "涉及", "行业")
]

'''

