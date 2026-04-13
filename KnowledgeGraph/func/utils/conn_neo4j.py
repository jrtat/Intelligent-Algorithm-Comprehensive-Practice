from langchain_community.graphs import Neo4jGraph

#--- 全局变量 ---#
# database_name = "bde42e4c"
# graph_url = "neo4j+s://bde42e4c.databases.neo4j.io"
# graph_username = "bde42e4c"
# graph_password = "Bj11oN-jZzUGJ47resfaMFvqZBxX7FE2JiUnZSBzcPY"

#--- 全局变量 ---#
database_name = "1f5dcc17"
graph_url = "neo4j+s://1f5dcc17.databases.neo4j.io"
graph_username = "1f5dcc17"
graph_password = "J1-Sv2VA6q5Qw3rH5vFQSmYCwMtuCpF8kqt-W0UrEDU"

def connect_neo4j():
    """
    :return: Neo4jGraph类型的实例
    """
    global database_name, graph_url, graph_username, graph_password
    return Neo4jGraph(
        url=graph_url,
        username=graph_username,
        password=graph_password,
        database=database_name,
        refresh_schema=True,
    )