import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding(): # xjx实验室的模型
    return OpenAIEmbeddings(
        model="qwen3-embedding:8b",
        base_url="http://59.72.63.156:14138/v1",  # 自定义端点
        api_key="Empty",
        dimensions=1536,
        tiktoken_enabled=False,
        check_embedding_ctx_length=False
    )

def get_embedding_temp():  # 临时的Embedding模型
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",  # 中文效果很好的开源模型
        model_kwargs={'device': 'cpu'},  # 没有 GPU 就用 cpu
        encode_kwargs={'normalize_embeddings': True}
    )

def get_llm():
    return ChatOpenAI(
        model="qwen3:8b",  # 模型名字（xjx实验室）
        base_url="http://59.72.63.156:14138/v1", # url（xjx实验室）
        api_key="EMPTY",  # vLLM 不需要真实 key
        temperature=0  # 温度0 = 输出最稳定（对于提取图谱这个应用来说，0是最好的，不要调这个参数）
    )

def get_llm_temp():
    return ChatOpenAI(
        model = "Qwen2.5-3B",  # 模型名字（本地）
        base_url="http://127.0.0.1:8000/v1",  # url本地
        api_key="EMPTY",  # vLLM 不需要真实 key
        temperature=0  # 温度0 = 输出最稳定（对于提取图谱这个应用来说，0是最好的，不要调这个参数）
    )