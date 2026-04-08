import pandas as pd
from preprocess.desc import preprocess_job_desc, preprocess_company_desc
from preprocess.salary import preprocess_salary
from preprocess.industry import preprocess_industry
from func.build_graphrag import build_graphrag, deduplication, transform_properties_to_nodes
from func.extract_document import get_extracted_document

df = pd.read_excel("raw.xlsx")
df = preprocess_job_desc(df)
df = preprocess_company_desc(df)
df = preprocess_salary(df)
df = preprocess_industry(df)
df = pd.write_excel("processed.xlsx")

raw_text = get_extracted_document(start_pos= 1, length= 50)
build_graphrag(raw_text,'rewrite')
transform_properties_to_nodes()
deduplication()

# 后续有空在这里开发一个语言检查器