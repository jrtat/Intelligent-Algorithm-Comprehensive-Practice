import os
from langchain_core.documents import Document
from LLMGraphTransformer import LLMGraphTransformer
from LLMGraphTransformer.schema import NodeSchema, RelationshipSchema
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.graphs import Neo4jGraph
from langchain_huggingface import HuggingFaceEmbeddings # 本地 Embedding 模型
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 分块
from collections import defaultdict
from rapidfuzz import fuzz
import numpy as np

#--- 全局变量 ---#
database_name = "1f5dcc17"
graph_url = "neo4j+s://1f5dcc17.databases.neo4j.io"
graph_username = "1f5dcc17"
graph_password = "J1-Sv2VA6q5Qw3rH5vFQSmYCwMtuCpF8kqt-W0UrEDU"

#--- 初始化大模型的函数 ---#
def get_embedding(): # xjx实验室的模型
    return OpenAIEmbeddings(
        model="qwen3-embedding:8b",
        base_url="http://59.72.63.156:14138/v1",  # 自定义端点
        api_key="Empty",
        dimensions=1536,
        tiktoken_enabled=False,
        check_embedding_ctx_length=False
    )

def get_embedding_temp():  # 临时的Embedding模型
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",  # 中文效果很好的开源模型
        model_kwargs={'device': 'cpu'},  # 没有 GPU 就用 cpu
        encode_kwargs={'normalize_embeddings': True}
    )

def get_llm():
    return ChatOpenAI(
        model="qwen3:8b",  # 模型名字（xjx实验室）
        base_url="http://59.72.63.156:14138/v1", # url（xjx实验室）
        api_key="EMPTY",  # vLLM 不需要真实 key
        temperature=0  # 温度0 = 输出最稳定（对于提取图谱这个应用来说，0是最好的，不要调这个参数）
    )

def get_llm_temp():
    return ChatOpenAI(
        model = "Qwen2.5-3B",  # 模型名字（本地）
        base_url="http://127.0.0.1:8000/v1",  # url本地
        api_key="EMPTY",  # vLLM 不需要真实 key
        temperature=0  # 温度0 = 输出最稳定（对于提取图谱这个应用来说，0是最好的，不要调这个参数）
    )

