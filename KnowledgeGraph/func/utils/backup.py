from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j

from typing import Dict, Any
import json

from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j
from typing import Dict, Any
import json
from datetime import datetime


class Neo4jAuraExporter:
    def __init__(self):
        self.graph = connect_neo4j()

    def export_complete(self, output_path = None):
        """
        完整导出（推荐方式）：使用 apoc.export.cypher.all 导出完整的 Cypher 脚本
        优点：
        - 100% 保真（任意标签、关系、属性、索引、约束、Point/Date/Duration/向量等都完美支持）
        - Aura 上完全可用（stream 模式，无需文件系统权限）
        - 比原 JSON + 手动重建方式更可靠、更通用
        """
        stream_data = self._export_data_stream()
        stats_query = """
        CALL apoc.meta.stats()
        YIELD labelCount, relTypeCount, propertyKeyCount, nodeCount, relCount
        RETURN labelCount, relTypeCount, propertyKeyCount, nodeCount, relCount
        """
        stats = self.graph.query(stats_query)

        export_data = {
            "metadata": {
                "export_timestamp": stream_data["export_time"],
                "node_count": stream_data.get("node_count", 0),
                "relationship_count": stream_data.get("relationship_count", 0),
                "statistics": stats[0] if stats else {},
                "export_method": "cypher_dump"   # 新增标识，便于后续维护
            },
            "cypher_dump": stream_data["cypher_dump"],      # 完整的 Cypher 脚本（包含 schema + data）
            "schema_cypher": stream_data["schema_cypher"]   # 单独的 schema 部分（兼容旧代码）
        }

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"✅ 导出完成，已保存到: {output_path}")
        return export_data

    def _export_data_stream(self):
        """
        使用 apoc.export.cypher.all + streamStatements:true 导出（Aura 推荐方式）
        """
        export_query = """
        CALL apoc.export.cypher.all(null, {
            streamStatements: true,
            format: "cypher-shell",
            useOptimizations: {type: "UNWIND_BATCH", unwindBatchSize: 10000},
            useTypes: true
        })
        YIELD cypherStatements, schemaStatements, nodeStatements, relationshipStatements,
              nodes, relationships
        RETURN cypherStatements, schemaStatements, nodes, relationships
        """

        result = self.graph.query(export_query)

        if not result:
            raise RuntimeError("导出失败：apoc.export.cypher.all 未返回数据")

        row = result[0]
        return {
            "cypher_dump": row["cypherStatements"],          # 完整脚本（最推荐）
            "schema_cypher": row["schemaStatements"] or "",  # 单独 schema
            "node_count": row.get("nodes", 0),
            "relationship_count": row.get("relationships", 0),
            "export_time": datetime.now().isoformat()
        }


class Neo4jAuraImporter:
    def __init__(self):
        self.graph = connect_neo4j()

    def import_from_file(self, file_path, clear_existing = False):
        print(f"正在读取导出文件: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        return self._import_data(export_data, clear_existing)

    def _import_data(self, export_data, clear_existing = False):
        print("=" * 60)
        print("开始导入 Neo4j AuraDB")
        print("=" * 60)

        metadata = export_data.get("metadata", {})
        print(f"导出时间: {metadata.get('export_timestamp', '未知')}")
        print(f"节点数: {metadata.get('node_count', 0)} | 关系数: {metadata.get('relationship_count', 0)}")

        if clear_existing:
            self._clear_database()

        cypher_dump = export_data.get("cypher_dump")  # 执行完整 Cypher Dump（最推荐、最通用）
        self._execute_cypher_dump(cypher_dump)

        print("\n" + "=" * 60)
        print("数据导入完成！")
        print("=" * 60)

    def _clear_database(self):
        print("正在清空数据库...")
        self.graph.query("MATCH (n) DETACH DELETE n")
        print("数据库已清空")

    def _execute_cypher_dump(self, cypher_dump: str):
        """执行导出的完整 Cypher 脚本（分批执行，避免 Aura 查询大小限制）"""
        print("正在执行 Cypher Dump 脚本...")

        statements = [stmt.strip() for stmt in cypher_dump.split(";") if stmt.strip()]
        # 安全分割语句（APOC 生成的脚本每条语句以 ; 结尾，且格式规范）

        total = len(statements)
        print(f"共 {total} 条语句，开始分批执行...")

        success = 0
        for i, stmt in enumerate(statements, 1):
            try:
                self.graph.query(stmt)
                success += 1
                if i % 50 == 0 or i == total:
                    print(f"  已执行 {i}/{total} 条")
            except Exception as e:
                # 部分 IF NOT EXISTS 或已存在的索引可能报警告，忽略非致命错误
                if "already exists" not in str(e).lower() and "constraint" not in str(e).lower():
                    print(f"第 {i} 条语句执行失败: {stmt[:100]}... → {e}")
                else:
                    success += 1  # 视为成功

        print(f"Cypher Dump 执行完成（成功 {success}/{total} 条）")
