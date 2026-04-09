import pandas as pd

def extract_row(row):
    """
    把df中的一行转成一个字符串
    """
    job_name = row['岗位名称']
    job_id = row['岗位编码']
    industry = row['所属行业']
    salary = row['薪资范围']
    location = row['地址']
    description = row['岗位详情']
    company_name = row['公司名称']
    company_type = row['公司类型']
    company_size = row['公司规模']
    company_desc = row['公司详情']
    text =  f'''
这是一个招聘信息。岗位为“{job_id}”，它属于“{job_name}”这一职业。该岗位的工作地点位于“{location}”，薪资约为{salary}每月。

该岗位的详细职责和要求（包含了该岗位对技术能力的要求）如下：{description}

该岗位由“{company_name}”提供。{company_name}属于“{industry}”行业，公司规模为“{company_size}”，公司类型为“{company_type}”。公司的简介如下：{company_desc}
'''
    return text

def get_extracted_document(file_name = 'processed.xlsx', start_pos=1, length=100):
    """
    从Excel文件中读入数据，并将其处理成字符串列表，每个字符串是Excel中的一行。可以指定从哪行开始，读入多少行，以便进行分批处理。
    :param file_name: Excel的名字
    :param start_pos: 开始的行数（从1开始计数）
    :param length: 截取的长度
    :return: 处理好的字符串列表
    """
    df = pd.read_excel(file_name, header=0)
    df['text_for_llm'] = df.apply(extract_row, axis=1)
    df = df.iloc[start_pos-1 : start_pos-1+length] # 从 start_pos 行（行号从1开始）截取 length 行
    return df['text_for_llm'].tolist()
