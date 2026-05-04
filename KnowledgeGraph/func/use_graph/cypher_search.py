from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j

import os
from typing import List, Optional

class Searcher:
    def __init__(self, graph):
        self.graph = graph

    def get_node_id_by_value_and_label(self, value, node_label, property_key: str = "id"): # 根据属性值和节点标签查找节点的内部 ID。
        

        cypher = f"""
        MATCH (n:{node_label} {{{property_key}: $value}})
        RETURN elementId(n) AS internal_id
        LIMIT 1
        """
        result = self.graph.query(cypher, params={"value": value})
        if result:
            return result[0].get("internal_id")
        return None

    def get_related_node_ids(self, id_val, relation_type, directed = False): # 查找通过指定关系类型与给定节点关联的所有节点的内部 ID。
    
        if directed:
            # 仅从 id_val 节点出发的关系
            cypher = f"""
            MATCH (n)-[:{relation_type}]->(m)
            WHERE elementId(n) = $id_val
            RETURN DISTINCT elementId(m) AS related_id
            """
        else:
            # 双向匹配（包括出向和入向）
            cypher = f"""
            MATCH (n)-[:{relation_type}]-(m)
            WHERE elementId(n) = $id_val
            RETURN DISTINCT elementId(m) AS related_id
            """

        result = self.graph.query(cypher, params={"id_val": id_val})
        return [record["related_id"] for record in result]


    def get_property_by_internal_id(self, internal_id: str, property_key: str): # 根据 Neo4j 内部节点 ID 获取指定属性的值。

        cypher = """
        MATCH (n)
        WHERE elementId(n) = $internal_id
        RETURN n[$property_key] AS prop_value
        """
        result = self.graph.query(cypher, params={
            "internal_id": internal_id,
            "property_key": property_key
        })

        if result and result[0].get("prop_value") is not None:
            return result[0]["prop_value"]
        return None

    def get_all_node_ids_by_label(self, node_label: str): # 获取指定类型的所有节点的内部 ID 列表。
        
        cypher = f"""
        MATCH (n:{node_label})
        RETURN elementId(n) AS internal_id
        """
        result = self.graph.query(cypher)
        return [record["internal_id"] for record in result]
