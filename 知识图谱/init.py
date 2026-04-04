from func.build_graphRAG import init
from func.extract_document import get_extracted_document

raw_text = get_extracted_document()
print("开始")
init(raw_text)
print("结束")