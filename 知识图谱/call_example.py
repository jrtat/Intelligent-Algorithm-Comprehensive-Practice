from 知识图谱.func.search_graphrag import init_query_conf, query_common_quality, query_unique_content_to_b, query_industries

# 示例调用（把 "软件工程师" 和 "数据分析师" 替换成你实际的职业名称）
init_query_conf()

print("\n=== 共同素质 ===")
res3 = query_unique_content_to_b("软件测试", "Java")
print(res3["result"])