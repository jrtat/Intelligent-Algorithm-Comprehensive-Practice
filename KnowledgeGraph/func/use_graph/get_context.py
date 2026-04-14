from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j
from KnowledgeGraph.func.utils.get_models import get_embedding_temp,get_local_embedding

from tqdm import tqdm

class ContextGetter:

    def __init__(self):
        self.graph = connect_neo4j()

    @staticmethod
    def cosine_similarity(vec1, vec2):
        """余弦相似度"""
        if not vec1 or not vec2:
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = (sum(a * a for a in vec1)) ** 0.5
        norm2 = (sum(b * b for b in vec2)) ** 0.5
        return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

    def get_merge_val_for_doc(
        self,
        doc_id: str,
        value_embedding: list,
    ) -> str:
        """
        核心逻辑：对单个 Document 找到最相似的 chunk + 其相邻 chunk 中相似度更高的一个，合并后返回 merge_val
        由于划分 chunk 时已经没有 overlap，合并时直接拼接即可，无需任何 overlap 去重/trim 逻辑
        """
        # Step 1：直接从 Document 节点读取 text_chunks 和 chunk_embeddings 两个列表
        records = self.graph.query(
            """
            MATCH (doc:Document)
            WHERE elementId(doc) = $doc_id
            RETURN 
                doc.text_chunks AS text_chunks,
                doc.chunk_embeddings AS chunk_embeddings
            """,
            params={"doc_id": doc_id}
        )

        if not records:
            return ""

        r = records[0]
        text_chunks = r.get("text_chunks") or []
        chunk_embeddings = r.get("chunk_embeddings") or []

        if not text_chunks or len(text_chunks) == 0:
            return ""

        # Step 2：在 Python 端计算每个 chunk 与 value_embedding 的相似度，找出最相似的一个
        similarities = []
        for i, emb in enumerate(chunk_embeddings):
            if emb:  # 防止空向量
                sim = self.cosine_similarity(value_embedding, emb)
                similarities.append((sim, i, text_chunks[i]))

        if not similarities:
            return text_chunks[0] if text_chunks else ""

        # 取出相似度最高的 chunk
        best_sim, top_idx, top_text = max(similarities, key=lambda x: x[0])

        # Step 3：获取相邻的两个 candidate（prev 和 next），并附上索引用于后续判断顺序
        candidates = []
        # 前一个 chunk
        if top_idx > 0:
            prev_emb = chunk_embeddings[top_idx - 1]
            if prev_emb:
                sim_prev = self.cosine_similarity(value_embedding, prev_emb)
                candidates.append((sim_prev, top_idx - 1, text_chunks[top_idx - 1]))
        # 后一个 chunk
        if top_idx < len(text_chunks) - 1:
            next_emb = chunk_embeddings[top_idx + 1]
            if next_emb:
                sim_next = self.cosine_similarity(value_embedding, next_emb)
                candidates.append((sim_next, top_idx + 1, text_chunks[top_idx + 1]))

        if not candidates:
            return top_text

        # Step 4：选出相似度更高的相邻 chunk
        _, adj_idx, adj_text = max(candidates, key=lambda x: x[0])

        # Step 5：合并 —— 因无 overlap，直接拼接（保持原始顺序）
        if adj_idx < top_idx:
            # prev 在前
            merge_val = adj_text + top_text
        else:
            # next 在后
            merge_val = top_text + adj_text

        return merge_val

    def get_knowledge_merge_vals(
        self,
        job_type_id: str,
        node_id: str
    ) -> list[str]:
        """保持完全不变，仅依赖 get_merge_val_for_doc"""
        embeddings = get_local_embedding()

        value_record = self.graph.query(
            """
            MATCH (n)
            WHERE elementId(n) = $node_id
            RETURN n.id AS value
            """,
            params={"node_id": node_id}
        )

        if not value_record or not value_record[0].get("value"):
            print(f"警告: 节点 {node_id} 未找到有效文本值")
            return []

        value = value_record[0]["value"].strip()
        if not value:
            return []

        value_embedding = embeddings.embed_query(value)

        doc_records = self.graph.query(
            """
            MATCH (jt:职业类别)-[:属于]-(job:岗位)-[r]->(n)
            WHERE elementId(jt) = $job_type_id 
              AND elementId(n) = $node_id
              AND type(r) IN ['需要具有','需要掌握','需要持有','负责','需要来自']
            MATCH (doc:Document)-[:MENTIONS]->(n)
            RETURN DISTINCT elementId(doc) AS doc_id
            """,
            params={"job_type_id": job_type_id, "node_id": node_id}
        )

        doc_ids = [r["doc_id"] for r in doc_records if r.get("doc_id") is not None]
        if not doc_ids:
            print(f"未找到与 job_type_id={job_type_id} 和 node_id={node_id} 关联的 Document")
            return []

        result = []
        for doc_id in doc_ids:
            merge_val = self.get_merge_val_for_doc(
                doc_id=doc_id,
                value_embedding=value_embedding
            )
            if merge_val:
                result.append(merge_val)
        return result

    def get_job_property_merge_vals(
        self,
        job_type_id: str,
        property_type: str
    ) -> list[str]:
        """保持完全不变，仅依赖 get_merge_val_for_doc"""
        embeddings = get_local_embedding()

        job_records = self.graph.query(
            """
            MATCH (job:岗位)-[:属于]->(jt:职业类别)
            WHERE elementId(jt) = $job_type_id
            RETURN elementId(job) AS job_id, job[$prop_type] AS value
            """,
            params={"job_type_id": job_type_id, "prop_type": property_type}
        )

        seen_doc_ids = set()
        result = []

        for job_r in job_records:
            job_id = job_r.get("job_id")
            value = job_r.get("value")
            if not job_id or not isinstance(value, str) or not value.strip():
                continue

            value_embedding = embeddings.embed_query(value)

            doc_records = self.graph.query(
                """
                MATCH (doc:Document)-[:MENTIONS]->(job:岗位)
                WHERE elementId(job) = $job_id
                RETURN DISTINCT elementId(doc) AS doc_id
                """,
                params={"job_id": job_id}
            )

            for doc_r in doc_records:
                doc_id = doc_r.get("doc_id")
                if doc_id is None or doc_id in seen_doc_ids:
                    continue
                seen_doc_ids.add(doc_id)

                merge_val = self.get_merge_val_for_doc(
                    doc_id=doc_id,
                    value_embedding=value_embedding
                )
                if merge_val and merge_val.strip():
                    result.append(merge_val)

        print(f"处理 job_type_id={job_type_id}, 属性={property_type} → 找到 {len(result)} 个 merge_val")
        return result