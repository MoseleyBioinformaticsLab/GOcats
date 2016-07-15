# !/usr/bin/python3
from . import dag
from . import parser

obo_parser = parser.OboParser()
little_godag = dag.GoGraph('cellular_component')
with open('/home/eugene/little_go.obo', 'r') as database:
    obo_parser.parse_go(database, little_godag)

print(len(little_godag.node_list))
print(len(little_godag.edge_list))
for node in little_godag.node_list:
	print(node.id)
for edge in little_godag.edge_list:
	print(edge.child_id, '-->', edge.parent_id, edge.relationship)
