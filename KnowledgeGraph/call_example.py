from KnowledgeGraph.func.use_graph.chyper_search import get_node_id_by_value_and_label,get_related_node_ids

# print(get_job_property_merge_vals(1880,"学历要求"))
id = get_node_id_by_value_and_label("统计员","职业类别","id")
print(id)
print(get_related_node_ids(id, "属于"))
print(len(get_related_node_ids(id, "属于")))
