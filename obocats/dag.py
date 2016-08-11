 # !/usr/bin/python3
import re

class OboGraph(object):

    """A pythonic graph of a generic Open Biomedical Ontology (OBO) directed 
    acyclic graph (DAG)"""

    def __init__(self):
        self.node_list = list()
        self.edge_list = list()
        self.id_index = dict()
        self.vocab_index = dict() 
        self.used_relationship_set = set()  
        self.root_nodes = list()  

    def add_node(self, node):
        self.node_list.append(node)
        self.id_index[node.id] = node
        for word in re.findall(r"[\w'-]+", node.name + " " + node.definition):  # If hyphens give me problems, I can add the hyphenated word, break up the words and then add the words separately as well. A phrase like "5'-dna ligation" will be split into ["5'-dna", "ligation"]
            try:
                self.vocab_index[word.lower()].add(node)
            except KeyError:
                self.vocab_index[word.lower()] = set([node])

    def add_edge(self, edge):
        self.edge_list.append(edge)

    def connect_nodes(self, allowed_relationships=None):
        """Connects nodes by adding node objects to appropriate edge objects 
        and vice-versa. May specify allowed_relationships in a list."""
        for edge in self.edge_list:
            edge.parent_node = self.id_index[edge.parent_id]  # add nodes to the edge
            edge.child_node = self.id_index[edge.child_id]
            self.id_index[edge.parent_id].add_edge(edge, allowed_relationships)  # add edges to the node
            self.id_index[edge.child_id].add_edge(edge, allowed_relationships)

    def filter_nodes(self, keyword_list, sub_ontology_filter=None):
        """Returns a list of nodes that contain words in the given keyword list.
        An aditional sub-ontology filter may be specified when needed."""
        filtered_nodes = set.union(*[node_set for node_set in [self.vocab_index[word] for word in keyword_list]])
        if sub_ontology_filter:
            filtered_nodes = [node for node in filtered_nodes if node.sub_ontology == sub_ontology_filter]
        return filtered_nodes

    def filter_edges(self, filtered_nodes, allowed_relationships=None):
        """Returns a list of edges from a parent graph that involve nodes in the
        filtered nodes list and, if specified, has an allowed relationship type."""
        filtered_edges = [edge for edge in self.edge_list if edge.parent_node in filtered_nodes and edge.child_node in filtered_nodes]
        if allowed_relationships:
            filtered_edges = [edge for edge in filtered_edges if edge.relationship in allowed_relationships]
        return filtered_edges


    def find_all_paths(self, start_node, end_node, direction='parent', allowed_relationships=None, path=[]):    
    #  TODO: Test current find_all_paths and add in options for filtering relationship types
    #  FIXME: This exceeds max recursion depth in python
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


class AbstractNode(object):

    """A node contaning all basic properties of an OBO node. The parser 
    currently has direct access to datamembers."""
    
    def __init__(self):
        self.id = str()
        self.name = str()
        self.definition = str()
        self.edges = list()
        self.parent_node_set = set()
        self.child_node_set = set()
        self.obsolete = False

    def add_edge(self, edge, allowed_relationships):
        """Adds an edge to the node, and updates the node's parent and child 
        sets."""
        self.edges.append(edge)
        self.update_node(edge, allowed_relationships)

    def update_node(self, edge, allowed_relationships=None):
        """Not terribly useful to have this as a separate funciton at the 
        moment. Consider moving"""
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


class AbstractEdge(object):

    """An OBO edge which links two ontology term nodes and contains a 
    relationship type describing now the two nodes are related."""
    
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
