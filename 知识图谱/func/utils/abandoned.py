#--- From build_graphrag#

def joy_division():
    """

    .. warning::
    **【已弃用】** 功能被transform_properties_to_node替代了

    “工作内容”、“证书”、“综合素质”、“职业技能”、“福利待遇”、“专业”、“行业”这七类节点中，
    如果节点值是一个列表，则拆分成多个独立节点（如果是字符串，则根据常见分隔符拆分），并保留与岗位/公司的关系，最后删除原列表节点。

    .. warning::
    **【注意】** 这段代码必须在构建索引向量之前执行，否则会导致索引失效。

    :return: 无返回值
    """

    # Step 0：声明全局变量
    global target_job_configs, target_company_configs

    # Step 1：建立数据库连接
    graph = connect_neo4j()

    # Step 2： 拆分岗位相关的节点
    for label, rel_type in target_job_configs.items():
        query = f"""
            MATCH (post:岗位)-[r:{rel_type}]->(n:{label})
            RETURN 
                id(post) AS post_id,
                id(n) AS node_id,
                properties(n) AS all_properties,
                collect(id(post)) AS all_post_ids
            """ # 查询：获取节点及其所有属性（支持多岗位关联）
        results = graph.query(query) # 存储查询的结果
        split_count = 0 # 计数

        for record in results:
            all_props = record.get("all_properties", {})
            node_id = record["node_id"]
            all_post_ids = record.get("all_post_ids", [])

            list_value = None
            list_key = None

            for key, value in all_props.items(): # 遍历节点的所有属性值
                if isinstance(value, list) and len(value) > 0: # 判断该属性值是否是列表
                    list_value = value
                    list_key = key
                    break # 如果是，记录该属性键（属性名）值（属性值）对，并立刻停止
            # 由于 target_configs 中的四种节点除了自身值外没有其他属性，因此这个循环实际只会执行一轮

            if list_value is None: # 这个不太可能被触发
                continue

            for item in list_value: # 遍历列表中的每个元素
                item_str = str(item).strip() # 转换为字符串并去除首尾空格
                if not item_str: # 如果是空串则跳过
                    continue

                for post_id in all_post_ids: # 遍历所有连接到原节点的岗位 ID
                    ''' 测试时可用这套代码(不添加 __Entity__ 标签看起来比较显眼)
                    create_query = f"""
                        MATCH (post:岗位) WHERE id(post) = $post_id
                        CREATE (new:{label} {{ {list_key}: $item }})
                        CREATE (post)-[:{rel_type}]->(new)
                        """ # 创建一个新节点，标签与原节点相同，并设置一个属性，属性名就是原列表的属性名，属性值为当前列表项的字符串，并与岗位建立关系
                    '''

                    create_query = f"""
                        MATCH (post:岗位) WHERE id(post) = $post_id
                        CREATE (new:{label} {{ {list_key}: $item, Entity: $item }})
                        CREATE (post)-[:{rel_type}]->(new)
                    """ # 创建一个新节点，标签与原节点相同，并设置一个属性，属性名就是原列表的属性名，属性值为当前列表项的字符串，并与岗位建立关系

                    graph.query(create_query, {"post_id": post_id, "item": item_str})  # 执行查询语句

            delete_query = "MATCH (n) WHERE id(n) = $node_id DETACH DELETE n"
            graph.query(delete_query, {"node_id": node_id}) # 删除原节点
            split_count += 1 # 计数

        print(f"已处理 {label} 节点：共拆分 {split_count} 个列表节点")

    # Step 3：拆分公司相关的节点
    for label, rel_type in target_company_configs.items():
        query = f"""
            MATCH (company:公司)-[r:{rel_type}]->(n:{label})
            RETURN 
                id(company) AS company_id,
                id(n) AS node_id,
                properties(n) AS all_properties,
                collect(id(company)) AS all_company_ids
            """  # 查询：获取节点及其所有属性，并收集关联的公司ID
        results = graph.query(query) # 存储查询的结果
        split_count = 0 # 计数

        for record in results:
            all_props = record.get("all_properties", {})
            node_id = record["node_id"]
            all_company_ids = record.get("all_company_ids", [])

            list_value = None
            list_key = None

            for key, value in all_props.items():
                if isinstance(value, list) and len(value) > 0:
                    list_value = value
                    list_key = key
                    break

            if list_value is None: # 这个不太可能被触发
                continue

            for item in list_value: # 遍历列表中的每个元素
                item_str = str(item).strip() # 转换为字符串并去除首尾空格
                if not item_str: # 如果是空串则跳过
                    continue

                for company_id in all_company_ids:  # 遍历所有连接到原节点的公司 ID
                    ''' 测试时可用这套代码(不添加 __Entity__ 标签看起来比较显眼)
                    create_query = f"""
                        MATCH (company:公司) WHERE id(company) = $company_id
                        CREATE (new:{label} {{ {list_key}: $item, Entity: $item }})
                        CREATE (company)-[:{rel_type}]->(new)
                        """
                    '''
                    create_query = f"""
                        MATCH (company:公司) WHERE id(company) = $company_id
                        CREATE (new:{label} {{ {list_key}: $item, Entity: $item }})
                        CREATE (company)-[:{rel_type}]->(new)
                        """
                    graph.query(create_query, {"company_id": company_id, "item": item_str})

            delete_query = "MATCH (n) WHERE id(n) = $node_id DETACH DELETE n"
            graph.query(delete_query, {"node_id": node_id})
            split_count += 1

        print(f"已处理 {label} 节点：共拆分 {split_count} 个列表节点")

    print("已成功拆分节点值为列表的节点！")


