import os
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_core.retrievers import BaseRetriever
from langchain_huggingface import HuggingFaceEmbeddings# 本地 Embedding 模型
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 分块
from collections import defaultdict
from rapidfuzz import fuzz
import numpy as np
from typing import List, Any

# --- 全局变量 ---#
database_name = "1f5dcc17"
graph_url = "neo4j+s://1f5dcc17.databases.neo4j.io"
graph_username = "1f5dcc17"
graph_password = "J1-Sv2VA6q5Qw3rH5vFQSmYCwMtuCpF8kqt-W0UrEDU"

class HybridGraphRetriever(BaseRetriever):
    vector_index: Any = None  # 对象
    k_vector: int = 6
    k_graph: int = 8

    def __init__(self, vector_index, k_vector: int = 6, k_graph: int = 8):
        super().__init__() # 先调用父类 __init__

        self.vector_index = vector_index # 负责做向量搜索和关键词搜索的 Neo4jVector 对象
        self.k_vector = k_vector # 向量检索里最多返回多少条结果
        self.k_graph = k_graph # 图结构检索（graph_retriever 函数）里最多返回多少条关系路径结果

    def _get_relevant_documents(self, query: str) -> List[Document]: # LangChain会“自动”调用该方法 （query 为llm的提示词）

        vector_docs = self.vector_index.similarity_search(query, k=self.k_vector)  # 调用 Neo4jVector 提供的向量搜索功能：找意思相近的文本
        graph_docs = graph_retriever(query, k=self.k_graph)  # 调用graph_retriever函数：找实体间的关系路径

        combined = vector_docs + graph_docs # 简单合并

        seen = set()
        unique_docs = []
        for doc in combined: # 去重（避免同样的内容出现两次）
            key = doc.page_content[:300]  # 用前300个字符判断是否重复
            if key not in seen:
                seen.add(key)
                unique_docs.append(doc)
        return unique_docs[:14]  # 设定最多给 LLM 多少条上下文，防止超 token

