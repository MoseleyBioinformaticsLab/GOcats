# !/usr/bin/python3
from . import dag
from . import parser

obo_parser = parser.OboParser()
go_dag = dag.GoGraph('cellular_component')
with open('/mlab/data/databases/GeneOntology/05-26-2016/go.obo', 'r') as database:
    obo_parser.parse_go(database, go_dag)

#print(len(go_dag.node_list))
#print(len(go_dag.edge_list))
#for node in go_dag.node_list:
#    print(node.id)
	
#for edge in go_dag.edge_list:
#    print(edge.child_id, '-->', edge.parent_id, edge.relationship)

go_dag.connect_nodes(['is_a', 'regulates'])

#print(go_dag.used_relationship_set)

test_node = go_dag.node_list[1117]

print([node.id for node in test_node.parent_node_set], '\n', '    -->', test_node.id, '\n', '        ', [node.id for node in test_node.child_node_set])
for node in go_dag.root_nodes:
	print(node.name)

"""tests the path traversal method that doesnt work
node1 = go_dag.id_index['GO:0051079']
node2 = go_dag.id_index['GO:0007049']
test_paths = go_dag.find_all_paths(node1, node2)
print(test_paths)
"""

sub_dag = dag.SubGraph(go_dag, ['mitochondrion', 'mitochondria', 'mitochondrial'])
for node in sub_dag.allowed_nodes:
	print(node.name)

#print([node.name for node in sub_dag.allowed_nodes])