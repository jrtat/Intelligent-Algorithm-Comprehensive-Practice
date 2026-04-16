from langchain_community.graphs import Neo4jGraph

import os
from dotenv import load_dotenv
load_dotenv()

def connect_neo4j():
    """
    :return: Neo4jGraph类型的实例
    """
    return Neo4jGraph(
        url=os.getenv('GRAPH_URL'),
        username=os.getenv('GRAPH_USERNAME'),
        password=os.getenv('GRAPH_PASSWORD'),
        database=os.getenv('DATABASE_NAME'),
        refresh_schema=True,
    )