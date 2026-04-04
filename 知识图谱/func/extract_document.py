import pandas as pd

def extract_row(row):
    job_name = row['岗位名称']
    id = row['岗位编码']
    industry = row['所属行业']
    salary = row['薪资范围']
    location = row['地址']
    description = row['岗位详情']
    company_name = row['公司名称']
    company_type = row['公司类型']
    company_size = row['公司规模']
    company_desc = row['公司详情']
    text =  f'''
这是一个招聘信息。岗位ID为“{id}”，它属于“{job_name}”这一职业类别。该岗位的工作地点位于“{location}”。

该岗位的详细职责和要求（包含了该岗位对职业技能的要求）如下：{description}

该岗位的招聘公司是“{company_name}”。这家公司属于“{industry}”行业，公司规模为“{company_size}”，公司类型为“{company_type}”。关于该公司的其他信息：{company_desc}
'''
    # print(text)
    return text

def get_extracted_document(start_pos=1, length=100):
    df = pd.read_excel('raw.xlsx', header=0)
    df['text_for_llmtrans'] = df.apply(extract_row, axis=1)
    df = df.iloc[start_pos-1 : start_pos-1+length] # 从 start_pos 行（行号从1开始）截取 length 行
    return df['text_for_llmtrans'].tolist()