#--- 初始化知识图谱 ---#
def init(raw_texts: list): # 初始化整个 GraphRAG 系统

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
    embeddings = get_embedding_temp()

    # Step 3：设置知识图谱的 schema（允许哪些节点和属性）
    # 1. 定义 NodeSchema
    node_schemas = [
        NodeSchema("职业类别"),  # 为每个节点类型指定属性
        NodeSchema("岗位ID", ["location","diploma"]),  # 例如，为岗位ID添加薪资范围属性
        NodeSchema("公司", ["industry"]),
        NodeSchema("专业", ["major"]),
        NodeSchema("综合素质能力", ["description"]),
        NodeSchema("技术技能", ["description"]),
        NodeSchema("证书")
    ]
    relationship_schemas = [
        RelationshipSchema("职业类别", "需要掌握", "技术技能"),
        RelationshipSchema("职业类别", "需要具有", "综合素质能力"),
        RelationshipSchema("职业类别", "需要持有", "证书"),
        RelationshipSchema("岗位ID", "属于", "职业类别"),
        RelationshipSchema("岗位ID", "需要掌握", "技术技能"),
        RelationshipSchema("岗位ID", "需要具有", "综合素质能力"),
        RelationshipSchema("岗位ID", "需要持有", "证书"),
        RelationshipSchema("岗位ID", "来自于", "公司"),
        RelationshipSchema("岗位ID", "需要毕业于", "毕业专业")
    ]

    # Step 4：创建 LLMGraphTransformer（把文本变成图结构）
    graph_transformer = LLMGraphTransformer(
        llm=RAG_llm,
        allowed_nodes=node_schemas,  # 使用 NodeSchema 列表
        allowed_relationships=relationship_schemas,  # 使用 RelationshipSchema 列表
        strict_mode=True,  # 保持严格模式
    )
    # Step 5：调用算法，把文本转成知识图谱的点和边
    graph_documents = graph_transformer.convert_to_graph_documents(split_docs)
    print(f"提取出 {len(graph_documents)} 个 GraphDocument")

    # Step 6：连接 Neo4j 数据库
    graph = Neo4jGraph(
        url=graph_url,
        username=graph_username,
        password=graph_password,
        database=database_name,
        refresh_schema=True
    )

    # Step 7：把图数据写入 Neo4j
    graph.query("MATCH (n) DETACH DELETE n") # 先清空数据库中原有信息
    graph.add_graph_documents(
        graph_documents,
        baseEntityLabel=True,  # 给所有实体节点加 __Entity__ 标签
        include_source=True  # 把原始文本也存成 Document 节点，建立 MENTIONS 关系
    )
    print("GraphRAG 初始化完成！")

    # Step 8：获取Neo4j图上所有的节点
    entities_query = """
        MATCH (n:__Entity__)
        RETURN 
            elementId(n) AS internal_id, 
            n.id AS name,
            labels(n) AS labels
        """ # 一次性把所有实体节点的信息查出来，包括类型
    entity_records = graph.query(entities_query) # 执行查询

    entity_list = [] # 存放处理后的实体信息
    for r in entity_records:
        if not r.get("name"):
            continue # labels 通常是列表，如 ['__Entity__', '岗位编码']
        node_labels = r["labels"]
        entity_type = node_labels[-1] if len(node_labels) > 1 else "__Entity__"  # 取最后一个具体类型

        entity_list.append({
            "internal_id": r["internal_id"],
            "name": r["name"],
            "type": entity_type  # 记录实体类型
        }) # 把当前实体的三个关键信息打包成一个字典，追加到 entity_list 中

    names = [e["name"] for e in entity_list] # 类型 list[str]，只提取所有实体的名称，用于批量向量化
    vectors = embeddings.embed_documents(names) # 类型 list[list[float]]，每个实体名称对应的 Embedding 向量

    embedding_threshold = 0.8 # embedding阈值
    fuzzy_threshold = 80 # 字符相似阈值
    NO_MERGE_TYPES = {
        '岗位id'
    } # 不判重的节点类型

    groups = defaultdict(list) # group 存放去重后的分组
    visited = set() # visit 记录一个节点是否已经被分组
    for i in range(len(entity_list)):  # 遍历每个节点
        if i in visited:
            continue

        current_type = entity_list[i]["type"] # 得到当前的节点的类型
        groups[i].append(i) # 将节点i当作一个新族群的第一个节点
        visited.add(i) # 记录该节点（好像用不到）

        for j in range(i + 1, len(entity_list)): # 遍历 i 之后的每个节点
            if j in visited: # 如果该节点已经属于某个组，就跳过
                continue
            if current_type in NO_MERGE_TYPES or entity_list[j]["type"] in NO_MERGE_TYPES: # 如果是“不允许合并”的类型，直接跳过
                continue
            if not(current_type == entity_list[j]["type"]): # 如果两个节点类型不同，就跳过
                continue

            is_similar_to_group = False # 检查 j 是否与当前组中【任意一个】成员相似
            for member_idx in groups[i]:  # 遍历当前组已有的所有成员
                vec_member = np.array(vectors[member_idx]) # 计算与该成员的相似度
                vec_j = np.array(vectors[j])
                cos_sim = np.dot(vec_member, vec_j) / (np.linalg.norm(vec_member) * np.linalg.norm(vec_j) + 1e-8) # 余弦相似度
                fuzzy_score = fuzz.ratio( entity_list[member_idx]["name"], entity_list[j]["name"]) # 混合相似度
                if cos_sim >= embedding_threshold or fuzzy_score >= fuzzy_threshold:
                    is_similar_to_group = True
                    break  # 只要找到一个相似，就不再继续检查

            if is_similar_to_group: # 如果经鉴定后成立
                groups[i].append(j) # 添加到族群
                visited.add(j) # 记录已访问

    merged_count = 0
    for canonical_idx, dup_indices in groups.items(): # 遍历每个族群，将其写入 Neo4j
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




