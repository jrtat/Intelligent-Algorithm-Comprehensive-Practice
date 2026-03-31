import pandas as pd

def extract_row(row):
    job_name = ['岗位名称']
    id = row['岗位编码']
    industry = row['所属行业']
    salary = row['薪资范围']
    location = row['地址']
    description = row['岗位详情']
    company_name = row['公司名称']
    company_type = row['公司类型']
    company_size = row['公司规模']
    company_desc = row['公司详情']
    return f'''
这个招聘信息ID为 {id}，其提供的岗位名称为 {job_name}，提供的薪资为{salary}，工作地为{location}，岗位详情如下：
{description}
提供该岗位的公司为 {company_name}，这个公司所属行业为 {industry}，公司的规模为 {company_size}，公司类型为 {company_type}，公司详情如下：
{company_size}
'''

def get_extracted_document():
    df = pd.read_excel('raw.xlsx', header=0)
    df['text_for_llmtrans'] = df.apply(extract_row, axis=1)
    df = df.head(10) # 临时，先截取一部分
    return df['text_for_llmtrans'].tolist()
