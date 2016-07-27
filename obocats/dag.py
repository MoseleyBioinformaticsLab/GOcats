 # !/usr/bin/python3

class OboGraph(object):
    """A pythonic graph of a generic Open Biomedical Ontology (OBO) directed 
    acyclic graph (DAG)"""
    def __init__(self):
        self.node_list = list()  # A list of node objects in the graph
        self.edge_list = list()  # A list of edge objects between nodes in the graph
        self.id_index = dict()  # A dictionary pointing ontology term IDs to the node object representing it in the graph
        self.vocab_index = dict()  #TODO: make these pointers to objects. A dictionary pointing every unique word in the ontology to a list of terms that contain that word.
        self.used_relationship_set = set()  # A set of relationships found used in the ontology (may need to add a typedef_set to the OboGraph obj)
        self.root_nodes = list()  # A list of nodes with no parents in the graph. 

    def add_node(self, node):
        self.node_list.append(node)
        self.id_index[node.id] = node
        for word in node.name+node.definition:
            try:
                self.vocab_index[word].add(node.id)
            except KeyError:
                self.vocab_index[word] = set([node.id])

    def add_edge(self, edge):
        self.edge_list.append(edge)

    def connect_nodes(self):
        """Connects nodes by adding node objects to appropriate edge objects 
        and vice-versa. MUST BE CALLED AFTER BOTH NODE AND EDGE LISTS ARE
        POPULATED FROM THE DATABASE FILE"""
        for edge in self.edge_list:
            edge.parent_node = self.id_index[edge.parent_id]
            edge.child_node = self.id_index[edge.child_id]
            self.id_index[edge.parent_id].add_edge(edge)
            self.id_index[edge.parent_id].add_child_id(edge.child_id)
            self.id_index[edge.child_id].add_edge(edge)
            self.id_index[edge.child_id].add_parent_id(edge.parent_id)

    #  TODO: Test current find_all_paths and add in options for filtering relationship types
    #  FIXME: This exceeds max recursion depth in python
    def find_all_paths(self, start_node, end_node, direction='parent', allowable_relationships=[], path=[]):
        """Returns a list of all paths (lists of GO IDs) between two graph nodes
        (start_node, end_node) with the specified directionality. The start node
        and end node parameters must be node objects."""
        path = path + [start_node.id]  # Probably need to check here if the edge has the right relationship type 
        if start_node.id == end_node.id:
            return [path]
        if start_node.id != end_node.id and start_node.id in [node.id for node in self.root_nodes]:  # If direction = parent: the end_node was not encountered in the path and the top of the graph was reached.
            return []
        if start_node.id != end_node.id and end_node.child_id_set == set():  # If direction = child: the end_node was not encountered in the path and the end of the graph was reached. 
            return []
        if start_node.id not in self.id_index.keys():
            print("{} was not found in the graph!".format(start_node.id))
            return []
        paths = []
        if direction is 'parent':
            for parent_id in start_node.parent_id_set:
                if parent_id not in path:
                    extended_paths = self.find_all_paths(self.id_index[parent_id],
                                                          end_node, 'parent', path)
                    for p in extended_paths:
                        paths.append(p)
        elif direction is 'child':
            for child_id in start_node.child_id_set:
                if child_id not in path:
                    extended_paths = self.find_all_paths(self.id_index[child_id],
                                                         end_node, 'child', path)
                    for c in extended_paths:
                        paths.append(c)
        return paths


class GoGraph(OboGraph):
    """A Gene-Ontology-specific graph"""
    def __init__(self, sub_ontology=None):
        super().__init__()
        self.sub_ontology = sub_ontology

    def add_node(self, node):
        assert node.sub_ontology  # May or may not add a contition to filter out sub-ontologies here before adding them
        super().add_node(node)

    def add_edge(self, edge):
        super().add_edge(edge) # May or may not add conditions to filter edges to nodes contained in the sub-ontology before adding.

    def connect_nodes(self):
        """May need to specialize this method for GO issues like obsolete
        terms and such."""
        super().connect_nodes()


