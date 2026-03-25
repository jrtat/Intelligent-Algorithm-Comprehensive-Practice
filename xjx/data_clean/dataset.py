# 数据清洗
import pandas as pd

df = pd.read_excel('data.xls')
# 岗位名称   地址	薪资范围	公司名称	所属行业	公司规模	公司类型	岗位编码	岗位详情	更新日期	公司详情	岗位来源地址

# 实体类
class Job():
    def __init__(self, id, name, company, city, salary, description, requirement, source):
        self.id = id
        self.name = name
        self.company = company
        self.city = city
        self.salary = salary
        self.description = description
        self.requirement = requirement
        self.source = source

class Company():
    def __init__(self, name, type, size, description):
        self.name = name
        self.type = type
        self.size = size
        self.description = description

class City():
    def __init__(self, name, population, location):
        self.name = name
        self.population = population
        self.location = location

class Industry():
    def __init__(self, name, description):
        self.name = name
        self.description = description

# 关系类

class Industry_Company():
    def __init__(self, industry, company):
        self.industry = industry
        self.company = company

# 数据处理

# 仅保存公司名称、所属行业、公司规模、公司类型、公司详情（去重）
df_company = df[['公司名称', '所属行业', '公司规模', '公司类型', '公司详情']]
df_company = df_company.drop_duplicates()

# 筛选行业：遍历所属行业，每个值中按","分割，不重复保存
industries = {}
for industry in df_company['所属行业']:
    industry = str(industry)
    for i in industry.split(','):
        industries[i] = Industry(i, '')

# 筛选公司：遍历公司名称，不重复保存
companies = {}
for index, company_inf in df_company.iterrows():
    companies[company_inf['公司名称']] = Company(company_inf['公司名称'], company_inf['公司类型'], company_inf['公司规模'], company_inf['公司详情'])


# 筛选地址
cities = {}
for city in df['地址']:
    cities[city] = City(city, '', '')

# 筛选岗位（顺带的不重复保存）
jobs = {}
for index, row in df.iterrows():
    jobs[row['岗位编码']] = Job(row['岗位编码'], row['岗位名称'], companies[row['公司名称']], cities[row['地址']], row['薪资范围'], row['岗位详情'], '', row['岗位来源地址'])


print(len(jobs), len(companies), len(cities), len(industries))

# 保存为 JSON 文件
import json

def job_to_dict(job):
    """将 Job 对象转换为字典"""
    return {
        'id': job.id,
        'name': job.name,
        'company': job.company.name if job.company else None,
        'city': job.city.name if job.city else None,
        'salary': job.salary,
        'description': job.description,
        'requirement': job.requirement,
        'source': job.source
    }

def company_to_dict(company):
    """将 Company 对象转换为字典"""
    return {
        'name': company.name,
        'type': company.type,
        'size': company.size,
        'description': company.description
    }

def city_to_dict(city):
    """将 City 对象转换为字典"""
    return {
        'name': city.name,
        'population': city.population,
        'location': city.location
    }

def industry_to_dict(industry):
    """将 Industry 对象转换为字典"""
    return {
        'name': industry.name,
        'description': industry.description
    }

# 构建完整的数据结构
data = {
    'jobs': {key: job_to_dict(job) for key, job in jobs.items()},
    'companies': {key: company_to_dict(company) for key, company in companies.items()},
    'cities': {key: city_to_dict(city) for key, city in cities.items()},
    'industries': {key: industry_to_dict(industry) for key, industry in industries.items()}
}

# 保存为 JSON 文件（中文正常显示）
with open('cleaned_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✓ 数据已保存到 cleaned_data.json")

# 可选：也可以保存为 CSV 格式（仅适用于 jobs 数据）
jobs_list = [job_to_dict(job) for job in jobs.values()]
df_jobs = pd.DataFrame(jobs_list)
df_jobs.to_csv('jobs.csv', index=False, encoding='utf-8-sig')
print("✓ 岗位数据已保存到 jobs.csv")

# 可选：保存公司为 CSV
companies_list = [company_to_dict(company) for company in companies.values()]
df_companies = pd.DataFrame(companies_list)
df_companies.to_csv('companies.csv', index=False, encoding='utf-8-sig')
print("✓ 公司数据已保存到 companies.csv")