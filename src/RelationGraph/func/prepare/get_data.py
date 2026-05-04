from src.RelationGraph.func.utils.conn_neo4j import connect_neo4j

import pandas as pd

def get_data_graph():
    # "职业类别", "公司" 为 str
    # "晋升路径", "学历要求", "综合素质", "职业技能", "证书", "工作内容", "专业", "工作经验", "行业" 为列表

    def ensure_list(value):

        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    # Step 1：与图建立连接
    graph = connect_neo4j()

    # Step 2：通过执行图查询获取特征
    query = """
    MATCH (p:岗位)
    OPTIONAL MATCH (p)-[:属于]->(cat:职业类别)
    OPTIONAL MATCH (p)-[:来自]->(c:公司)
    OPTIONAL MATCH (c)-[:涉及]->(ind:行业) 
    OPTIONAL MATCH (p)-[:需要具有]->(q:综合素质)
    OPTIONAL MATCH (p)-[:需要掌握]->(s:职业技能)
    OPTIONAL MATCH (p)-[:需要持有]->(cert:证书)
    OPTIONAL MATCH (p)-[:负责]->(t:工作内容)
    OPTIONAL MATCH (p)-[:需要来自]->(m:专业)
    OPTIONAL MATCH (p)-[:需要拥有]->(exp:工作经验)
    RETURN 
        p.id AS 岗位id,
        p.薪资范围 AS 薪资范围,
        p.学历要求 AS 学历要求,
        p.晋升路径 AS 晋升路径,
        collect(DISTINCT cat.id) AS 职业类别,
        collect(DISTINCT c.id) AS 公司,
        collect(DISTINCT q.id) AS 综合素质,
        collect(DISTINCT s.id) AS 职业技能,
        collect(DISTINCT cert.id) AS 证书,
        collect(DISTINCT t.id) AS 工作内容,
        collect(DISTINCT m.id) AS 专业,
        collect(DISTINCT exp.id) AS 工作经验,
        [(p)-[:来自]->(c)-[:涉及]->(ind:行业) | ind.id][0] AS 行业
    """
    # 解释：使用列表推导式收集所有关联公司的行业属性，再取第一个元素（下标0，因为公司只有一个所以是可行的）。

    results = graph.query(query)  # 执行查询
    df = pd.DataFrame(results) # 将查询结果转换为 DataFrame

    # Step 3：处理“职业类别”和“公司”列：取第一个元素（若非空列表）
    for col in ["职业类别", "公司", "薪资范围"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
        else:
            df[col] = None

    # Step 4：处理多值列：转换为列表格式
    multi_value_cols = ["晋升路径", "学历要求", "综合素质", "职业技能", "证书", "工作内容", "专业", "工作经验", "行业"]

    for col in multi_value_cols:
        if col in df.columns:
            df[col] = df[col].apply(ensure_list)
        else:
            df[col] = [[] for _ in range(len(df))]

    return df

def get_data_raw():
    # 不作任何多余处理， 只将 “岗位名称” 改名为 “职业类别”
    file_path = "processed.xlsx"
    df = pd.read_excel(file_path, header=0)
    df.rename(columns={'岗位名称': '职业类别'}, inplace=True)
    return df