'''

text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # 分块大小
        chunk_overlap=150,  # 重叠部分大小，帮助保留跨块实体关系
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]  # 中文友好分隔符
    )
split_docs = text_splitter.split_documents(split_docs) # 未必需要分块

'''

#--- Completely Useless ---#

target_job_configs = {
    "工作内容": "负责",
    "证书": "需要持有",
    "综合素质": "需要具有",
    "职业技能": "需要掌握",
    "福利待遇": "提供",
    "专业": "需要来自",
} # 定义要处理的四种节点类型和对应的关系类型

target_company_configs = {
    "行业": "涉及"
}

def use_llm(hybrid_retriever, question: str):
    # Step 0：判断graphRAG是否已经构建完成了（通过判断hybrid_retriever是否存在）
    if hybrid_retriever is None:
        raise ValueError("请先调用 init() 初始化！")

    # Step 1：创建 LLM
    llm = get_llm_temp()

    # Step 2：构建 RAG Chain
    template = """
    你是一个专业、准确的助手。请严格基于以下上下文回答问题。
    如果上下文无法回答，请诚实说明“根据提供的信息无法确定”。

    上下文：
    {context}

    问题：{question}

    请用中文、结构清晰地回答（可分点）：
    """
    prompt = ChatPromptTemplate.from_template(template)
    rag_chain = (
            {"context": hybrid_retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )

    # Step 3：执行查询并得到答案
    answer = rag_chain.invoke(question)

    # Step 4：返回答案
    return answer

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

#--- 图搜索方式登记 ---#
def graph_retriever(graph_search_type):
    if(graph_search_type == 'none'):
        return 'hello world'

def graph_retriever(query: str, k: int = 10) -> List[Document]:
    # 这个函数会：
    # 1. 先让LLM从问题里提取关键实体
    # 2. 用Cypher在Neo4j图谱里找这些实体以及它们周围1~2跳的关系

    # Step 0：与数据库建立连接 & 初始化 LLM
    graph = connect_neo4j()
    llm = get_llm_temp()

    # Step 1：让 LLM 提取实体 （重要实体的规定可以进一步精细化）
    entity_prompt = f"""
    从以下查询中提取所有重要实体（职业类别，技术能力，公司，证书等），用英文逗号分隔。
    只返回实体列表，不要解释或其他文字。
    查询：{query}
    """
    entities_text = llm.invoke(entity_prompt).content.strip() # 调用大模型获取回复
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