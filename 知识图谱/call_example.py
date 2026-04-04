from func.build_graphrag import get_retriever
from func.use_graphrag import use_llm

hybrid_retriever = get_retriever() # 初始化graphRAG后得到 hybrid_retriever
answer = use_llm(hybrid_retriever,"熟练使用C++，Java，MySQL适合应聘哪些岗位？") # 提问
print("=== GraphRAG 的回答 ===")
print(answer) # 输出回答
