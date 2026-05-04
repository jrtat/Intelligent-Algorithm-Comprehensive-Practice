import os

from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j
from KnowledgeGraph.func.utils.get_models import get_embedding_temp, get_local_embedding

from langchain_experimental.text_splitter import SemanticChunker
from langchain_neo4j import Neo4jVector

personal_quality_vs = None
skill_vs = None
certificate_vs = None
work_content_vs = None
category_vs = None
work_experience_vs = None
welfare_vs = None

company_vs = None
company_industry_vs = None
job_location_vs = None
job_major_vs = None

chunk_vs = None



#--- 统一使用该函数创建向量索引 ---#
def create_specialized_vectorstore(index_name, node_label, text_node_properties,
    embedding_node_property, retrieval_query = None ):
    """
    :param index_name: 给索引命名
    :param node_label: 指定该索引加在哪个类型的节点上
    :param text_node_properties: 指定该索引涉及哪些属性
    :param embedding_node_property: 在 Neo4j 节点上存储向量嵌入（embedding）的具体属性名称
    :param retrieval_query: 这个比较复杂
    :return: Neo4jVector类型的实例
    """
    embeddings = get_embedding_temp()
    vectorstore = Neo4jVector.from_existing_graph(
        embedding=embeddings, # embedding 模型
        url=os.getenv('GRAPH_URL'), # 图数据库url
        username=os.getenv('GRAPH_USERNAME'), # 图数据库用户名
        password=os.getenv('GRAPH_PASSWORD'), # 图数据库密码
        database=os.getenv('DATABASE_NAME'), # 数据库名
        index_name=index_name,
        node_label=node_label,
        text_node_properties=text_node_properties,
        embedding_node_property=embedding_node_property,
        retrieval_query=retrieval_query
    )
    print(f" 已为节点类型“{node_label}” 创建向量索引（{index_name} ）")
    return vectorstore

def build_chunk():
    
    # Step 0：声明参数 与 全局变量
    batch_size = 20  # 批次大小
    skip = 0 # 分页变量
    total_docs = 0 # 处理的总 docs 数
    total_chunks = 0 # 处理的总 chunk 数
    global chunk_vs  # 保留声明，但后面不再使用（已废弃向量索引）

    # Step 1：初始化 Embedding 模型 和 分块器
    embeddings = get_local_embedding() # 使用与 ContextGetter 中一致的 embedding 函数
    splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile", # 使用百分位数方式决定哪里“断句”（最常用、最稳定）
        breakpoint_threshold_amount=0.75, # 句间相似度低于多少时截断
        sentence_split_regex = r'(?<=[。！？.!?；：…\n\r])\s*'
    )  # LangChain 提供的语义分块器，根据 embedding 相似度在语义断点处切分

    # Step 2：与图数据库建立连接
    graph = connect_neo4j()

    # Step 3：读取 Document 并分块（改为直接存为 Document 的列表属性）
    while True:
        records = graph.query(
            """
            MATCH (doc:Document)
            RETURN elementId(doc) AS doc_id, doc.text AS value
            SKIP $skip LIMIT $limit
            """,
            params={"skip": skip, "limit": batch_size}
        )

        if not records:
            break

        for record in records:
            doc_id = record["doc_id"]
            value = record["value"]

            if not isinstance(value, str) or not value.strip():
                continue

            # 使用 SemanticChunker 进行语义分块
            chunk_texts = splitter.split_text(value)
            if not chunk_texts:
                continue

            # 直接把 chunk_texts 列表写入 Document 节点（不再存储 chunk_embeddings）
            graph.query(
                """
                MATCH (doc:Document) WHERE elementId(doc) = $doc_id
                SET doc.text_chunks = $chunk_texts
                """,
                params={
                    "doc_id": doc_id,
                    "chunk_texts": chunk_texts
                }
            )

            total_docs += 1
            total_chunks += len(chunk_texts)
            print(f"已处理 Document {doc_id} → 生成 {len(chunk_texts)} 个 chunk（已存为 text_chunks 列表属性）")

        skip += batch_size

    print(f"\n 完成！共处理 {total_docs} 个 Document，每个 Document 已将 chunks 存为 text_chunks 列表属性。")

