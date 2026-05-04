# 不想写TAT，明明不是我该负责的
# 根据问题设计方法
from tqdm import tqdm

from KnowledgeGraph.func.build_vec import get_vector
from KnowledgeGraph.func.use_graph.get_context import ContextGetter

# 节点标签到关系类型的映射
NODE_TO_REL = {
    "职业技能": "需要掌握",
    "综合素质": "需要具有",
    "证书": "需要持有",
    "工作经验": "需要拥有",
    "工作内容": "负责",
    "福利待遇": "提供",
    "专业": "需要来自"
}


class Tester:
    def __init__(self, graph, embeddings):
        self.graph = graph
        self.embeddings = embeddings
        self.getter = ContextGetter(graph, embeddings)

    def get_occupation_list(self, job_ids: list) -> list:
        """
        根据岗位ID列表查询对应的职业类别列表
        :param job_ids: 岗位ID列表
        :return: 职业类别列表
        """
        if not job_ids:
            return []

        records = self.graph.query(
            """
            MATCH (job:岗位)-[:属于]->(jt:职业类别)
            WHERE job.id IN $job_ids
            RETURN DISTINCT jt.id AS 职业类别
            """,
            params={"job_ids": job_ids}
        )

        return [r["职业类别"] for r in records if r.get("职业类别")]

    def get_job(self, text, need=None, is_jt=False, k=1):
        """
        根据 text 查询返回 Top-K 匹配的岗位或职业类别
        :param text: 查询文本
        :param need: 向量索引类型，默认"职业技能"，可选"综合素质","证书","工作内容","工作经验","福利待遇"
        :param is_jt: False=查岗位, True=查职业类别
        :param k: 返回数量
        :return: [{text, score, from, 职业类型列表}, ...]
        """
        vec_type = need if need else "职业技能"
        vector_store = get_vector(vec_type, self.embeddings)

        results = []
        for doc, score in vector_store.similarity_search_with_score(query=text, k=k):
            tmp = doc.metadata.get("关联岗位列表", [])
            job_list = self.get_occupation_list(tmp)  if is_jt else tmp
            results.append({
                "text": doc.page_content,
                "score": round(score, 4),
                "from": job_list,
                
            })
        return results

    def get_similar(self, jt1, jt2, need):
        """
        找出两个职业类别在指定需求方面的共同点
        :param jt1: 职业类别1的名称
        :param jt2: 职业类别2的名称
        :param need: 节点类型，如"职业技能"、"综合素质"等
        :param k: 返回数量
        :return: [{"jt_node": node_val, "similarity": sim, "jt1_chunks": [...], "jt2_chunks": [...]}, ...]
        """
        rel_type = NODE_TO_REL.get(need)
        if not rel_type:
            return []

        # 查询两个职业类别共同关联的节点
        shared_nodes = self.graph.query(
            """
            MATCH (jt1:职业类别)-[:属于]-(job1:岗位)-[r1]->(n)
            MATCH (jt2:职业类别)-[:属于]-(job2:岗位)-[r2]->(n)
            WHERE jt1.id = $jt1 AND jt2.id = $jt2
              AND type(r1) = $rel_type AND type(r2) = $rel_type
            RETURN n.id AS value, elementId(jt1) AS jt1_id, elementId(jt2) AS jt2_id
            """,
            params={"jt1": jt1, "jt2": jt2, "rel_type": rel_type}
        )

        if not shared_nodes:
            return []

        jt1_id = shared_nodes[0]["jt1_id"]
        jt2_id = shared_nodes[0]["jt2_id"]

        result = []
        record = []
        for node in tqdm(shared_nodes):
            node_val = node["value"]
            if not node_val or node_val in record:
                continue
            record.append(node_val)
            # 获取该节点在两个职业类别下的 chunk 列表
            node_records = self.graph.query(
                "MATCH (n) WHERE n.id = $val RETURN elementId(n) AS node_id",
                params={"val": node_val}
            )

            if not node_records:
                continue

            node_id = node_records[0]["node_id"]
            chunks1 = self.getter.get_knowledge_merge_vals(jt1_id, node_id)
            chunks2 = self.getter.get_knowledge_merge_vals(jt2_id, node_id)

            result.append({
                "jt_node": node_val,
                "jt1_chunks": chunks1,
                "jt2_chunks": chunks2
            })
        return result