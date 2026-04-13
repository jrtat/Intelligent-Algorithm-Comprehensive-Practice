import json
from KnowledgeGraph.func.use_graph.cypher_search import Searcher
from KnowledgeGraph.func.use_graph.get_context import ContextGetter
from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j
from processor.utils.LLMInvoker import LLMInvoker

model = LLMInvoker()


# def get_id(str_val: str) -> str:
#     """
#     从字符串中提取 ID。假设输入格式为 "职业类别_123"，则返回 123。
#     """
#     try:
#         return int(str_val.split("_")[-1])
#     except (IndexError, ValueError):
#         raise ValueError(f"无法从字符串 '{str_val}' 中提取 ID。请确保格式正确，例如 '职业类别_123'。")


graph = connect_neo4j()
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

def batch_extract_info_neo4j(job_type_id: int, source_type: str, source_value: str, target: str, prompt: str):
    """
    从 neo4j 获取 Chunk 数据，提取信息后写回职业类别节点属性。

    :param job_type_id: 职业类别节点 ID
    :param source_type: 来源类型，"knowledge"（知识类型）或 "property"（属性类型）
    :param source_value: 具体值
                         - knowledge: 知识类型（综合素质、职业技能、证书、工作内容、专业、工作经验）
                         - property: 属性类型（学历要求、晋升路径）
    :param target: 目标属性名，将作为职业类别节点的新属性
    :param prompt: 提示词
    :return: 处理后的信息
    """


    # Step 1: 获取该职业类别的所有相关 Chunk 并合并
    # merge_val = get_job_type_chunks(job_type_id, source_type, source_value)
    dic = {}
    if source_type == "knowledge":
        ids = searcher.get_related_node_ids(job_type_id, "属于")
        lst_ids = []
        for i in ids:
            lst_ids.extend(searcher.get_related_node_ids(i,KNOWLEDGE_REL_MAP[source_value]))
        for key in lst_ids:
            dic[searcher.get_property_by_internal_id(key, "id")] = getter.get_knowledge_merge_vals(job_type_id, key)

    elif source_type == "property":
        dic[source_value] = getter.get_job_property_merge_vals(job_type_id, source_value)

    else:
        print(f"未找到任何 Chunk，job_type_id={job_type_id}, source_type={source_type}, source_value={source_value}")
        return
    print(dic)
    # # Step 2: 构建 prompt 并调用 LLM
    # p = f'''
    # 你是一个专业的信息提取分析助手。请根据提供的信息，提取【{target}】字段的内容。
    #
    # ### 任务：
    # {prompt}
    #
    # ### 要求：
    # 1. **输出格式**：仅返回一个标准的 JSON 对象，格式为：{{"{target}": （提取的内容）}}
    # 2. **内容真实性**：必须严格基于原文信息，不能篡改、不能编造、不能无中生有
    # 3. **完整性**：确保返回的内容是完整的、有效的、与原文信息一致的、没有遗漏的
    # 4. **简洁性**：不要任何解释、思考过程或其他多余内容
    # 5. **可解析性**：确保返回的 JSON 格式正确，可以被 json.loads() 直接解析
    #
    # ### 提供的信息：
    #
    # {merge_val}
    # '''
    #
    # raw_response = model.call_ollama(p)
    #
    # if not raw_response:
    #     print(f"❌ 职业类别 (id={job_type_id}) 信息解析失败")
    #     return
    #
    # # Step 3: 将结果写入职业类别节点
    # result_value = raw_response.get(target)
    # if result_value is not None:
    #     graph.query(
    #         f"""
    #         MATCH (jt:职业类别)
    #         WHERE id(jt) = $job_type_id
    #         SET jt.{target} = $value
    #         """,
    #         params={"job_type_id": job_type_id, "value": json.dumps(result_value, ensure_ascii=False)}
    #     )
    #     print(f"✅ 职业类别 (id={job_type_id}) → {target} = {result_value}")
    # else:
    #     print(f"⚠️ LLM 返回结果中未找到 {target} 字段")


if __name__ == '__main__':
    # 示例调用
    # batch_extract_info_neo4j(
    #     job_type_id=1,
    #     source_type="property",
    #     source_value="学历要求",
    #     target="学历要求_提取",
    #     prompt="根据以下岗位信息提取学历要求..."
    # )
    graph = connect_neo4j()

    id = searcher.get_node_id_by_value_and_label("前端开发", "职业类别", "id")
    print(id)
    # lst_job = get_related_node_ids(id, "属于")
    # for i in lst_job[:10]:
    #     print(i)
        # print(len(get_related_node_ids(605, KNOWLEDGE_REL_MAP["证书"])))

    # print(get_knowledge_merge_vals(id, "职业技能", get_related_node_ids(id, KNOWLEDGE_REL_MAP["职业技能"][0])))

    # get_job_type_chunks(id, "knowledge", "专业")
    # get_job_type_chunks(id, "property", "学历要求")
    batch_extract_info_neo4j(id, "knowledge", "职业技能", "职业技能概述", "根据岗位信息，请提取技能...")
    batch_extract_info_neo4j(id, "property", "学历要求", "学历要求概述", "根据岗位信息，请提取学历要求...")

