# !/usr/bin/python3

class OboGraph(object):
	"""A pythonic graph of a generic Open Biomedical Ontology (OBO) directed acyclic graph (DAG)"""
	def __init__(self):
		self.node_list = []  # A list of node objects in the graph
		self.edge_list = []  # A list of edge objects between nodes in the graph
		self.id_index = {}  # A dictionary pointing ontology term IDs to the node object representing it in the graph
		self.vocab_index = {}  # A dictionary pointing every unique word in the ontology to a list of terms that contain that word. CAREFUL WITH THIS ONE

	def add_node(self, node):
		self.node_list.append(node)
		self.id_index[node.node_id] = node
		for word in node.name+node.definition:
			try:
				vocab_index[word].add(node.node_id)
			except KeyError():
				vocab_index[word] = set(node.node_id)

	def add_edge(self, edge):
		self.edge_list.append(edge)

class AbstractNode(object):
	def __init__(self):
		self.node_id = ""
		self.definition = ""
		