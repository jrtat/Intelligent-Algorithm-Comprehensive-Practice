from func.build_graphRAG import init, RAG_llm, hybrid_retriever
from func.use_graphRAG import test_search

raw_text = ["这里放你的第一段文本...", "这里放你的第二段文本..."] # 你的原始文本（以后可以换成从文件读取）
init(raw_text) # 初始化graphRAG后得到 hybrid_retriever
answer = use_llm(RAG_llm, hybrid_retriever, "熟练使用C++，Java，MySQL适合应聘哪些岗位？") # 提问

print("=== GraphRAG 的回答 ===")
print(answer) # 输出回答