# TODO: Should GoSubGraph inherit from GoGraph or should it contain an instance of the GoGraph?
# Make a generic SubGraph that inherits from OboGraph and have a required parameter: parent_graph? Which will be the object 
# of the parent graph. Rationalle: I can't inherit the DATA from the parent class, because that gets added through parsing after the 
# object is instantiated, and I don't want to re-parse for every subpgraph. Because that would be not smart. 
class GoSubGraph(GoGraph):
    """A subgraph of Gene Ontology. Represents a concept in the graph
    Needs filtering methods for specifying nodes that have the correct 
    keyword values as specified by the keyword list."""
    def __init__(self, go_graph, keyword_list):
        super().__init__()
        self.go_graph = go_graph
        self.keyword_list = keyword_list
        self.allowed_nodes = self._filter_nodes(self.go_graph.vocab_index, self.keyword_list)  # Should be a list of nodes that contain words from the keyword list

    def _filter_nodes(self, vocab_index, keyword_list):
        """Returns a list of nodes that contain keywords """
        filtered_id_list = []
        for word in keyword_list:
            filtered_id_list.extend(vocab_index[word])
        return [self.go_graph.id_index[id] for id in filtered_id_list]

"""Can have a bunch of OBO graph objects
that inherit from the generic OboGraph
with specialized information and methods"""


class Edge(object):
    """a generic edge for an OBO node that may be extended later into a 
    subclass for ontologies like GO that are including go term extensions"""
    def __init__(self, parent_id, child_id, relationship, parent_node=None, child_node=None):
        self.parent_id = parent_id
        self.child_id = child_id
        self.relationship = relationship
        self.parent_node = parent_node
        self.child_node = child_node
"""
    @property
    def parent_id(self):
        if self.parent_node :
            return self.parent_node.id
        else :
            return self._parent_id

    @property
    def child_id(self):
        if self.child_node :
            return self.child_node.id
        else :
            return self._child_id

    # alternative implementation
    @property
    def parent_node(self):
        return self._parent_node

    @parent_node.setter
    def parent_node(self, new_parent):
        self._parent_node = new_parent
        if new_parent :
            self.parent_id = new_parent.id

    @property
    def child_node(self):
        return self._child_node
    
    @child_node.setter
    def child_node(self, new_child):
        self._child_node = new_child
        if new_child :
            self.child_id = new_child.id
"""        



class AbstractNode(object):
    """Generic OBO node contaning all basic properties of a node except for 
    an edge list, which will be ontology-specific and defined in each node 
    object that inherits from this object."""
    def __init__(self):
        self.id = str()
        self.name = str()  # A list of strings (words) in the term name
        self.definition = str()  # ... in the term definition
        self.edges = list()
        self.parent_id_set = None  # A set of OBO IDs that are the parents of the current term (cannot make node obj refs here because they can't go into sets. Need sets for set analysis later.)
        self.child_id_set = None  # .. children ...
        self.obsolete = False

    def set_id(self, id):  # dont need the first 4 functions, add @property syntax to the last three like before. change adding functions in parser to directly access the values. 
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_definition(self, definition):
        self.definition = definition

    def set_obsolete(self):
        self.obsolete = True

    def add_edge(self, edge):
        self.edges.append(edge)

    def update_node(self, allowed_relationships=None)
        # update parents and child sets based on its edges.

    def add_parent_id(self, parent_id):  #these will go into update node. 
        self.parent_id_set.add(parent_id)
    
    def add_child_id(self, child_id):
        self.child_id_set.add(child_id)


class GoGraphNode(AbstractNode):
    """Extends AbstractNode to include GO relevant information"""
    def __init__(self):
        super().__init__()
        self.sub_ontology = None

    def set_sub_ontology(self, sub_ontology): # delete this worthless setter.
        self.sub_ontology = sub_ontology

    def add_edge(self, edge):
        pass
    """need to add in methods for adding (node ids | node object 
    pointers) to the graph_parent and graph_child sets"""


class SubGraphNode(AbstractNode):
    """Extends Abstract node to include GO relevent information GIVEN SUB-
    GRAPH CONSTRAINTS which deliniate a subgraph"""
    def __init__(self, super_node, allowed_relationships=None):
        self.super_node = super_node  # Will be the node object in the full graph, with the full edge list
        self.edges = list()
        self._populate_edges(allowed_relationships)
        self.update_node()
    
        @property
        def id(self):
            return self.super_node.id

        @property
        def name(self):
            return self.super_node.name
        
        @property
        def definition(self):
            return self.super_node.definition

        @property
        def obsolete(self):
            return self.super_node.obsolete
