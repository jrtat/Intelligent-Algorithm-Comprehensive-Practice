from func.build_graphrag import build_graphrag, deduplication, transform_properties_to_nodes
from func.extract_document import get_extracted_document

raw_text = get_extracted_document(start_pos= 1, length= 50)
build_graphrag(raw_text,'rewrite')
transform_properties_to_nodes()
deduplication()

# 后续有空在这里开发一个语言检查器