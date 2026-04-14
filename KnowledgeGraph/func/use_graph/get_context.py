from langchain_neo4j import Neo4jVector
from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j
from KnowledgeGraph.func.utils.get_models import get_embedding_temp
from tqdm import tqdm

class ContextGetter:
    def __init__(self, graph, embeddings):
        self.graph = graph
        self.embeddings = embeddings

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
        doc_id: int,
        value_embedding: list,
        chunk_overlap: int = 40
    ) -> str:
        """
        核心逻辑：对单个 Document 找到最相似的 Chunk + 其前后 Chunk 中更接近的一个，合并后返回 merge_val
        """
        # Step 1： 使用向量索引找出该 Document 下最相似的 1 个 Chunk（限制在该 doc 的 Chunk）
        records = self.graph.query(
            """
            CALL db.index.vector.queryNodes('chunk_index', 1, $value_embedding)
            YIELD node AS chunk, score
            MATCH (chunk)-[:FROM_DOCUMENT]->(d:Document)
            WHERE elementId(d) = $doc_id
            WITH chunk, score
    
            OPTIONAL MATCH (prev:Chunk)-[:NEXT_CHUNK]->(chunk)
            OPTIONAL MATCH (chunk)-[:NEXT_CHUNK]->(next:Chunk)
    
            RETURN 
                chunk.text AS top_text,
                prev.text AS prev_text,
                prev.chunk_embedding AS prev_emb,
                next.text AS next_text,
                next.chunk_embedding AS next_emb,
                score
            """,
            params={
                "value_embedding": value_embedding,
                "doc_id": doc_id
            }
        )

        if not records:
            return ""

        r = records[0]
        top_text = r.get("top_text") or ""
        prev_text = r.get("prev_text")
        prev_emb = r.get("prev_emb")
        next_text = r.get("next_text")
        next_emb = r.get("next_emb")

        if not top_text:
            return ""

        # Step 2：判断前后两个 Chunk 中哪个与 value 更接近
        candidates = []
        if prev_text and prev_emb:
            sim_prev = self.cosine_similarity(value_embedding, prev_emb)
            candidates.append((sim_prev, prev_text))
        if next_text and next_emb:
            sim_next = self.cosine_similarity(value_embedding, next_emb)
            candidates.append((sim_next, next_text))

        if not candidates:  # 如果没有前后 Chunk，直接返回 top
            return top_text

        best_sim, best_adj_text = max(candidates, key=lambda x: x[0]) # 选相似度最高的那个相邻 Chunk

        # Step 3：合并（处理重叠）
        if len(top_text) >= chunk_overlap and len(best_adj_text) >= chunk_overlap:
            # 由于 splitter 的 overlap 是固定 40 字符，且相邻 chunk 必然满足 end==start[overlap]
            if top_text[-chunk_overlap:] == best_adj_text[:chunk_overlap]:
                merged = top_text + best_adj_text[chunk_overlap:]
            else:
                merged = top_text + " " + best_adj_text  # 兜底
        else:
            merged = top_text + " " + best_adj_text

        return merged

    def get_knowledge_merge_vals(
        self,
        job_type_id: str,
        node_id: str # 该类型节点（已通过 job_type_id → 岗位 → node_id 两条边连接）
    ) -> list[str]:
        """
        返回 list，每个元素是对应 Document 的 merge_val。
        """

        # Step 0：与图建立连接 & 初始化模型


        # Step 1: 从知识节点取出文本值
        value_record = self.graph.query(
            f"""
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

        # Step 2：把得到的文本值向量化
        value_embedding = self.embeddings.embed_query(value)

        # Step 3：找出“与 node_id 直接相连”且“属于该 job_type 的岗位体系下” 的 Document
        doc_records = self.graph.query(
            """
            MATCH (jt:职业类别)-[:属于]-(job:岗位)-[r]->(n)
            WHERE elementId(jt) = $job_type_id 
              AND elementId(n) = $node_id
              AND type(r) IN ['需要具有','需要掌握','需要持有','负责','需要来自']
    
            MATCH (doc:Document)-[:MENTIONS]->(job)
    
            RETURN DISTINCT elementId(doc) AS doc_id
            """,
            params={"job_type_id": job_type_id, "node_id": node_id}
        )

        # Step 4：把找到的 Document 转成列表
        doc_ids = [r["doc_id"] for r in doc_records if r.get("doc_id") is not None]

        if not doc_ids:
            print(f"未找到与 job_type_id={job_type_id} 和 node_id={node_id} 关联的 Document")
            return []

        # Step 5: 对每个 Document 计算 merge_val
        result = [] # 记录结果
        for doc_id in doc_ids:
            merge_val = self.get_merge_val_for_doc(
                doc_id=doc_id,
                value_embedding=value_embedding
            ) # 使用辅助函数
            if merge_val:  # 只添加非空结果
                result.append(merge_val)

        return result

    def get_job_property_merge_vals(
        self,
        job_type_id: str,
        property_type: str  # "学历要求"、"晋升路径" 之一
    ) -> list[str]:
        """
        返回 list，每个元素是对应 Document 的 merge_val。
        """
        # Step 0：与图建立连接 & 初始化模型
        embeddings = get_embedding_temp()

        # Step 1：找出所有与 job_type 直接相连的 岗位 节点，并取出对应属性值
        job_records = self.graph.query(
            """
            MATCH (job:岗位)-[:属于]->(jt:职业类别)
            WHERE elementId(jt) = $job_type_id
            RETURN elementId(job) AS job_id, job[$prop_type] AS value
            """,
            params={ "job_type_id": job_type_id, "prop_type": property_type }
        )

        seen_doc_ids = set()   # 避免同一个 Document 被重复添加
        result = []

        # Step 2：遍历每个岗位，查找该岗位对应的 Document 并计算 merge_val
        for job_r in tqdm(job_records):
            job_id = job_r.get("job_id")
            value = job_r.get("value")

            if not job_id or not isinstance(value, str) or not value.strip():
                continue

            value_embedding = embeddings.embed_query(value) # 计算属性值 value 中的 embedding 值

            doc_records = self.graph.query(
                """
                MATCH (doc:Document)-[:MENTIONS]->(job:岗位)
                WHERE elementId(job) = $job_id
                RETURN DISTINCT elementId(doc) AS doc_id
                """,
                params={"job_id": job_id}
            ) # 找出该岗位被 Document 通过 [:MENTION] 关系指向的 Document 节点

            for doc_r in doc_records: # 实际上一个 岗位节点 只会连接一个 Document 节点
                doc_id = doc_r.get("doc_id")

                if doc_id is None or doc_id in seen_doc_ids: # 防止重复添加（没用）
                    continue
                seen_doc_ids.add(doc_id) # 记录 Document 节点的 id

                merge_val = self.get_merge_val_for_doc(
                    doc_id=doc_id,
                    value_embedding=value_embedding
                ) # 调用辅助函数

                if merge_val and merge_val.strip():   # 只添加非空结果
                    result.append(merge_val)

        print(f"处理 job_type_id={job_type_id}, 属性={property_type} → 找到 {len(result)} 个 merge_val")
        return result
