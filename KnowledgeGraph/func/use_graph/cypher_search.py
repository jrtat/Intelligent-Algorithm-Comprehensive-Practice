from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j

import os
from typing import List, Optional

def get_node_id_by_value_and_label(value, node_label, property_key: str = "id"):
    """
    根据属性值和节点标签查找节点的内部 ID。
    Args:
        value: 要匹配的值
        node_label: 节点类型
        property_key: 用于匹配的属性名，默认为 'id'

    Returns:
        节点的内部 ID (整数) 或 None（若未找到）

    Note:
        返回的是 Neo4j 内部 id(node)。
    """
    graph = connect_neo4j()

    cypher = f"""
    MATCH (n:{node_label} {{{property_key}: $value}})
    RETURN id(n) AS internal_id
    LIMIT 1
    """
    result = graph.query(cypher, params={"value": value})
    if result:
        return result[0].get("internal_id")
    return None

def get_related_node_ids(id_val, relation_type, directed = False):
    """
    查找通过指定关系类型与给定节点关联的所有节点的内部 ID。

    Args:
        id_val: 源节点的内部 ID (由 id(node) 获得)
        relation_type: 关系类型 (例如 'ACTED_IN', 'FRIEND')
        directed: 是否仅考虑出向关系，默认为 False (双向匹配)

    Returns:
        关联节点 ID 的列表（无重复），若无结果返回空列表

    Note:
        内部 ID 通过 id(node) 获取，若数据库版本支持，建议改用 elementId(n)。
    """
    graph = connect_neo4j()
    if directed:
        # 仅从 id_val 节点出发的关系
        cypher = f"""
        MATCH (n)-[:{relation_type}]->(m)
        WHERE id(n) = $id_val
        RETURN DISTINCT id(m) AS related_id
        """
    else:
        # 双向匹配（包括出向和入向）
        cypher = f"""
        MATCH (n)-[:{relation_type}]-(m)
        WHERE id(n) = $id_val
        RETURN DISTINCT id(m) AS related_id
        """

    result = graph.query(cypher, params={"id_val": id_val})
    return [record["related_id"] for record in result]