def build_vec_ver1():
    global personal_quality_vs, skill_vs, certificate_vs, work_content_vs, work_experience_vs, welfare_vs
    personal_quality_vs = create_specialized_vectorstore(
        index_name="综合素质_vector_index",
        node_label="综合素质",
        text_node_properties=["id"],
        embedding_node_property="综合素质_embedding",
        retrieval_query=""
    )  # 综合素质向量索引
    skill_vs = create_specialized_vectorstore(
        index_name="职业技能_vector_index",
        node_label="职业技能",
        text_node_properties=["id"],
        embedding_node_property="职业技能_embedding",
        retrieval_query=""
    )  # 职业技能向量索引
    certificate_vs = create_specialized_vectorstore(
        index_name="证书_vector_index",
        node_label="证书",
        text_node_properties=["id"],
        embedding_node_property="证书_embedding",
        retrieval_query=""
    )  # 证书向量索引
    work_content_vs = create_specialized_vectorstore(
        index_name="工作内容_vector_index",
        node_label="工作内容",
        text_node_properties=["id"],
        embedding_node_property="工作内容_embedding",
        retrieval_query=""
    )  # 工作内容向量索引
    welfare_vs = create_specialized_vectorstore(
        index_name="工作经验_vector_index",
        node_label="工作经验",
        text_node_properties=["id"],
        embedding_node_property="工作经验_embedding",
        retrieval_query=""
    )
    work_experience_vs = create_specialized_vectorstore(
        index_name="福利待遇_vector_index",
        node_label="福利待遇",
        text_node_properties=["id"],
        embedding_node_property="福利待遇_embedding",
        retrieval_query=""
    )  # 福利待遇向量索引

    print("所有向量索引创建完成！")

def get_vector(vec_type, embedding):
   
    return Neo4jVector.from_existing_index(
        embedding=embedding,
        url=os.getenv('GRAPH_URL'), username=os.getenv('GRAPH_USERNAME'), password=os.getenv('GRAPH_PASSWORD'),
        database=os.getenv('DATABASE_NAME'),  # 数据库名
        index_name=f"{vec_type}_vector_index",  # 和创建时一致
        retrieval_query="""
            WITH node, score
            OPTIONAL MATCH (position:岗位)-[]->(node)
            WITH node, score, 
                 collect(DISTINCT position.id) AS 关联岗位列表
            RETURN
                coalesce(node.id, elementId(node)) AS text,
                score,
                node {.*, 关联岗位列表: 关联岗位列表} AS metadata
        """
    )

#--- Useless ---#

def build_vec_ver114514():
    global  category_vs, company_vs, company_industry_vs, job_location_vs, job_major_vs
    category_vs = create_specialized_vectorstore(
        index_name="category_vector_index",
        node_label="职业类别",
        text_node_properties=["id"],
        embedding_node_property="category_embedding",
        retrieval_query=""
    )  # 职业类别自身
    company_vs = create_specialized_vectorstore(
        index_name="company_vector_index",
        node_label="公司",
        text_node_properties=[],
        embedding_node_property="company_embedding",
        retrieval_query=""
    )  # 公司自身
    company_industry_vs = create_specialized_vectorstore(
        index_name="company_industry_vector_index",
        node_label="公司",
        text_node_properties=["所属行业"],
        embedding_node_property="company_industry_embedding",
        retrieval_query=""
    )  # 公司 + “所属行业”专用索引
    job_location_vs = create_specialized_vectorstore(
        index_name="job_location_vector_index",
        node_label="岗位",
        text_node_properties=["工作地点"],
        embedding_node_property="job_location_embedding",
        retrieval_query=""
    )  # 岗位 + “工作地点”专用索引
    job_major_vs = create_specialized_vectorstore(
        index_name="job_major_vector_index",
        node_label="岗位",
        text_node_properties=["专业要求"],
        embedding_node_property="job_major_embedding",
        retrieval_query=""
    )  # 岗位 + “专业要求”专用索引

#--- Example ---#
# build_vec_ver1() # 在原数据库中处理（仅需一次）

# embedding = get_local_embedding()
# vector_store_eg = get_vector("职业技能",embedding)
# for doc, score in vector_store_eg.similarity_search_with_score(query="你的问题", k=5):
#     print("文本:", doc.page_content)
#     # print("职业类型列表:", doc.metadata.get("职业类型列表")) 不用这个了
#     print("关联岗位列表:", doc.metadata.get("关联岗位列表"))
#     print("相似度分数:", round(score, 4))   # 分数越小越相似（通常0~1之间）
#     print("---")
