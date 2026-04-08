import pandas as pd
from preprocess.desc import preprocess_job_desc, preprocess_company_desc
from preprocess.salary import preprocess_salary
from preprocess.industry import preprocess_industry_easy
from preprocess.loc import preprocess_loc
from func.build_graphrag import build_graphrag, deduplication, transform_properties_to_nodes
from func.extract_document import get_extracted_document

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

raw_text = get_extracted_document(start_pos= 1, length= 100)
build_graphrag(raw_text,'rewrite')
# transform_properties_to_nodes()
# deduplication()