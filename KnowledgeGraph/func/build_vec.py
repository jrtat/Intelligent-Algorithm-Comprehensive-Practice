from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j,graph_url,graph_username,graph_password,database_name
from KnowledgeGraph.func.utils.get_models import get_embedding_temp

from langchain_text_splitters import RecursiveCharacterTextSplitter
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
    chunk_size = 200  # 分块大小
    chunk_overlap = 40  # 重叠大小
    batch_size = 20  # 批次大小
    skip = 0 # 分页变量
    total_docs = 0 # 处理的总 docs 数
    total_chunks = 0 # 处理的总 chunk 数
    global chunk_vs

    # Step 1：初始化 Embedding 模型 和 分块器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False, # separators 中的字符串将被当作普通字符序列进行精确匹配
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
    ) # LangChain 提供的一种递归切分器，它会按 separators 列表中优先级从高到低的顺序尝试切分。

    # Step 2：与图数据库建立连接
    graph = connect_neo4j()

    # Step 3：读取 Document 并分块
    while True:
        records = graph.query(
            """
            MATCH (doc:Document)
            RETURN id(doc) AS doc_id, doc.text AS value
            SKIP $skip LIMIT $limit
            """,
            params={"skip": skip, "limit": batch_size}
        )
        # Cypher 查询：匹配所有标签为 Document 的节点，返回其内部 ID（id(doc)）和 text 属性。
        # SKIP $skip LIMIT $limit：分页机制，$skip 和 $limit 是参数化查询的占位符。
        # params：用字典将 Python 变量传入查询

        if not records: # 如果这一批查询返回空列表，说明所有文档都已处理完，退出循环
            break

        for record in records: # 遍历本批次返回的每条记录（一个文档节点）
            doc_id = record["doc_id"] # 从字典中取出文档的文本内容。
            value = record["value"] # 从字典中取出文档的内部 ID。

            if not isinstance(value, str) or not value.strip(): # 若 value 不是字符串，或字符串去除空格后为空，则跳过该文档
                continue

            chunk_texts = splitter.split_text(value) # 分块
            chunk_data = [
                {
                    "text": text,
                    "index": idx
                }
                for idx, text in enumerate(chunk_texts)
            ] # 构造要写入的数据
            # 用列表推导式构造一个字典列表 chunk_data：
            # zip(chunk_texts, chunk_embeddings)：将文本块和其向量一一配对。
            # enumerate：生成索引 idx，代表该块在原文档中的顺序（从 0 开始）。
            # 每个字典包含三个键：
            #   1. text（文本）
            #   2. embedding（向量）
            #   3. index（序号）。
            # 这个结构将用于接下来的 Cypher 查询中的 UNWIND 操作。

            graph.query(
                """
                MATCH (doc:Document) WHERE id(doc) = $doc_id

                UNWIND $chunk_data AS chunkData
                CREATE (c:Chunk {
                    text: chunkData.text,
                    chunk_index: chunkData.index
                })
                CREATE (c)-[:FROM_DOCUMENT]->(doc)

                WITH doc, collect(c) AS createdChunks

                // 创建 NEXT_CHUNK 链
                UNWIND range(0, size(createdChunks)-2) AS i
                WITH createdChunks[i] AS c1, createdChunks[i+1] AS c2
                CREATE (c1)-[:NEXT_CHUNK]->(c2)
                """,
                params={
                    "doc_id": doc_id,
                    "chunk_data": chunk_data
                }
            )
            # MATCH (doc:Document) WHERE id(doc) = $doc_id 找到之前读取的那个文档节点。
            # UNWIND $chunk_data AS chunkData chunk_data 列表“展开”，每一行迭代作为一个 chunkData 变量。
            # CREATE (c:Chunk { ... }) 为每个 chunkData 创建一个新的 Chunk 节点，并将字典中的 text、embedding、chunk_index 作为属性存入。
            # CREATE (c)-[:FROM_DOCUMENT]->(doc) 同时创建从 Chunk 指向 Document 的关系 FROM_DOCUMENT，表明该块来源于该文档。
            # WITH doc, collect(c) AS createdChunks 将前面创建的所有 Chunk 节点收集到一个列表 createdChunks 中，同时保留 doc。
            # UNWIND range(0, size(createdChunks)-2) AS i 生成一个从 0 到（块数量 - 2）的整数序列。例如，如果有 3 个块，则生成 [0, 1]。
            # WITH createdChunks[i] AS c1, createdChunks[i+1] AS c2 取出相邻的两个块：c1 是第 i 个，c2 是第 i+1 个。
            # CREATE (c1)-[:NEXT_CHUNK]->(c2) 在这两个块之间创建一个 NEXT_CHUNK 关系，形成一条链表结构。这在后续需要按顺序拼接上下文时很有用。
            total_docs += 1 # 计数
            total_chunks += len(chunk_data) # 计数
            print(f"已处理 Document {doc_id} → 生成 {len(chunk_data)} 个 Chunk")
        skip += batch_size # 分页变量

    print(f"\n 完成！共处理 {total_docs} 个 Document，生成 {total_chunks} 个 Chunk 节点。")

    chunk_vs = create_specialized_vectorstore(
        index_name="chunk_index",
        node_label="Chunk",
        text_node_properties=["text"],
        embedding_node_property="chunk_embedding"
    )  # 综合素质向量索引

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
