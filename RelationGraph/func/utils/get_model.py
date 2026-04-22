import os
import torch
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

import os
from dotenv import load_dotenv
load_dotenv()

def get_embedding():
    """
    返回xjx实验室的模型
    :return: OpenAIEmbeddings的实例
    """
    return OpenAIEmbeddings(
        model=os.getenv('LOCAL_EMBEDDING_MODEL_NAME'),
        base_url=f"{os.getenv('LOCAL_BASE_URL')}/v1",  # 自定义端点
        api_key="Empty",
        dimensions=1536,
        tiktoken_enabled=False,
        check_embedding_ctx_length=False
    )

def get_embedding_temp():  # 临时的Embedding模型
    """
    一个轻量级的 Embedding 模型
    :return: HuggingFaceEmbeddings的实例
    """
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用设备: {device.upper()}（bge-m3）")
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",  # 中文效果很好的开源模型 BAAI/bge-m3
        model_kwargs = {
            'device': device
        },
        encode_kwargs = {
            'normalize_embeddings': True,
            'batch_size': 64 if device == "cuda" else 16  # GPU 可开大
        }
    )

def get_local_embedding(path="/home/xuejx/projects/Intelligent-Algorithm-Comprehensive-Practice/model/bge-m3"):
    """
    从本地加载一个 Embedding 模型
    :param path: 模型路径
    :return: HuggingFaceEmbeddings的实例
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用设备: {device.upper()}（{os.path.basename(path)}）")
    return HuggingFaceEmbeddings(
        model_name=path,
        model_kwargs = {
            'device': device
        },
        encode_kwargs = {
            'normalize_embeddings': True,
            'batch_size': 64 if device == "cuda" else 16  # GPU 可开大
        }
    )

def get_llm():
    """
    返回xjx实验室的模型
    :return: ChatOpenAI的实例
    """
    return ChatOpenAI(
        model=os.getenv('LOCAL_MODEL_NAME'),  # 模型名字（xjx实验室）
        base_url=f"{os.getenv('LOCAL_BASE_URL')}/v1", # url（xjx实验室）
        api_key="EMPTY",  # vLLM 不需要真实 key
        temperature=0  # 温度0 = 输出最稳定（对于提取图谱这个应用来说，0是最好的，不要调这个参数）
    )

def get_llm_temp():
    """
    返回本地的模型（必须在本地启动一个进程用来接收请求）
    :return: OpenAIEmbeddings的实例
    """
    return ChatOpenAI(
        model = "Qwen2.5-3B",  # 模型名字（本地）
        base_url="http://127.0.0.1:8000/v1",  # url本地
        api_key="EMPTY",  # vLLM 不需要真实 key
        temperature=0  # 温度0 = 输出最稳定（对于提取图谱这个应用来说，0是最好的，不要调这个参数）
    )

def get_llm_silicon_flow(
        model_name,
        api_key = os.getenv('SILICONFLOW_API')
    ):
    """
    .. note:
    【deepseek-ai/DeepSeek-R1-0528-Qwen3-8B】  免费

    .. note:
    【deepseek-ai/DeepSeek-R1-Distill-Qwen-7B】  免费

    .. note:
    【Qwen/Qwen3-8B】 免费

    .. note:
    【Qwen/Qwen2.5-7B-Instruct】 免费

    .. note:
    【Qwen/Qwen3.5-4B】 免费

    .. note:
    【THUDM/GLM-Z1-9B-0414】 免费

    .. note:
    【THUDM/GLM-4.1V-9B-Thinking】 免费

    .. note:
    【deepseek-ai/DeepSeek-V2.5】  1.33元 每百万



    :param model_name: 指定模型名字
    :param api_key: 指定api_key （默认是我（ls）的）
    :return: ChatOpenAI类型的实例
    """
    return ChatOpenAI(
        model= model_name,   # 或硅基流动上的对应 model id
        base_url="https://api.siliconflow.cn/v1",
        api_key=api_key,
        temperature=0.01      # 低温度，提高结构化输出稳定性
    )
