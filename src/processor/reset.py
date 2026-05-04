# 重置数据
from src.processor.utils.FileProcessor import FileProcessor

if __name__ == '__main__':
    fp = FileProcessor('data/cleaned_data.json')
    data = fp.read()
    # fp_jobs = FileProcessor('data/jobs.json')
    # fp_jobs.save(data['jobs'])
    fp_companies = FileProcessor('data/companies.json')
    fp_companies.save(data['companies'])
    fp_cities = FileProcessor('data/cities.json')
    fp_cities.save(data['cities'])
    fp_industries = FileProcessor('data/industries.json')
    fp_industries.save(data['industries'])
