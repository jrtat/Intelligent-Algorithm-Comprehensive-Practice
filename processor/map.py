from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j
from processor.utils.FileProcessor import FileProcessor

from KnowledgeGraph.func.use_graph.cypher_search import Searcher

if __name__ == '__main__':
    graph = connect_neo4j()
    searcher = Searcher(graph)
    ids = searcher.get_all_node_ids_by_label("职业类别")

    fp_id2num = FileProcessor("maps/id2num.json")
    dic_id2num = {}
    fp_num2jt = FileProcessor("maps/num2jt.json")
    dic_num2jt = {}

    for i in range(len(ids)):
        dic_id2num[ids[i]] = str(i)
        dic_num2jt[str(i)] = searcher.get_property_by_internal_id(ids[i], "id")

    fp_id2num.save(dic_id2num)
    fp_num2jt.save(dic_num2jt)


