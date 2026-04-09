from langchain_community.graphs import Neo4jGraph
import pandas as pd
from typing import Any, List

#--- 全局变量 ---#
database_name = "1f5dcc17"
graph_url = "neo4j+s://1f5dcc17.databases.neo4j.io"
graph_username = "1f5dcc17"
graph_password = "J1-Sv2VA6q5Qw3rH5vFQSmYCwMtuCpF8kqt-W0UrEDU"

def ensure_list(value: Any) -> List:
    """
    将任意值转换为列表，None 转为空列表
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

def get_data():
    """
    从Neo4j中获取一个 DataFrame类型变量
    包含以下列： “岗位id”，“职业类别”，“公司”，"薪资范围", "学历要求","晋升路径"，"工作经验"，"综合素质"，"职业技能"，"证书"，"工作内容"，"专业"
    """

    graph = Neo4jGraph(
        url=graph_url,
        username=graph_username,
        password=graph_password,
        database=database_name,
        refresh_schema=True
    )

    query = """
    MATCH (p:岗位)
    OPTIONAL MATCH (p)-[:属于]->(cat:职业类别)
    OPTIONAL MATCH (p)-[:来自]->(c:公司)
    OPTIONAL MATCH (p)-[:需要具有]->(q:综合素质)
    OPTIONAL MATCH (p)-[:需要掌握]->(s:职业技能)
    OPTIONAL MATCH (p)-[:需要持有]->(cert:证书)
    OPTIONAL MATCH (p)-[:负责]->(t:工作内容)
    OPTIONAL MATCH (p)-[:需要来自]->(m:专业)
    RETURN 
        p.id AS 岗位id,
        p.薪资范围 AS 薪资范围,
        p.学历要求 AS 学历要求,
        p.晋升路径 AS 晋升路径,
        p.工作经验 AS 工作经验,
        collect(DISTINCT cat.id) AS 职业类别,
        collect(DISTINCT c.id) AS 公司,
        collect(DISTINCT q.id) AS 综合素质,
        collect(DISTINCT s.id) AS 职业技能,
        collect(DISTINCT cert.id) AS 证书,
        collect(DISTINCT t.id) AS 工作内容,
        collect(DISTINCT m.id) AS 专业
    """ # 一次性获取所有岗位及其相关信息
    # 匹配数据库中所有标签为 岗位 的节点，并将它们绑定到变量 p
    # 对于每个岗位，尝试匹配一条 () 关系指向 () 节点。若没有匹配，cat 将为 null
    # 使用 collect(DISTINCT ().id) 将多个关联节点的 id 属性收集到一个列表中去重
    # 返回结果 results 是一个 列表，其中每个元素是一个字典，对应一行查询结果（一个岗位及其关联数据）。比如以下格式：
    '''
    [{"岗位": "Cc114514", "薪资范围": "15000-25000每月", ..., "综合素质": "["乐观", "团队协作"]", ...},
     {"岗位": "Cctv919810", ...},
    ...
    ]
    '''
    results = graph.query(query)  # 执行查询
    df = pd.DataFrame(results) # 将查询结果转换为 DataFrame

    for col in ["职业类别", "公司"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None) # 如果列表非空取第一个元素
        else:
            df[col] = None # 如果该列不存在，则返回 None

    for col in [ "综合素质", "职业技能", "证书", "工作内容", "专业"]:
        if col in df.columns:
            df[col] = df[col].apply(ensure_list) # 将这些列的值转换为列表
        else:
            df[col] = [[] for _ in range(len(df))] # 如果查询结果中缺少某列（比如没有任何岗位有该属性），则创建空列表列

    return df
