# !/usr/bin/python3
from . import dag
from . import parser

obo_parser = parser.OboParser()
go_dag = dag.GoGraph('cellular_component')
with open('/mlab/data/databases/GeneOntology/05-26-2016/go.obo', 'r') as database:
    obo_parser.parse_go(database, go_dag)

print(len(go_dag.node_list))
print(len(go_dag.edge_list))
for node in go_dag.node_list:
	print(node.id)
for edge in go_dag.edge_list:
	print(edge.child_id, '-->', edge.parent_id, edge.relationship)

