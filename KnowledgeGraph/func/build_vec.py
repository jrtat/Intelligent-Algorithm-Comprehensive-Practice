from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j,graph_url,graph_username,graph_password,database_name
from KnowledgeGraph.func.utils.get_models import get_embedding_temp, get_local_embedding

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_neo4j import Neo4jVector

personal_quality_vs = None
skill_vs = None
certificate_vs = None
work_content_vs = None
category_vs = None
work_experience_vs = None

company_vs = None
company_industry_vs = None
job_location_vs = None
job_major_vs = None

chunk_vs = None

#--- 统一使用该函数创建向量索引 ---#
def create_specialized_vectorstore(
    index_name: str,
    node_label: str,
    text_node_properties: list[str],
    embedding_node_property: str,
    retrieval_query: str = None
) -> Neo4jVector:
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
        url=graph_url, # 图数据库url
        username=graph_username, # 图数据库用户名
        password=graph_password, # 图数据库密码
        database=database_name, # 数据库名
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
        breakpoint_threshold_amount=0.5, # 句间相似度低于多少时截断
    )  # LangChain 提供的语义分块器，根据 embedding 相似度在语义断点处切分

    # Step 2：与图数据库建立连接
    graph = connect_neo4j()

    # Step 3：读取 Document 并分块（改为直接存为 Document 的列表属性）
    while True:
        records = graph.query(
            """
            MATCH (doc:Document)
            RETURN id(doc) AS doc_id, doc.text AS value
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

            # 一次性计算所有 chunk 的 embedding（列表形式）
            chunk_embeddings = embeddings.embed_documents(chunk_texts)

            # 直接把两个列表写入 Document 节点（而不是创建 Chunk 节点）
            graph.query(
                """
                MATCH (doc:Document) WHERE id(doc) = $doc_id
                SET doc.text_chunks = $chunk_texts,
                    doc.chunk_embeddings = $chunk_embeddings
                """,
                params={
                    "doc_id": doc_id,
                    "chunk_texts": chunk_texts,
                    "chunk_embeddings": chunk_embeddings
                }
            )

            total_docs += 1
            total_chunks += len(chunk_texts)
            print(f"已处理 Document {doc_id} → 生成 {len(chunk_texts)} 个 chunk（已存为列表属性）")

        skip += batch_size

    print(f"\n 完成！共处理 {total_docs} 个 Document，每个 Document 已将 chunks 存为 text_chunks / chunk_embeddings 列表属性。")

def build_vec():
    """
    初始化所有的向量索引
    :return: 无返回值
    """
    global personal_quality_vs, skill_vs, certificate_vs, work_content_vs, work_experience_vs, \
        category_vs, company_vs, \
        company_industry_vs, job_location_vs, job_major_vs
    personal_quality_vs = create_specialized_vectorstore(
        index_name="综合素质_vector_index",
        node_label="综合素质",
        text_node_properties=["id"],
        embedding_node_property="综合素质_embedding",
        retrieval_query="""
            RETURN 
                node {.*, embedding: Null} AS text,
                score,
                { 
                    associated_posts: [(n)<-[:需要具有]-(p:岗位) | p.岗位]
                } AS metadata
        """
    )  # 综合素质向量索引
    skill_vs = create_specialized_vectorstore(
        index_name="职业技能_vector_index",
        node_label="职业技能",
        text_node_properties=["id"],
        embedding_node_property="职业技能_embedding",
        retrieval_query="""
            RETURN 
                node {.*, embedding: Null} AS text,
                score,
                { 
                    associated_posts: [(n)<-[:需要掌握]-(p:岗位) | p.岗位]
                } AS metadata
        """
    )  # 职业技能向量索引
    certificate_vs = create_specialized_vectorstore(
        index_name="证书_vector_index",
        node_label="证书",
        text_node_properties=["id"],
        embedding_node_property="证书_embedding",
        retrieval_query="""
            RETURN 
                node {.*, embedding: Null} AS text,
                score,
                { 
                    associated_posts: [(n)<-[:需要持有]-(p:岗位) | p.岗位]
                } AS metadata
        """
    )  # 证书向量索引
    work_content_vs = create_specialized_vectorstore(
        index_name="工作内容_vector_index",
        node_label="工作内容",
        text_node_properties=["id"],
        embedding_node_property="工作内容_embedding",
        retrieval_query="""
            RETURN 
                node {.*, embedding: Null} AS text,
                score,
                { 
                    associated_posts: [(n)<-[:负责]-(p:岗位) | p.岗位]
                } AS metadata
        """
    )  # 工作内容向量索引
    work_experience_vs = create_specialized_vectorstore(
        index_name="工作经验_vector_index",
        node_label="工作经验",
        text_node_properties=["id"],
        embedding_node_property="工作经验_embedding",
        retrieval_query="""
                RETURN 
                    node {.*, embedding: Null} AS text,
                    score,
                    { 
                        associated_posts: [(n)<-[:需要拥有]-(p:岗位) | p.岗位]
                    } AS metadata
            """
    )  # 工作经验向量索引
    category_vs = create_specialized_vectorstore(
        index_name="category_vector_index",
        node_label="职业类别",
        text_node_properties=["id"],
        embedding_node_property="category_embedding",
        retrieval_query="""
            RETURN 
                node {{.*, embedding: Null}} AS text,
                score,
                node AS metadata
        """
    )  # 职业类别自身
    company_vs = create_specialized_vectorstore(
        index_name="company_vector_index",
        node_label="公司",
        text_node_properties=[],
        embedding_node_property="company_embedding",
        retrieval_query="""
            RETURN 
                node {{.*, embedding: Null}} AS text,
                score,
                node AS metadata
        """
    )  # 公司自身
    company_industry_vs = create_specialized_vectorstore(
        index_name="company_industry_vector_index",
        node_label="公司",
        text_node_properties=["所属行业"],
        embedding_node_property="company_industry_embedding",
        retrieval_query="""
            RETURN 
                node {{.*, embedding: Null}} AS text,
                score,
                node AS metadata
        """
    )  # 公司 + “所属行业”专用索引
    job_location_vs = create_specialized_vectorstore(
        index_name="job_location_vector_index",
        node_label="岗位",
        text_node_properties=["工作地点"],
        embedding_node_property="job_location_embedding",
        retrieval_query="""
            RETURN 
                node {{.*, embedding: Null}} AS text,
                score,
                {{岗位编号: node.岗位, 所属公司: node.公司}} AS metadata
        """
    )  # 岗位 + “工作地点”专用索引
    job_major_vs = create_specialized_vectorstore(
        index_name="job_major_vector_index",
        node_label="岗位",
        text_node_properties=["专业要求"],
        embedding_node_property="job_major_embedding",
        retrieval_query="""
            RETURN 
                node {{.*, embedding: Null}} AS text,
                score,
                {{岗位编号: node.岗位, 所属公司: node.公司}} AS metadata
        """
    )  # 岗位 + “专业要求”专用索引
    print("所有向量索引创建完成！")
