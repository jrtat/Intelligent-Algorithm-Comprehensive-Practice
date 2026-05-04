# 数据清洗
import pandas as pd
from src.processor.utils.FileProcessor import FileProcessor
# import os
# print(os.path.exists('data.xls'))

# 实体类（可以直接写为字典形式，这里为表直观使用面向对象）
class Job:
    def __init__(self, id, name, company, city, salary, description, source):
        self.岗位编码 = id
        self.岗位名称 = name
        self.公司名称 = company
        self.地址 = city
        self.薪资范围 = salary
        self.岗位详情 = description
        self.岗位来源地址 = source

class Company:
    def __init__(self, name, type, size, description):
        self.公司名称 = name
        self.公司类型 = type
        self.公司规模 = size
        self.公司详情 = description
        self.jobs = set()
        self.所属行业 = set() # 完整保留列表信息

class City: # 没必要（定位方便）
    def __init__(self, name):
        self.地址 = name
        self.jobs = set()

class Industry:
    def __init__(self, name):
        self.所属行业 = name
        self.companies = set()

# 关系类

# class CompanyIndustry:
#     def __init__(self, company, industry):
#         self.industry = industry
#         self.company = company

if __name__ == '__main__':
    # 数据处理

    df = pd.read_excel('data.xls')
    # 岗位名称   地址	薪资范围	公司名称	所属行业	公司规模	公司类型	岗位编码	岗位详情	更新日期	公司详情	岗位来源地址


    # 仅保存公司名称、所属行业、公司规模、公司类型、公司详情（去重）
    df_company = df[['公司名称', '所属行业', '公司规模', '公司类型', '公司详情']]
    df_company = df_company.drop_duplicates()

    # 筛选行业：遍历所属行业，每个值中按","分割，不重复保存
    industries = {}
    for industry in df_company['所属行业']:
        industry = str(industry)
        for i in industry.split(','):
            industries[i] = Industry(i)

    # 筛选地址
    cities = {}
    for city in df['地址']:
        cities[city] = City(city)

    # 筛选公司：遍历公司名称，不重复保存
    companies = {}
    for index, company_inf in df_company.iterrows():
        companies[company_inf['公司名称']] = Company(company_inf['公司名称'], company_inf['公司类型'], company_inf['公司规模'], str(company_inf['公司详情']).replace('<br>', ''))
        for i in str(company_inf['所属行业']).split(','):
            industries[i].companies.add(company_inf['公司名称'])
            companies[company_inf['公司名称']].所属行业.add(i)

    # 筛选岗位（顺带的不重复保存）
    jobs = {}
    for index, row in df.iterrows():
        jobs[row['岗位编码']] = Job(row['岗位编码'], row['岗位名称'], row['公司名称'], row['地址'], row['薪资范围'], str(row['岗位详情']).replace('<br>', ''), row['岗位来源地址'])
        companies[row['公司名称']].jobs.add(row['岗位编码'])
        cities[row['地址']].jobs.add(row['岗位编码'])


    print(len(jobs), len(companies), len(cities), len(industries))

    # 保存为 JSON 文件
    f = FileProcessor('data/cleaned_data.json')
    f.save({"jobs": jobs, "companies": companies, "cities": cities, "industries": industries})

    print("✓ 数据已保存到 cleaned_data.json")

    # # 可选：也可以保存为 CSV 格式（仅适用于 jobs 数据）
    # jobs_list = [job_to_dict(job) for job in jobs.values()]
    # df_jobs = pd.DataFrame(jobs_list)
    # df_jobs.to_csv('jobs.csv', index=False, encoding='utf-8-sig')
    # print("✓ 岗位数据已保存到 jobs.csv")
    #
    # # 可选：保存公司为 CSV
    # companies_list = [company_to_dict(company) for company in companies.values()]
    # df_companies = pd.DataFrame(companies_list)
    # df_companies.to_csv('companies.csv', index=False, encoding='utf-8-sig')
    # print("✓ 公司数据已保存到 companies.csv")
