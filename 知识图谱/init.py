from func.build_graphRAG import init, get_retriever
from func.use_graphRAG import use_llm
from func.extract_document import get_extracted_document

raw_text = get_extracted_document()
init(raw_text)
