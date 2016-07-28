 # !/usr/bin/python3
import re

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
        # TODO: if hyphens give me problems, I can add the hyphenated word, 
        #break up the words and then add the words separately as well. 
        for word in re.findall(r"[\w'-]+", node.name + " " + node.definition):  # A phrase like "5'-dna ligation" will be split into ["5'-dna", "ligation"]
            try:
                self.vocab_index[word.lower()].add(node)
            except KeyError:
                self.vocab_index[word.lower()] = set([node])

    def add_edge(self, edge):
        self.edge_list.append(edge)

    def connect_nodes(self, allowed_relationships=None):
        """Connects nodes by adding node objects to appropriate edge objects 
        and vice-versa. Allowed relationships may be a list specified to add 
        only a set of desired relationship types"""
        for edge in self.edge_list:
            # add nodes to the edge
            edge.parent_node = self.id_index[edge.parent_id]
            edge.child_node = self.id_index[edge.child_id]
            #add edges to the node
            self.id_index[edge.parent_id].add_edge(edge, allowed_relationships)
            self.id_index[edge.child_id].add_edge(edge, allowed_relationships)

    #  TODO: Test current find_all_paths and add in options for filtering 
    #  relationship types
    #  FIXME: This exceeds max recursion depth in python
    def find_all_paths(self, start_node, end_node, direction='parent', allowed_relationships=None, path=[]):
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


class SubGraph(OboGraph):
    """A subgraph of Gene Ontology. Represents a concept in the graph. Needs 
    filtering methods for specifying nodes that have the correct keyword values 
    as specified by the keyword list."""
    def __init__(self, super_graph, keyword_list):
        super().__init__()
        self.super_graph = super_graph
        self.keyword_list = keyword_list
        self.allowed_nodes = [node for node in [super_graph.vocab_index[word] for word in keyword_list]]

    def _filter_nodes(self, vocab_index, keyword_list):
        """Returns a list of nodes that contain keywords """
        filtered_id_list = []
        for word in keyword_list:
            filtered_id_list.extend(vocab_index[word])
        return [self.super_graph.id_index[id] for id in filtered_id_list]


class Edge(object):
    """a generic edge for an OBO node that may be extended later into a subclass
    for ontologies like GO that are including go term extensions"""
    def __init__(self, parent_id, child_id, relationship, parent_node=None, child_node=None):
        self.parent_id = parent_id
        self.child_id = child_id
        self.relationship = relationship
        self.parent_node = parent_node
        self.child_node = child_node

    @property
    def parent_id(self):
        if self.parent_node :
            return self.parent_node.id
        else :
            return self._parent_id

    @parent_id.setter
    def parent_id(self, new_parent):
        self._parent_id = new_parent

    @property
    def child_id(self):
        if self.child_node :
            return self.child_node.id
        else :
            return self._child_id

    @child_id.setter
    def child_id(self, new_child):
        self._child_id = new_child

"""
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
    """Generic OBO node contaning all basic properties of a node except for an 
    edge list, which will be ontology-specific and defined in each node object 
    that inherits from this object."""
    def __init__(self):
        self.id = str()
        self.name = str()
        self.definition = str()
        self.edges = list()
        self.parent_node_set = set()
        self.child_node_set = set()
        self.obsolete = False


    def add_edge(self, edge, allowed_relationships):
        """Adds an edge to the node, and updates the """
        self.edges.append(edge)
        self.update_node(edge, allowed_relationships)

    def update_node(self, edge, allowed_relationships=None):
        if not allowed_relationships:
            if edge.child_id == self.id:
                self.parent_node_set.add(edge.parent_node)
            elif edge.parent_id == self.id:
                self.child_node_set.add(edge.child_node)
        else:
            if edge.child_id == self.id and edge.relationship in allowed_relationships:
                self.parent_node_set.add(edge.parent_node)
            elif edge.parent_id == self.id and edge.relationship in allowed_relationships:
                self.child_node_set.add(edge.child_node)
            

class GoGraphNode(AbstractNode):
    """Extends AbstractNode to include GO relevant information"""
    def __init__(self):
        super().__init__()
        self.sub_ontology = None


class SubGraphNode(AbstractNode):
    """An instance of a node within a subgraph of an OBO ontology (super-graph)
    """
    def __init__(self, super_node, allowed_relationships=None):
        self.super_node = super_node
        self.edges = list()
        self._populate_edges(allowed_relationships)
        self.update_node(allowed_relationships)
    
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
