import os
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.retrievers import BaseRetriever
from typing import List, Any

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

#--- 自定义类 实现混合检索 ---#
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

#--- 实现图检索器 ---#
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

#--- 获取混合检索器 ---#
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
        search_type="hybrid", # 设置搜索类型为“混合搜索”，结合语义相似度（向量搜索）和关键词匹配（BM25算法），经重排序和去重后返回最终结果，能显著提升搜索质量
        node_label="Document",  # 指定图数据库中哪些节点需要被索引，索引器将只为Document标签（原始文本所在的节点标签）的节点创建和查询向量
        text_node_properties=["text"],  # 指定节点上的哪个属性包含待Embedding的文本，LangChain会将这些属性的内容拼接后送入Embedding模型（LLMGraphTransformer 默认用 text）
        embedding_node_property="embedding",  # 指定将生成的向量存到节点的哪个属性里
        index_name="vector_index", # 为创建的向量索引指定名称，用于后续检索和管
        keyword_index_name="keyword_index" # 当search_type为"hybrid"时，用于指定底层全文索引（Fulltext Index）的名称，如果没有，LangChain会自动执行Cypher命令创建一个
    )

    # Step 3：创建并返回混合检索器
    hybrid_retriever = HybridGraphRetriever(vector_index=vector_index)
    print("hybrid_retriever 构建完成！")
    return hybrid_retriever