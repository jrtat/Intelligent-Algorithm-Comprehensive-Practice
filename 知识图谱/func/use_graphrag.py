from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

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

def use_llm(hybrid_retriever,question: str):

    # Step 0：判断graphRAG是否已经构建完成了（通过判断hybrid_retriever是否存在）
    if hybrid_retriever is None:
        raise ValueError("请先调用 init() 初始化！")

    # Step 1：创建 LLM
    llm = get_llm_temp()
    
    # Step 2：构建 RAG Chain
    template = """
    你是一个专业、准确的助手。请严格基于以下上下文回答问题。
    如果上下文无法回答，请诚实说明“根据提供的信息无法确定”。

    上下文：
    {context}

    问题：{question}

    请用中文、结构清晰地回答（可分点）：
    """
    prompt = ChatPromptTemplate.from_template(template)
    rag_chain = (
            {"context": hybrid_retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )

    # Step 3：执行查询并得到答案
    answer = rag_chain.invoke(question)

    # Step 4：返回答案
    return answer
