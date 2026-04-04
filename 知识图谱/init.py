from func.build_graphrag import init,deduplication
from func.utils.extract_document import get_extracted_document

raw_text = get_extracted_document(1,5)
init(raw_text,'rewrite')
deduplication()