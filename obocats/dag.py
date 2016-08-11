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
        for word in re.findall(r"[\w'-]+", node.name + " " + node.definition):
            try:
                self.vocab_index[word.lower()].add(node)
            except KeyError:
                self.vocab_index[word.lower()] = set([node])

    def add_edge(self, edge):
        self.edge_list.append(edge)

    def connect_nodes(self, allowed_relationships=None):
        for edge in self.edge_list:
            edge.parent_node = self.id_index[edge.parent_id]
            edge.child_node = self.id_index[edge.child_id]
            self.id_index[edge.parent_id].add_edge(edge, allowed_relationships)
            self.id_index[edge.child_id].add_edge(edge, allowed_relationships)

    def filter_nodes(self, keyword_list, sub_ontology_filter=None):
        filtered_nodes = set.union(*[node_set for node_set in [self.vocab_index[word] for word in keyword_list]])
        if sub_ontology_filter:
            filtered_nodes = [node for node in filtered_nodes if node.sub_ontology == sub_ontology_filter]
        return filtered_nodes

    def filter_edges(self, filtered_nodes, allowed_relationships=None):
        filtered_edges = [edge for edge in self.edge_list if edge.parent_node in filtered_nodes and edge.child_node in filtered_nodes]
        if allowed_relationships:
            filtered_edges = [edge for edge in filtered_edges if edge.relationship in allowed_relationships]
        return filtered_edges


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
