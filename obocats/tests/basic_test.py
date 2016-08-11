# !/usr/bin/python3
from . import dag
from . import parser
from . import godag
from . import subdag

mlab_database = open('/mlab/data/databases/GeneOntology/05-26-2016/go.obo', 'r')  # @ work
#home_database = open('/home/eugene/Databases/GeneOntology/06-14-2016/go.obo', 'r')  # @home

# Parse GO and make the graph. 
go_dag = godag.GoGraph()
go_parser = parser.GoParser(mlab_database, go_dag)
go_parser.parse()
mlab_database.close()
go_dag.connect_nodes()

# Test printing
print(len(go_dag.node_list))
print(len(go_dag.edge_list))
for node in go_dag.node_list:
    print(node.id)
	
for edge in go_dag.edge_list:
    print(edge.child_id, '-->', edge.parent_id, edge.relationship)

print(go_dag.used_relationship_set)

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

subdag = subdag.SubGraph.from_filtered_graph(go_dag, ['mitochondrion', 'mitochondria', 'mitochondrial'])
#for node in sub_dag.node_list:
#	print(node)

#print([node.name for node in sub_dag.allowed_nodes])
#for node in subdag.node_list:
#	print(node.name)