
from src.processor.utils.FileProcessor import FileProcessor
from src.processor.utils.ExcelMaker import ExcelMaker

if __name__ == '__main__':
    # 合并信息
    fp_jobs = FileProcessor("data/jobs.json")
    fp_companies = FileProcessor("data/companies.json")
    fp_cites = FileProcessor("data/cities.json")

    data = fp_jobs.read()
    data_2 = fp_companies.read()
    data_3 = fp_cites.read()

    for i in data.keys():
        if "公司名称" in data[i] and data[i]["公司名称"] in data_2:
            for k, v in data_2[data[i]["公司名称"]].items():
                if k == "jobs":
                    continue
                data[i][k] = v

        if "地址" in data[i] and data[i]["地址"] in data_3:
            for k, v in data_3[data[i]["地址"]].items():
                if k == "jobs":
                    continue
                data[i][k] = v

    em = ExcelMaker('output.xlsx')
    em.save_job(data)

