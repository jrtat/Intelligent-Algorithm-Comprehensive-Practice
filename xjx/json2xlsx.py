
from xjx.utils.FileProcessor import FileProcessor
from xjx.utils.ExcelMaker import ExcelMaker

if __name__ == '__main__':
    fp = FileProcessor("data/job_key_info.json")

    data = fp.read()

    em = ExcelMaker('data/output.xlsx')
    em.save_job(data)

