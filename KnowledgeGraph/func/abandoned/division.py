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
