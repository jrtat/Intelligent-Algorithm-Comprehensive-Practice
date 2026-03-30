import os
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_core.retrievers import BaseRetriever
from langchain_huggingface import HuggingFaceEmbeddings # 新增：本地 Embedding 模型（推荐）
from typing import List

# --- 全局变量 ---#
RAG_llm = None # 大语言模型
graph = None # Neo4j 图数据库
hybrid_retriever = None # 最终得到的 hybrid_retriever

class HybridGraphRetriever(BaseRetriever): # 自定义混合检索器：向量检索 + 图结构检索
    # 继承自 LangChain 提供的一个父类 BaseRetriever

    def __init__(self, vector_index, k_vector: int = 6, k_graph: int = 8): # 构造函数
        self.vector_index = vector_index  # 负责做向量搜索和关键词搜索的 Neo4jVector 对象
        self.k_vector = k_vector  # 向量检索里最多返回多少条结果
        self.k_graph = k_graph  # 图结构检索（graph_retriever 函数）里最多返回多少条关系路径结果

    def _get_relevant_documents(self, query: str) -> List[Document]: # 当RAG链需要上下文时，LangChain会“自动”调用这个方法，query 为 用户的问题

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

def init(raw_texts: list): # 初始化整个 GraphRAG 系统

    # Step 0：声明全局变量，以便后续初始化
    global RAG_llm, graph, hybrid_retriever

    # Step 1：把原始文本转成 LangChain Document 对象
    documents = [Document(page_content=text) for text in raw_texts]

    # Step 2：创建 LLM
    RAG_llm = ChatOpenAI(
        model="Qwen/Qwen2.5-3B-Instruct",  # 你在 vLLM 里部署的模型名字
        base_url="http://localhost:8000/v1",  # vLLM 的 OpenAI 兼容接口
        api_key="EMPTY",  # vLLM 不需要真实 key
        temperature=0  # 温度0 = 输出最稳定（提取图谱必须这样）
    )

    # Step 3：创建 Embedding 模型
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",  # 中文效果很好的开源模型
        model_kwargs={'device': 'cpu'},  # 没有 GPU 就用 cpu
        encode_kwargs={'normalize_embeddings': True}
    )

    # Step 4：设置知识图谱的 schema（允许哪些节点和属性）
    allowed_nodes = []
    allowed_relationships = []
    node_properties = []
    relationship_properties = []

    # Step 5：创建 LLMGraphTransformer（把文本变成图结构）
    graph_transformer = LLMGraphTransformer(
        llm=RAG_llm,
        allowed_nodes=allowed_nodes,
        allowed_relationships=allowed_relationships,
        node_properties=node_properties,
        relationship_properties=relationship_properties,
        strict_mode=True  # 只保留符合 schema 的结果，防止乱提取
    )

    # Step 6：把文本转成 GraphDocument
    graph_documents = graph_transformer.convert_to_graph_documents(documents)
    print(f"提取出 {len(graph_documents)} 个 GraphDocument")

    # Step 7：连接 Neo4j 数据库
    graph = Neo4jGraph(
        url="",
        username="",
        password="",
        refresh_schema=True
    )

    # Step 8：把图数据写入 Neo4j
    graph.add_graph_documents(
        graph_documents,
        baseEntityLabel=True,  # 给所有实体节点加 __Entity__ 标签
        include_source=True  # 把原始文本也存成 Document 节点，建立 MENTIONS 关系
    )
    print("知识图谱已成功写入 Neo4j！")

    # Step 9：创建向量索引（支持 hybrid 搜索）
    vector_index = Neo4jVector.from_existing_graph(
        embedding=embeddings,
        url=graph._driver._uri,
        username=graph._username,
        password=graph._password,
        search_type="hybrid",  # 向量相似度 + 关键词 BM25
        node_label="Document",  # 原始文本所在的节点标签
        text_node_properties=["text"],  # 用哪个属性做 embedding（LLMGraphTransformer 默认用 text）
        embedding_node_property="embedding",  # 向量存到这个属性里
        index_name="vector_index",
        keyword_index_name="keyword_index"
    )

    # Step 10：创建并返回混合检索器
    hybrid_retriever = HybridGraphRetriever(vector_index=vector_index)
    print("GraphRAG 初始化完成！")

def graph_retriever(query: str, k: int = 10) -> List[Document]:
    # 这个函数会：
    # 1. 先让LLM从问题里提取关键实体
    # 2. 用Cypher在Neo4j图谱里找这些实体以及它们周围1~2跳的关系

    # Step 0：声明全局变量，以便后续使用
    global RAG_llm, graph

    # Step 1：让 LLM 从问题里挑出关键实体
    entity_prompt = f"""
    从以下查询中提取所有重要实体（人名、组织、地点、技术、职位等），用英文逗号分隔。
    只返回实体列表，不要解释。
    查询：{query}
    """

    # Step 2：从 llm 返回的结果中提取出实体
    entities_text = RAG_llm.invoke(entity_prompt).content.strip() # 把上面构造的 prompt 发送给 llm，让它回答，取出大模型返回的文本内容并删除多余空格
    entities = [e.strip() for e in entities_text.split(",") if e.strip()] # 用 split(",") 把字符串按逗号切开（并去掉空格），得到列表。
    if not entities:
        entities = [query]  # 如果没提取到，就直接用整个问题

    # Step 3：用 Cypher 查询
    cypher_query = """
    MATCH (n:__Entity__)
    WHERE ANY(entity IN $entities WHERE toLower(n.id) CONTAINS toLower(entity))
    OPTIONAL MATCH path = (n)-[r*1..2]-(m:__Entity__)
    WITH n, m, type(r) as rel_type, path
    RETURN
        n.id AS source,
        collect(DISTINCT rel_type) AS relations,
        m.id AS target,
        '路径: ' + n.id + ' - ' + reduce(s = '', rel IN relationships(path) | s + type(rel) + ' -> ') + m.id AS path_text
    LIMIT $limit
    """
    results = graph.query(cypher_query, {"entities": entities, "limit": k}) # 找到实体，并把周围 1~2 步的关系也拿出来

    docs = [] # 存放最终要返回的 Document 对象
    for record in results: # 循环处理每一条 Neo4j 返回的结果：
        text = f"{record['source']} {record.get('relations', [])} {record.get('target', '')}。{record.get('path_text', '')}"
        # 用 f-string 把 source、relations、target、path_text 拼接成一段容易阅读的文本（如果没有 relations，就返回空列表，避免报错）
        docs.append(Document(page_content=text, metadata={"source": "graph", "type": "structured"}))
        # Document(...)：把拼接好的文本包装成 LangChain 的 Document 对象
        # metadata：给这条记录打上标签，告诉后面的人这是来自“graph”（图检索），类型是结构化的
    return docs