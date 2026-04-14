from KnowledgeGraph.func.use_graph.cypher_search import Searcher
from KnowledgeGraph.func.use_graph.get_context import ContextGetter
from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j
from KnowledgeGraph.func.utils.get_models import get_embedding_temp
from processor.utils.FileProcessor import FileProcessor

graph = connect_neo4j()
embeddings = get_embedding_temp()
getter = ContextGetter(graph)
searcher = Searcher(graph)

# 需求类型 → 对应的关系类型
KNOWLEDGE_REL_MAP = {
    "综合素质": "需要具有",
    "职业技能": "需要掌握",
    "证书": "需要持有",
    "工作内容": "负责",
    "工作经验": "需要拥有",
    "专业": "需要来自",
}

def get_info(job_type_id, source_type, source_value):
    fp = FileProcessor(f"need_data/{searcher.get_property_by_internal_id(job_type_id, 'id')}_{source_value}.json")
    dic = {}
    if source_type == "knowledge":
        ids = searcher.get_related_node_ids(job_type_id, "属于")
        lst_ids = []
        for i in ids:
            lst_ids.extend(searcher.get_related_node_ids(i, KNOWLEDGE_REL_MAP[source_value]))
        for key in lst_ids:
            dic[searcher.get_property_by_internal_id(key, "id")] = getter.get_knowledge_merge_vals(job_type_id, key)

    elif source_type == "property":
        dic[source_value] = getter.get_job_property_merge_vals(job_type_id, source_value)

    else:
        print(f"未找到任何 Chunk，job_type_id={job_type_id}, source_type={source_type}, source_value={source_value}")
        return
    fp.save(dic)

if __name__ == '__main__':

    ids = searcher.get_all_node_ids_by_label("职业类别")

    for i in ids:
        get_info(i, "knowledge", "综合素质")
        get_info(i, "knowledge", "职业技能")
        get_info(i, "knowledge", "证书")
        get_info(i, "knowledge", "专业")
        get_info(i, "knowledge", "工作经验")

        get_info(i, "property", "晋升路径")
        get_info(i, "property", "学历要求")

    for i in ids:
        get_info(i, "knowledge", "工作内容")
        get_info(i, "knowledge", "福利待遇")





# def get_job_type_chunks(job_type_id: int, source_type: str, source_value: str) -> str:
#     """
#     获取指定职业类别下指定类型的 Chunk，合并为一个 merge_val。
#
#     :param job_type_id: 职业类别节点 ID
#     :param source_type: "knowledge"（知识类型）或 "property"（属性类型）
#     :param source_value: 具体值
#                         - source_type="knowledge" 时：知识类型名称
#                         - source_type="property" 时：属性类型名称
#     :return: 合并后的字符串
#
#
#     """
#     # records = graph.query(
#     #     """
#     #     MATCH (jt:职业类别)-[:属于]-(job:岗位)-[r]->()
#     #     WHERE id(jt) = $job_type_id
#     #       AND type(r) = $rel_type
#     #
#     #     MATCH (doc:Document)-[:MENTIONS]->(job)
#     #     MATCH (chunk:Chunk)-[:FROM_DOCUMENT]->(doc)
#     #
#     #     RETURN chunk.text AS chunk_text
#     #     """,
#     #     params={"job_type_id": job_type_id, "rel_type": rel_type}
#     # )
#
#
#     graph = connect_neo4j()
#
#     if source_type == "knowledge":
#         # 获取该职业类别下该知识类型关联的所有岗位的 Chunk
#         rel_type = KNOWLEDGE_REL_MAP.get(source_value)
#         if not rel_type:
#             raise ValueError(f"不支持的知识类型：{source_value}，可选值：{list(KNOWLEDGE_REL_MAP.keys())}")
#
#         records = graph.query(
#             """
#             MATCH (jt:职业类别)-[:属于]-(job:岗位)-[r]->(knowledge)
#             WHERE id(jt) = $job_type_id
#               AND type(r) = $rel_type
#
#             MATCH (doc:Document)-[:MENTIONS]->(job)
#             RETURN id(doc) as doc_id, knowledge.id as knowledge_words
#             """,
#             params={"job_type_id": job_type_id, "rel_type": rel_type}
#         )
#
#         docs = {}
#
#         for r in records:
#             docs[r["doc_id"]] = r["knowledge_words"]
#         print(docs)
#
#     elif source_type == "property":
#         # 获取该职业类别下所有岗位的该属性关联的 Chunk
#         records = graph.query(
#             """
#             MATCH (jt:职业类别)-[:属于]-(job:岗位)
#             WHERE id(jt) = $job_type_id
#
#             MATCH (doc:Document)-[:MENTIONS]->(job)
#             MATCH (chunk:Chunk)-[:FROM_DOCUMENT]->(doc)
#
#             RETURN chunk.text AS chunk_text
#             """,
#             params={"job_type_id": job_type_id}
#         )
#
#         chunks = [r["chunk_text"] for r in records if r.get("chunk_text")]
#         merge_val = " ".join(chunks)
#
#         print(f"job_type_id={job_type_id}, property={source_value} → 找到 {len(chunks)} 个 Chunk")
#         return merge_val
#
#     else:
#         raise ValueError(f"不支持的 source_type：{source_type}，可选值：knowledge, property")
#
#     # MATCH (chunk:Chunk)-[:FROM_DOCUMENT]->(doc)
#     #
#     #             RETURN chunk.text AS chunk_text
#