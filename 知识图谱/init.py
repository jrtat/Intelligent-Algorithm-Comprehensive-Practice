from func.build_graphrag import init
from func.extract_document import get_extracted_document

raw_text = get_extracted_document(1,20)
init(raw_text,'rewrite')