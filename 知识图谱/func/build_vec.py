from .utils.conn_neo4j import connect_neo4j,graph_url,graph_username,graph_password,database_name
from .utils.get_models import get_llm,get_llm_temp, get_llm_silicon_flow ,get_embedding_temp,get_embedding
from langchain_community.vectorstores.neo4j_vector import Neo4jVector

personal_quality_vs = None
skill_vs = None
certificate_vs = None
work_content_vs = None
category_vs = None
company_vs = None
company_industry_vs = None
job_location_vs = None
job_major_vs = None

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

#--- 初始化函数 ---#
def build_vec():
    """
    初始化所有的向量索引
    :return: 无返回值
    """
    global personal_quality_vs, skill_vs, certificate_vs, work_content_vs, \
           category_vs, company_vs, \
           company_industry_vs, job_location_vs, job_major_vs

    personal_quality_vs = create_specialized_vectorstore(
        index_name="综合素质_vector_index",
        node_label="综合素质",
        text_node_properties=["name"],
        embedding_node_property="综合素质_embedding",
        retrieval_query="""
            RETURN 
                node {.*, embedding: Null} AS text,
                score,
                { 
                    associated_posts: [(n)<-[:需要具有]-(p:岗位) | p.岗位]
                } AS metadata
        """
    ) # 综合素质向量索引

    personal_quality_vs.similarity_search("这是一句话", 5)

    skill_vs = create_specialized_vectorstore(
        index_name="职业技能_vector_index",
        node_label="职业技能",
        text_node_properties=["name"],
        embedding_node_property="职业技能_embedding",
        retrieval_query="""
            RETURN 
                node {.*, embedding: Null} AS text,
                score,
                { 
                    associated_posts: [(n)<-[:需要掌握]-(p:岗位) | p.岗位]
                } AS metadata
        """
    ) # 职业技能向量索引

    certificate_vs = create_specialized_vectorstore(
        index_name="证书_vector_index",
        node_label="证书",
        text_node_properties=["name"],
        embedding_node_property="证书_embedding",
        retrieval_query="""
            RETURN 
                node {.*, embedding: Null} AS text,
                score,
                { 
                    associated_posts: [(n)<-[:需要持有]-(p:岗位) | p.岗位]
                } AS metadata
        """
    ) # 证书向量索引

    work_content_vs = create_specialized_vectorstore(
        index_name="工作内容_vector_index",
        node_label="工作内容",
        text_node_properties=["name"],
        embedding_node_property="工作内容_embedding",
        retrieval_query="""
            RETURN 
                node {.*, embedding: Null} AS text,
                score,
                { 
                    associated_posts: [(n)<-[:负责]-(p:岗位) | p.岗位]
                } AS metadata
        """
    ) # 工作内容向量索引

    category_vs = create_specialized_vectorstore(
        index_name="category_vector_index",
        node_label="职业类别",
        text_node_properties=["name"],  # 或你实际存放类别名称的属性
        embedding_node_property="category_embedding",
        retrieval_query="""
            RETURN 
                node {{.*, embedding: Null}} AS text,
                score,
                node AS metadata
        """
    ) # 职业类别自身

    company_vs = create_specialized_vectorstore(
        index_name="company_vector_index",
        node_label="公司",
        text_node_properties=["name"],  # 或 "公司描述"
        embedding_node_property="company_embedding",
        retrieval_query="""
            RETURN 
                node {{.*, embedding: Null}} AS text,
                score,
                node AS metadata
        """
    ) # 公司自身

    print("所有向量索引创建完成！")

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
    ) # 公司 + “所属行业”专用索引

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
    ) # 岗位 + “工作地点”专用索引

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
    ) # 岗位 + “专业要求”专用索引


