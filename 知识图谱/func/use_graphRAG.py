from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def use_llm(llm, hybrid_retriever, question: str): #

    # Step 0：判断graphRAG是否已经构建完成了
    if hybrid_retriever is None:
        raise ValueError("请先调用 init() 初始化！")

    # Step 1：构建 RAG Chain
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

    # Step 2：执行查询并得到答案
    answer = rag_chain.invoke(question)

    # Step 3：返回答案
    return answer