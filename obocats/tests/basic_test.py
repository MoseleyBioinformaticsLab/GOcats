# !/usr/bin/python3
import sys
from . import dag
from . import parser
from . import godag
from . import subdag

database = open(sys.argv[1], "r")

# Parse GO and make the graph. 
go_dag = godag.GoGraph()
go_parser = parser.GoParser(database, go_dag)
go_parser.parse()
database.close()
go_dag.connect_nodes()

# Test printing
#print(len(go_dag.node_list))
#print(len(go_dag.edge_list))
#for node in go_dag.node_list:
#    print(node.id)
#    
#for edge in go_dag.edge_list:
#    print(edge.child_id, '-->', edge.parent_id, edge.relationship)

#print(go_dag.used_relationship_set)

#test_node = go_dag.node_list[1117]
#print([node.id for node in test_node.parent_node_set], '\n', '    -->', test_node.id, '\n', '        ', [node.id for node in test_node.child_node_set])
#for node in go_dag.root_nodes:
#   print(node.name)
#for node in go_dag.descendants(test_node):
#   print(node.name)

"""tests the path traversal method that doesnt work
node1 = go_dag.id_index['GO:0051079']
node2 = go_dag.id_index['GO:0007049']
test_paths = go_dag.find_all_paths(node1, node2)
print(test_paths)
"""

#for node in go_dag.orphans:
#   print(node.name)

subdag = subdag.SubGraph.from_filtered_graph(go_dag, ['mitochondrion'], "cellular_component")
print(subgraph.top_node.name)

#for node in subdag.node_list:
#    print(node.name, "\n", "    parents: ", [pnode.name for pnode in node.parent_node_set], "\n", "        children: ", [cnode.name for cnode in node.child_node_set])
#for orphan in subdag.orphans:
#    print(orphan.name)

#for node in subdag.node_list:
#   print(node)