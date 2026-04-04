from utils.get_models import get_llm_temp,get_llm,get_embedding_temp,get_embedding
from utils.conn_neo4j import connect_neo4j

import os, time
from langchain_core.documents import Document
from LLMGraphTransformer import LLMGraphTransformer
from LLMGraphTransformer.schema import NodeSchema, RelationshipSchema
from langchain_community.graphs import Neo4jGraph
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 分块
from collections import defaultdict
from rapidfuzz import fuzz
from tqdm import tqdm
import numpy as np



#--- 初始化知识图谱 ---#
def init(raw_texts: list, init_type = 'add'): # 初始化整个 GraphRAG 系统

    # Step 0：使用全局变量
    global graph_url, graph_username, graph_password, database_name

    # Step 1：把原始文本分块，并转成 LangChain Document 对象
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # 分块大小
        chunk_overlap=150,  # 重叠部分大小，帮助保留跨块实体关系
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]  # 中文友好分隔符
    )
    split_docs = [Document(page_content=text) for text in raw_texts]
    # split_docs = text_splitter.split_documents(split_docs) # 未必需要分块

    # Step 2：初始化 LLM 和 Embedding 模型
    RAG_llm = get_llm()

    # Step 3：设置知识图谱的 schema（允许哪些节点和属性）
    # 1. 定义 NodeSchema
    node_schemas = [
        NodeSchema("职业类别"),  # 为每个节点类型指定属性
        NodeSchema("岗位ID", ["location","diploma","major","personal qualities"]),  # 例如，为岗位ID添加薪资范围属性
        NodeSchema("公司", ["industry","description"]),
        NodeSchema("技术能力", ["description"]),
        NodeSchema("证书")
    ]
    relationship_schemas = [
        RelationshipSchema("职业类别", "需要掌握", "技术能力"),
        RelationshipSchema("职业类别", "需要持有", "证书"),
        RelationshipSchema("岗位ID", "属于", "职业类别"),
        RelationshipSchema("岗位ID", "需要掌握", "技术能力"),
        RelationshipSchema("岗位ID", "需要持有", "证书"),
        RelationshipSchema("岗位ID", "来自于", "公司")
    ]

    # Step 4：创建 LLMGraphTransformer（把文本变成图结构）
    graph_transformer = LLMGraphTransformer(
        llm=RAG_llm,
        allowed_nodes=node_schemas,  # 使用 NodeSchema 列表
        allowed_relationships=relationship_schemas,  # 使用 RelationshipSchema 列表
        strict_mode=True,  # 保持严格模式
    )

    # Step 5：调用算法，把文本转成知识图谱的点和边（现已加入重试机制）
    graph_documents = [] # 存储结果
    max_retries = 3  # 配置最大重试次数
    retry_delay = 1  # 配置重试间隔（秒）

    for idx, doc in enumerate(tqdm(split_docs, desc="提取图谱")):
        success = False
        for attempt in range(max_retries):
            try:
                graph_doc = graph_transformer.convert_to_graph_document(doc) # 调用单个文档的转换方法
                graph_documents.append(graph_doc)
                success = True
                break  # 成功则跳出重试循环
            except Exception as e:
                print(f"文档 {idx} 处理失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1: # 判断是否重试
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

#--- 节点去重 ---#
def deduplication():

    # Step 0：使用全局变量 & 配置局部参数
    global graph_url, graph_username, graph_password, database_name
    embedding_threshold = 0.75  # embedding阈值
    fuzzy_threshold = 75  # 字符相似阈值
    NO_MERGE_TYPES = {
        '岗位id'
    }  # 不判重的节点类型

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
            """  # 一次性把所有节点的信息查出来，包括类型
    entity_records = graph.query(entities_query)  # 执行查询

    entity_list = []  # 存放处理后的实体信息
    for r in entity_records:
        if not r.get("name"):
            continue  # labels 通常是列表，如 ['__Entity__', '岗位编码']
        node_labels = r["labels"]
        entity_type = node_labels[-1] if len(node_labels) > 1 else "__Entity__"  # 取最后一个具体类型

        entity_list.append({
            "internal_id": r["internal_id"],
            "name": r["name"],
            "type": entity_type  # 记录实体类型
        })  # 把当前实体的三个关键信息打包成一个字典，追加到 entity_list 中

    names = [e["name"] for e in entity_list]  # 类型 list[str]，只提取所有实体的名称，用于批量向量化
    vectors = embeddings.embed_documents(names)  # 类型 list[list[float]]，每个实体名称对应的 Embedding 向量

    # Step 3：遍历每个节点，尝试找到能被合并的点，组成族群
    groups = defaultdict(list)  # group 存放去重后的分组
    visited = set()  # visit 记录一个节点是否已经被分组
    for i in range(len(entity_list)):  # 遍历每个节点
        if i in visited:
            continue

        current_type = entity_list[i]["type"]  # 得到当前的节点的类型
        groups[i].append(i)  # 将节点i当作一个新族群的第一个节点
        visited.add(i)  # 记录该节点（好像用不到）

        for j in range(i + 1, len(entity_list)):  # 遍历 i 之后的每个节点
            if j in visited:  # 如果该节点已经属于某个组，就跳过
                continue
            if current_type in NO_MERGE_TYPES or entity_list[j]["type"] in NO_MERGE_TYPES:  # 如果是“不允许合并”的类型，直接跳过
                continue
            if not (current_type == entity_list[j]["type"]):  # 如果两个节点类型不同，就跳过
                continue

            is_similar_to_group = False  # 检查 j 是否与当前组中【任意一个】成员相似
            for member_idx in groups[i]:  # 遍历当前组已有的所有成员
                vec_member = np.array(vectors[member_idx])  # 计算与该成员的相似度
                vec_j = np.array(vectors[j])
                cos_sim = np.dot(vec_member, vec_j) / (
                            np.linalg.norm(vec_member) * np.linalg.norm(vec_j) + 1e-8)  # 余弦相似度
                fuzzy_score = fuzz.ratio(entity_list[member_idx]["name"], entity_list[j]["name"])  # 混合相似度
                if cos_sim >= embedding_threshold or fuzzy_score >= fuzzy_threshold:
                    is_similar_to_group = True
                    break  # 只要找到一个相似，就不再继续检查

            if is_similar_to_group:  # 如果经鉴定后成立
                groups[i].append(j)  # 添加到族群
                visited.add(j)  # 记录已访问

    # Step 4：合并找到的族群，并将修改同步到Neo4j
    merged_count = 0
    for canonical_idx, dup_indices in groups.items():  # 遍历每个族群，将其写入 Neo4j
        if len(dup_indices) <= 1:
            continue

        node_element_ids = [entity_list[idx]["internal_id"] for idx in dup_indices]
        canonical_name = entity_list[canonical_idx]["name"]
        entity_type = entity_list[canonical_idx]["type"]

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
            """

        graph.query(merge_cypher, {
            "nodeElementIds": node_element_ids,
            "canonicalName": canonical_name
        })

        merged_count += len(dup_indices) - 1

    print(f"实体去重完成！共合并 {merged_count} 个重复实体")




