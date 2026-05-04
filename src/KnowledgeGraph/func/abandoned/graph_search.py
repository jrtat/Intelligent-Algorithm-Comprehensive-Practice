from src.KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j
from src.KnowledgeGraph.func.utils.get_models import get_llm_silicon_flow

from langchain_community.graphs import Neo4jGraph
from langchain_neo4j import GraphCypherQAChain
from langchain_openai import ChatOpenAI

#--- 声明全局变量 ---#
graph_to_query: Neo4jGraph
llm_to_query: ChatOpenAI
chain: GraphCypherQAChain

def init_query_conf():
    """
    为GraphCypherQAChain查询做准备，主要是以下3点：
    1. 与Neo4j连接
    2. 与llm连接
    3. 初始化GraphCypherQAChain
    """
    # Step 0：声明全局变量
    global graph_to_query, llm_to_query, chain

    # 与 Neo4j 数据库建立连接
    graph_to_query = connect_neo4j()

    # Step 1： 与llm连接
    llm_to_query = get_llm_silicon_flow("deepseek-ai/DeepSeek-V2.5")

    # Step 2： 初始化GraphCypherQAChain
    chain = GraphCypherQAChain.from_llm(
        llm=llm_to_query,
        graph=graph_to_query,
        verbose=True,  # 打印生成的 Cypher 和中间步骤，便于调试
        validate_cypher=True, # 有效性验证，会验证生成的 Cypher 查询是否有效
        return_intermediate_steps=True,  # 返回 Cypher 查询语句和原始结果
        allow_dangerous_requests=True,  # LangChain 较新版本需要此参数（允许危险操作）
    )

def query_common_quality(occupation_a: str, occupation_b: str):
    """
    职业A 与 职业B 有哪些 综合素质 是共通的？
    """
    question = f"请问职业类型“{occupation_a}”与职业类型“{occupation_b}”有哪些“综合素质”是共通的？"
    result = chain.invoke({"query": question})
    return result

def query_common_skill(occupation_a: str, occupation_b: str):
    """
    职业A 与 职业B 有哪些 专业技能 是共通的？
    """
    question = f"职业类型“{occupation_a}”与职业类型“{occupation_b}”有哪些“专业技能”是共通的？"
    result = chain.invoke({"query": question})
    return result

def query_common_certificate(occupation_a: str, occupation_b: str):
    """
    职业A 与 职业B 有哪些 证书 是共通的？
    """
    question = f"职业类型“{occupation_a}”与“{occupation_b}”有哪些“证书”是共通的？"
    result = chain.invoke({"query": question})
    return result

def query_common_content(occupation_a: str, occupation_b: str):
    """
    职业A 与 职业B 有哪些 工作内容 是共通的？
    """
    question = f"职业类型“{occupation_a}”与“{occupation_b}”有哪些“工作内容”是共通的？"
    result = chain.invoke({"query": question})
    return result

def query_unique_quality_to_b(occupation_a: str, occupation_b: str):
    """
    职业B 的哪些 综合素质 是职业A没有的？
    """
    question = f"职业类型“{occupation_b}”的哪些“综合素质”是职业类型“{occupation_a}”没有的？"
    result = chain.invoke({"query": question})
    return result

def query_unique_skill_quality_to_b(occupation_a: str, occupation_b: str):
    """
    职业B 的哪些 专业技能 是职业A没有的？
    """
    question = f"职业类型“{occupation_b}”的哪些“专业技能”是职业类型“{occupation_a}”没有的？"
    result = chain.invoke({"query": question})
    return result

def query_unique_certification_to_b(occupation_a: str, occupation_b: str):
    """
    职业B 的哪些 证书 是职业A没有的？
    """
    question = f"职业类型“{occupation_b}”的哪些“证书”是职业类型“{occupation_a}”没有的？"
    result = chain.invoke({"query": question})
    return result

def query_unique_content_to_b(occupation_a: str, occupation_b: str):
    """
    职业B 的哪些 工作内容 是职业A没有的？
    """
    question = f"职业类型“{occupation_b}”的哪些“工作内容”是职业类型“{occupation_a}”没有的？"
    result = chain.invoke({"query": question})
    return result

def query_industries(occupation_a: str):
    """
    职业A 都涉及哪些行业？
    """
    question = f"职业类型“{occupation_a}”都涉及哪些行业？"
    result = chain.invoke({"query": question})
    return result
