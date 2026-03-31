from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

def use_llm(hybrid_retriever,question: str):

    # Step 0：判断graphRAG是否已经构建完成了
    if hybrid_retriever is None:
        raise ValueError("请先调用 init() 初始化！")

    # Step 1：声明大模型
    llm = ChatOpenAI(
        model="Qwen2.5-3B",  # 你在 vLLM 里部署的模型名字
        base_url="http://127.0.0.1:8000/v1",  # vLLM 的 OpenAI 兼容接口
        api_key="EMPTY",  # vLLM 不需要真实 key
        temperature=0  # 温度0 = 输出最稳定（提取图谱必须这样）
    )

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