def graph_retriever(query: str, k: int = 10) -> List[Document]:
    # 这个函数会：
    # 1. 先让LLM从问题里提取关键实体
    # 2. 用Cypher在Neo4j图谱里找这些实体以及它们周围1~2跳的关系

    # Step 0：与数据库建立连接 & 初始化 LLM
    graph = Neo4jGraph(
        url=graph_url,
        username=graph_username,
        password=graph_password,
        database=database_name,
        refresh_schema=True
    )
    RAG_llm = get_llm_temp()

    # Step 1：让 LLM 提取实体 （重要实体的规定可以进一步精细化）
    entity_prompt = f"""
    从以下查询中提取所有重要实体（人名、组织、地点、技术、职位、技能等），用英文逗号分隔。
    只返回实体列表，不要解释或其他文字。
    查询：{query}
    """
    entities_text = RAG_llm.invoke(entity_prompt).content.strip() # 调用大模型获取回复
    entities = [e.strip() for e in entities_text.split(",") if e.strip()] # 将其转成列表
    if not entities:
        entities = [query]

    # Step 2： Cypher 查询
    cypher_query = """
    MATCH (n:__Entity__)
    WHERE ANY(entity IN $entities WHERE toLower(n.id) CONTAINS toLower(entity))
    OPTIONAL MATCH path = (n)-[r*1..2]-(m:__Entity__)
    WITH n, m, 
         [rel IN relationships(path) | type(rel)] AS rel_types,
         path
    RETURN
        n.id AS source,
        rel_types AS relations,
        m.id AS target,
        '路径: ' + n.id + ' → ' + 
        reduce(s = '', rel IN relationships(path) | s + type(rel) + ' → ') + m.id AS path_text
    LIMIT $limit
    """
    results = graph.query(cypher_query, {"entities": entities, "limit": k})
    # 查找所有标签为__Entity__的节点n，从每个符合条件的节点n出发，沿任意类型的关系向外扩展1到2步，到达另一个标签为__Entity__的节点m
    # 由于是OPTIONAL MATCH，即使没有找到路径，n仍会保留
    # 提取路径中所有关系的关系类型，存入rel_types列表，保留完整路径path供后续使用
    # 最终每行返回四个字段：
        # source：起始节点n的id属性
        # relations：路径中所有关系类型的列表（按路径顺序）
        # target：目标节点m的id属性（若无可达节点则为null）
        # path_text：格式化后的路径描述，例如'路径: A → 关系类型1 → 关系类型2 → B'，其中A和B为节点ID，关系类型依次列出

    # Step 3：处理查询结果并返回
    docs = [] # 存放最终要返回的 Document 对象
    for record in results: # 循环处理每一条 Neo4j 返回的结果：
        relations_str = ", ".join(record.get('relations', [])) if record.get('relations') else ""
        text = f"{record.get('source', '')} {relations_str} {record.get('target', '')}。" \
               f"{record.get('path_text', '')}"
        docs.append(Document(
            page_content=text,
            metadata={"source": "graph", "type": "structured"}
        ))
        # 提取 relations 字段（关系类型列表），用逗号拼接成 relations_str
        # 将 source、relations_str、target 以及 path_text 拼接成一段可读的文本
        # 创建 （LangChain 的） Document 对象，其中 page_content 为拼接的文本，metadata 记录来源类型（图数据）
        # 最终所有 Document 对象存储在 docs 列表中，可用于后续的向量化存储、检索或问答等任务

    return docs

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
    documents = [Document(page_content=text) for text in raw_texts]
    split_docs = text_splitter.split_documents(documents)

    # Step 2：初始化 LLM 和 Embedding 模型
    RAG_llm = get_llm_temp()
    embeddings = get_embedding_temp()

    # Step 3：设置知识图谱的 schema（允许哪些节点和属性）
    allowed_nodes = ['岗位名称','岗位ID',
                     '公司','城市','行业',
                     '毕业专业','学历',
                     '软技能','工作技能','工作内容',
                     '证书','论文']
    node_properties = []
    allowed_relationships = []
    relationship_properties = []

    # Step 4：创建 LLMGraphTransformer（把文本变成图结构）
    graph_transformer = LLMGraphTransformer(
        llm=RAG_llm,
        allowed_nodes=allowed_nodes,
        allowed_relationships=allowed_relationships,
        node_properties=node_properties,
        relationship_properties=relationship_properties,
        strict_mode=False  # 在最终使用时设置为 True 只保留符合 schema 的结果，防止乱提取
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

    embedding_threshold = 0.92 # embedding阈值
    fuzzy_threshold = 85 # 字符相似阈值
    NO_MERGE_TYPES = {
        '岗位ID'
    } # 不判重的节点类型

    groups = defaultdict(list) # group 存放去重后的分组
    visited = set() # visit 记录一个节点是否已经被分组
    for i in range(len(entity_list)):  # 遍历每个节点
        if i in visited:
            continue

        current_type = entity_list[i]["type"] # 得到当前的节点的类型
        groups[i].append(i) # 将节点i当作一个新族群的第一个节点
        visited.add(i) # 记录该节点（好像用不到）

        for j in range(i + 1, len(entity_list)): # 遍历节点 i 之后的每个节点
            if j in visited: # 如果节点 j 已经属于某个族群了，就跳过
                continue

            if current_type in NO_MERGE_TYPES or entity_list[j]["type"] in NO_MERGE_TYPES: # 如果是“不需要合并”的类型，直接跳过，不进行相似度计算
                continue

            vec_i = np.array(vectors[i])
            vec_j = np.array(vectors[j])
            cos_sim = np.dot(vec_i, vec_j) / (np.linalg.norm(vec_i) * np.linalg.norm(vec_j) + 1e-8) # 余弦相似度
            fuzzy_score = fuzz.ratio(entity_list[i]["name"], entity_list[j]["name"]) # 字符模糊相似度

            if cos_sim >= embedding_threshold or fuzzy_score >= fuzzy_threshold:
                groups[i].append(j)
                visited.add(j)

    # ====================== 执行合并 ======================
    merged_count = 0
    for canonical_idx, dup_indices in groups.items():
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

def get_retriever():

    # Step 0：声明全局变量
    global graph_url, graph_username, graph_password, database_name

    # Step 1：初始化Embedding模型
    embeddings = get_embedding_temp()

    # Step 2：创建向量索引（这个索引是在Neo4j数据库上的）
    vector_index = Neo4jVector.from_existing_graph(
        embedding=embeddings,
        url=graph_url,
        username=graph_username,
        password=graph_password,
        database=database_name,
        search_type="hybrid",  # 向量相似度 + 关键词 BM25
        node_label="Document",  # 原始文本所在的节点标签
        text_node_properties=["text"],  # 用哪个属性做 embedding（LLMGraphTransformer 默认用 text）
        embedding_node_property="embedding",  # 向量存到这个属性里
        index_name="vector_index",
        keyword_index_name="keyword_index"
    )

    # Step 3：创建并返回混合检索器
    hybrid_retriever = HybridGraphRetriever(vector_index=vector_index)
    print("hybrid_retriever 构建完成！")
    return hybrid_retriever


