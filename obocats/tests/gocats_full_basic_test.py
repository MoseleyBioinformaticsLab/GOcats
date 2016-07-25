# !/usr/bin/python3
from . import dag
from . import parser

obo_parser = parser.OboParser()
go_dag = dag.GoGraph('cellular_component')
with open('/home/eugene/Databases/GeneOntology/07-14-2016/go.obo', 'r') as database:
    obo_parser.parse_go(database, go_dag)

print(len(go_dag.node_list))
print(len(go_dag.edge_list))
for node in go_dag.node_list:
	print(node.id)
for edge in go_dag.edge_list:
	print(edge.child_id, '-->', edge.parent_id, edge.relationship)

go_dag.connect_nodes()

print(go_dag.relationship_set)

test_node = go_dag.node_list[1117]

print(test_node.parent_id_set, '\n', '    -->', test_node.id, '\n', '        ', test_node.child_id_set)

