from func.build_graphRAG import init
from func.use_graphRAG import use_llm
from func.extract_document import get_extracted_document

raw_text = get_extracted_document()
hybrid_retriever = init(raw_text) # 初始化graphRAG后得到 hybrid_retriever

answer = use_llm(hybrid_retriever,"熟练使用C++，Java，MySQL适合应聘哪些岗位？") # 提问

print("=== GraphRAG 的回答 ===")
print(answer) # 输出回答
