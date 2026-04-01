
from xjx.utils.LLMInvoker import LLMInvoker
from xjx.utils.FileProcessor import FileProcessor

if __name__ == '__main__':

    # 初始化LLM调用器

    model = LLMInvoker()
    fp = FileProcessor('data/cleaned_data.json')

    data = fp.read()

    # 批量提取岗位关键信息
    model.batch_extract_job_info(data["jobs"])

    # # 批量提取公司关键信息
    # model.batch_extract_company_info(companies)

