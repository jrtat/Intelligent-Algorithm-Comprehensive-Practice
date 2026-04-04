from utils.get_models import get_llm_temp,get_llm,get_embedding_temp,get_embedding
from utils.conn_neo4j import graph_url, graph_username, graph_password, database_name
from utils.graph_searcher import graph_retriever

from langchain_core.documents import Document
from langchain_community.vectorstores import Neo4jVector
from langchain_core.retrievers import BaseRetriever
from typing import List, Any

#--- 自定义类 实现混合检索 ---#
class HybridGraphRetriever(BaseRetriever):
    vector_index: Any = None
    graph_search_type: Any = None
    k_vector: int = 6
    k_graph: int = 8

    def __init__(self, vector_index, graph_search_type, k_vector: int = 6, k_graph: int = 8):
        super().__init__() # 先调用父类 __init__

        self.vector_index = vector_index # 负责做向量搜索和关键词搜索的 Neo4jVector 对象
        self.k_vector = k_vector # 向量检索里最多返回多少条结果
        self.k_graph = k_graph # 图结构检索（graph_retriever 函数）里最多返回多少条关系路径结果

    def _get_relevant_documents(self, query: str) -> List[Document]: # LangChain会“自动”调用该方法 （query 为llm的提示词）

        vector_docs = self.vector_index.similarity_search(query, k=self.k_vector)  # 调用 Neo4jVector 提供的向量搜索功能：找意思相近的文本
        graph_docs = graph_retriever(self.graph_search_type)  # 调用graph_retriever函数：找实体间的关系路径

        combined = vector_docs + graph_docs # 简单合并

        seen = set()
        unique_docs = []
        for doc in combined: # 去重（避免同样的内容出现两次）
            key = doc.page_content[:300]  # 用前300个字符判断是否重复
            if key not in seen:
                seen.add(key)
                unique_docs.append(doc)
        return unique_docs[:14]  # 设定最多给 LLM 多少条上下文，防止超 token

#--- 获取混合检索器 ---#
def get_retriever(graph_search_type = 'none'):

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
    hybrid_retriever = HybridGraphRetriever(vector_index=vector_index, graph_search_type = graph_search_type)
    print("hybrid_retriever 构建完成！")
    return hybrid_retriever