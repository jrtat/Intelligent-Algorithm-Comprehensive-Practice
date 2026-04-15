# 调取大语言模型

# 调取大语言模型
import requests
import json
from processor.utils.FileProcessor import FileProcessor
from tqdm import tqdm

import os
from dotenv import load_dotenv
load_dotenv()

class LLMInvoker:
    """
    本地Ollama模型通用调用器，支持提取岗位/公司详情关键信息
    由于服务器资源有限，建议只调用一个模型
    """

    def __init__(self, model_name=os.getenv('LOCAL_MODEL_NAME'), base_url=os.getenv('LOCAL_BASE_URL'), api_key=None):
        """
        初始化LLM调用器
        :param model_name: Ollama部署的模型名称（如qwen:7b、llama3:8b等）
        :param base_url: Ollama API基础地址
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{self.base_url}/api/generate"
        self.embeddings_url = f"{self.base_url}/api/embeddings"
        self.headers = {"Content-Type": "application/json"} # 指定发送格式是json，对输入输出的格式没有要求

    def call_ollama(self, prompt, format="string", stream=False):
        """
        底层调用Ollama API的方法
        :param prompt: 提示词
        :param format: 输出格式
        :param stream: 是否流式返回
        :return: 模型响应文本
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            # "format": format  # 指定格式输出，便于解析
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=240
            )
            response.raise_for_status()  # 抛出HTTP异常

            # if stream: # 实时查看信息
            #     # 流式响应处理（可选）
            #     result = ""
            #     for line in response.iter_lines():
            #         if line:
            #             line_data = json.loads(line)
            #             if "response" in line_data:
            #                 result += line_data["response"]
            #             if line_data.get("done"):
            #                 break
            #     return result
            # else:
            #     # 非流式响应
            response_data = response.json()
            return json.loads(response_data.get("response", "").strip()) # 尝试解析JSON（转数据结构）json.loads(response_data.get("response", "").strip())

        except requests.exceptions.RequestException as e:
            print(f"❌ 调用Ollama模型失败: {e}")
            return None

    def call_ollama_embedding(self, prompt):
        """
        调用 Ollama 模型获取嵌入向量
        :param prompt: 提示词
        :return: 嵌入向量（列表形式）
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt
        }

        try:
            response = requests.post(
                self.embeddings_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=120
            )
            response.raise_for_status()

            response_data = response.json()
            embedding = response_data.get("embedding", [])

            if not embedding:
                print(f"⚠️ 返回的 embedding 为空")
                return None

            return embedding

        except requests.exceptions.RequestException as e:
            print(f"❌ 调用 Ollama Embedding 模型失败：{e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ 解析 Embedding 响应失败：{e}")
            return None

    def extract_job_key_info(self, job_description):
        """
        提取岗位详情关键信息
        :param job_description: 原始岗位详情文本
        :return: 结构化的关键信息字典

        你是一个专业的信息提取助手。请分析以下岗位详情文本，提取并返回JSON格式的关键信息：
        # 现在有如下岗位详情：
        # {job_description}
        #
        # 请以列表的形式从中提取出岗位所需的所有证书或论文要求（certification），包括但不限于：
        # 1. 英语的四级（CET-4），六级（CET-6）；日语的N1-N5等。
        # 2. 各个岗位，技能的证书（如律师资格证，教师资格证，计算机二级等）。
        # 3. CCF，SCI，Nature等期刊，会议。
        # 请阅读完岗位详情后逐条列举，不要遗漏。要求直接使用原文的说法，不要输出思考过程，不要输出任何解释。
        #
        # 要求：仅返回JSON，不要额外解释，确保JSON格式可解析。
        """
        prompt = f"""
        请分析以下岗位详情文本，提取并返回JSON格式的关键信息，必须包含：
        1. 学历要求维度一（education_1）：字符串（无任何要求/中专及以上/大专及以上/本科及以上/硕士及以上/博士及以上）
        2. 学历要求维度二（education_2）：字符串（无任何要求/双一流/985、211）
        3. 创新能力：整型（分为0~3四档：
            0：不需要创新能力，比如岗位信息没有提到任何与创新能力相关的内容；
            1：需要一定的创新能力，多数普通人都具备这种创新能力；
            2：需要较高的创新能力，只有少数人拥有这种创新能力；
            3：需要极高的创新能力，只有极少数人拥有这种创新能力）
        4. 抗压能力：整型（分为0-3四档：
            0：工作强度低，不会出现加班，且与他人交流少；
            1：工作强度普通，很少出现加班，可能涉及与他人沟通，但对方态度往往比较温和；
            2：工作强度较高，在忙的时候总是会出现加班，涉及与他人沟通，且对方可能情绪激动或者态度较差；
            3：工作强度极高，加班是常态，涉及与他人沟通，且对方总是情绪激动且态度极差）
        5. 沟通能力：整型（分为0~3四档：
            0：不需要沟通能力，比如岗位信息没有提到任何与团队协作，沟通，交流相关的内容；
            1：需要一定的沟通能力，多数人都具有这种能力；
            2：需要较高的沟通能力，能够管理协调15人左右的团队，与少量客户沟通协调；
            3：需要极高的沟通能力，能够管理协调一个大的部门，同时与许多客户沟通协调）
        6. 学习能力：整型（分为0~3四档：
            0：岗位的业务没有什么难度，不需要任何学习能力；
            1：岗位的业务涉及一定专业知识，需要一定的学习能力；
            2：岗位的业务涉及大量专业知识，可能涉及开发，研发，科创等，需要较高的学习能力；
            3：岗位的业务涉及大量高深的专业知识，可能涉及尖端产业的开发，研发，科创等，需要极高的学习能力）
        7. 实习能力：整型（分为0~4五档：
            0：不需要有实习；
            1：需要有3个月以内的实习；
            2：需要有6个月以内的实习；
            3：需要有1年以内的实习；
            4：需要有1年以上的实习）
        8. 职业技能：列表
        9. 证书要求：列表

        岗位详情：
        {job_description}

        要求：仅返回JSON，不要额外解释，确保JSON格式可解析。
        """
        # 调用模型
        raw_response = self.call_ollama(prompt)
        if not raw_response:
            print("❌ 岗位信息解析失败")
            return None

        # 解析JSON响应
        try:
            key_info = json.loads(raw_response.strip())
            return key_info
        except json.JSONDecodeError:
            print(f"❌ 岗位信息解析失败，原始响应：{raw_response}")
            return None

    # def extract_company_key_info(self, company_description):
    #     """
    #     提取公司详情关键信息
    #     :param company_description: 原始公司详情文本
    #     :return: 结构化的关键信息字典
    #     """
    #     prompt = f"""
    #     请分析以下公司详情文本，提取并返回JSON格式的关键信息，包含但不限于：
    #     1. 公司简介（introduction）：字符串
    #     2. 主营业务（business）：列表形式
    #     3. 企业福利（benefits）：列表形式
    #     4. 发展阶段（stage）：字符串（如"初创期"、"成长期"、"上市公司"）
    #     5. 所在领域（field）：字符串（如"人工智能"、"电商"、"金融科技"）
    #
    #     公司详情：
    #     {company_description}
    #
    #     要求：仅返回JSON，不要额外解释，确保JSON格式可解析。
    #     """
    #     # 调用模型
    #     raw_response = self._call_ollama(prompt)
    #     if not raw_response:
    #         return None
    #
    #     # 解析JSON响应
    #     try:
    #         key_info = json.loads(raw_response.strip())
    #         return key_info
    #     except json.JSONDecodeError:
    #         print(f"❌ 公司信息解析失败，原始响应：{raw_response}")
    #         return None

    def batch_extract_job_info(self, jobs_dict, save_path="job_key_info.json"):
        """
        批量提取岗位关键信息并保存
        :param jobs_dict: 岗位字典（如initialize.py中的jobs）
        :param save_path: 保存路径
        """
        total = len(jobs_dict)
        print(f"开始批量提取{total}个岗位的关键信息...")
        tmp = 0
        for job_id, job in tqdm(jobs_dict.items()):

            if "key_info" not in job.keys():
                key_info = self.extract_job_key_info(job["description"])
                jobs_dict[job_id]["key_info"] = key_info

                tmp += 1
            if tmp % 20 == 0:
                fp = FileProcessor(save_path)
                fp.save(jobs_dict)
                # print(f"已保存{tmp}个岗位的关键信息")

        # 保存结果
        fp = FileProcessor(save_path)
        fp.save(jobs_dict)
        print(f"✅ 岗位关键信息已保存到 {save_path}")
        return jobs_dict

    # def batch_extract_company_info(self, companies_dict, save_path="company_key_info.json"):
    #     """
    #     批量提取公司关键信息并保存
    #     :param companies_dict: 公司字典（如initialize.py中的companies）
    #     :param save_path: 保存路径
    #     """
    #     company_key_info = {}
    #     total = len(companies_dict)
    #     print(f"开始批量提取{total}个公司的关键信息...")
    #
    #     for idx, (company_name, company) in tqdm(enumerate(companies_dict.items(), 1)):
    #         key_info = self.extract_company_key_info(company.description)
    #         company_key_info[company_name] = {
    #             "basic_info": {
    #                 "type": company.type,
    #                 "size": company.size
    #             },
    #             "key_info": key_info or {}
    #         }
    #
    #     # 保存结果
    #     fp = FileProcessor(save_path)
    #     fp.save(company_key_info)
    #     print(f"✅ 公司关键信息已保存到 {save_path}")
    #     return company_key_info

