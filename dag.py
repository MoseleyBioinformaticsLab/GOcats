# !/usr/bin/python3


class OboGraph(object):
	"""A pythonic graph of a generic Open Biomedical Ontology (OBO) directed 
	acyclic graph (DAG)"""
	def __init__(self):
		self.node_list = []  # A list of node objects in the graph
		self.edge_list = []  # A list of edge objects between nodes in the graph
		self.id_index = {}  # A dictionary pointing ontology term IDs to the node object representing it in the graph
		self.vocab_index = {}  # A dictionary pointing every unique word in the ontology to a list of terms that contain that word. CAREFUL WITH THIS ONE

	def add_node(self, node):
		self.node_list.append(node)
		self.id_index[node.id] = node
		for word in node.name+node.definition:
			try:
				vocab_index[word].add(node.id)
			except KeyError():
				vocab_index[word] = set(node.id)

	def add_edge(self, edge):
		self.edge_list.append(edge)


class GoGraph(OboGraph):
	"""A Gene ontology specific DAG"""


class AbstractNode(object):
	"""Generic OBO node contaning all basic properties of a node except for 
	an edge list, which will be ontology-specific and defined in each node 
	object that inherits from this object."""
	def __init__(self):
		self.id = str()
		self.name = list()  # A list of strings (words) in the term name
		self.defintion = list()  # ... in the term definition

	def set_id(self, id):
		self.id = id

	def set_name(self, name):
		self.name = name_list

	def set_definition(self, defintion):
		self.definition = definition


class Edge(object):
	"""a generic edge for an OBO node that may be extended later into a 
	subclass for ontologies like GO that are including go term extensions"""
	def __init__(self):
		self.parent_id = str()
		self.child_id = str()
		self.relationship = str()
		self.parent_node = None
		self.child_node = None

"""
Can I handle the actual nodes pointers like this?
	@property
	def parent_node(self):
		return self._parent_node

	@parent_node.setter
	def parent_node(self, value):
		self._parent_node = value

	@property
	def child_node(self):
		return self._child_node
	
	@child_node.setter
	def child_node(self, value):
		self._child_node = value
"""	
	 


class GoDagNode(AbstractNode):
	"""Extends AbstractNode to include GO relevant information"""
	def __init__(self):
		super().__init__()
		self.dag_edges = list()  # A list of edge object pointers in the GO graph
		self.dag_parent_set = set()  # A set of parent (id's | node objects)? in the GO graph
		self.dag_child_set = set()  #... child ... in the GO graph

	def add_dag_edge(self, edge):
		self.dag_edges.append(edge)

		"""need to add in methods for adding (node ids | node object 
		pointers) to the dag_parent and dag_child sets"""


class SubDagNode(AbstractNode):
	"""Extends Abstract node to include GO relevent information GIVEN SUB-
	GRAPH CONSTRAINTS which deliniate a sub-DAG"""
	def __init__(self):
		super().__init__()
		self.subdag_edges = list()
		self.subdag_parent_set = set()
		self.subdag_child_set = set()
		self.dag_node = None  # Will be the node object in the overall dag, with the full edge list 
	
	def add_subdag_edge