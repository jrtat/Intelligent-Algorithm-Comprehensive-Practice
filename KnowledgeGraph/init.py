import pandas as pd
from KnowledgeGraph.preprocess.desc import preprocess_job_desc, preprocess_company_desc
from KnowledgeGraph.preprocess.salary import preprocess_salary
from KnowledgeGraph.preprocess.industry import preprocess_industry_easy
from KnowledgeGraph.preprocess.loc import preprocess_loc
from KnowledgeGraph.func.build_graphrag import build_graphrag, deduplication, transform_properties_to_nodes
from KnowledgeGraph.func.extract_document import get_extracted_document
from KnowledgeGraph.func.build_vec import build_vec,build_chunk

def init_excel():
    df = pd.read_excel("raw.xlsx")
    df = preprocess_job_desc(df)
    df = preprocess_company_desc(df)
    df = preprocess_salary(df)
    df = preprocess_industry_easy(df)
    print("yes")
    df = preprocess_loc(df)
    df.dropna(subset=['岗位名称', '薪资范围', '所属行业', '公司名称', '公司规模', # '公司详情', '公司类型',
                      '岗位编码', '岗位详情'], inplace=True)
    df = df.drop_duplicates(subset=['岗位编码'])
    df.to_excel("processed.xlsx")

# init_excel()

# raw_text = get_extracted_document(start_pos= 9001, length= 40)
# build_graphrag(raw_text,'add')
# transform_properties_to_nodes()
# deduplication()
build_chunk()
