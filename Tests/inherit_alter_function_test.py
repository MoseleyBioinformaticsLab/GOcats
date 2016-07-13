class OboGraph(object):
	"""A pythonic graph of a generic Open Biomedical Ontology (OBO) directed 
	acyclic graph (DAG)"""
	def __init__(self):
		self.node_list = list()  # A list of node objects in the graph
		self.edge_list = list()  # A list of edge objects between nodes in the graph
		self.id_index = dict()  # A dictionary pointing ontology term IDs to the node object representing it in the graph
		self.vocab_index = dict()  # A dictionary pointing every unique word in the ontology to a list of terms that contain that word. CAREFUL WITH THIS ONE

	def add_node(self, node):
		self.node_list.append(node)
		self.id_index[node.id] = node
		for word in node.name+node.definition:
			try:
				self.vocab_index[word].add(node.id)
			except KeyError:
				self.vocab_index[word] = set([node.id])
				pass

	def add_edge(self, edge):
		self.edge_list.append(edge)


class GoGraph(OboGraph):
	"""A Gene-Ontology-specific DAG"""
	def __init__(self, sub_ontology):
		super().__init__()
		self.sub_ontology = sub_ontology

	def add_node(self, node):
		assert node.sub_ontology  # make sure that the node provided has a sub_ontology speicfied (need to add option for incorporating all in the future)
		if node.sub_ontology == self.sub_ontology:
			super().add_node(node)
		else:
			pass  # Don't add nodes to the graph that aren't in the specified GO sub-ontology 

"""Can have a bunch of OBO graph objects
that inherit from the generic OboGraph
with specialized information and methods"""


class AbstractNode(object):
	def __init__(self):
		self.id = str()
		self.name = list()  # A list of strings (words) in the term name
		self.definition = list()  # ... in the term definition

	def set_id(self, id):
		self.id = id

	def set_name(self, name):
		self.name = name

	def set_definition(self, definition):
		self.definition = definition


class GoDagNode(AbstractNode):
	"""Extends AbstractNode to include GO relevant information"""
	def __init__(self):
		super().__init__()
		self.sub_ontology = str()

	def set_sub_ontology(self, sub_ontology):
		self.sub_ontology = sub_ontology

"""can also have a bunch of Nodes objects 
specific to OBO ontologies"""



#executed in some top-level module
pokedex = GoGraph('pokemon')  # a hypothetical pokemon sub-ontology of GO.

#Parser.parse_go(database_file, pokedex)
#Creates nodes and edges like so:
node1 = GoDagNode()

node1.set_id('GO:XXXXXX1')
node1.set_name(['pikachu'])
node1.set_definition(['an', 'electric', 'pokemon'])
node1.set_sub_ontology('pokemon')

pokedex.add_node(node1)

node2 = GoDagNode()

node2.set_id('GO:XXXXXX2')
node2.set_name(['bulbasaur'])
node2.set_definition(['a', 'grass', 'pokemon'])
node2.set_sub_ontology('pokemon')

pokedex.add_node(node2)

node3 = GoDagNode()

node3.set_id('GO:XXXXX9')
node3.set_name(['day', 'man'])
node3.set_definition(['fighter', 'of', 'the', 'night', 'man'])
node3.set_sub_ontology('philadelphia')  #this shouldn't be added to pokedex because its not a pokemon 

pokedex.add_node(node3)

"""same basic thing for edges"""

for node in pokedex.node_list:
	print(node.id, node.name, node.definition, node.sub_ontology)

print(pokedex.vocab_index)

phil_dag = GoGraph('philadelphia')  # a hypothetical 'It's Always Sunny in Philadelphia' sub-ontology of GO

phil_dag.add_node(node3)

for node in phil_dag.node_list:
	print(node.id, node.name, node.definition, node.sub_ontology)

print(phil_dag.vocab_index)

