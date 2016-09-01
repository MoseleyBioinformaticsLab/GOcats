# !/usr/bin/python3
import re


class OboGraph(object):

    """A pythonic graph of a generic Open Biomedical Ontology (OBO) directed 
    acyclic graph (DAG)"""

    def __init__(self, namespace_filter=None, allowed_relationships=None):
        self.namespace_filter = namespace_filter
        self.allowed_relationships = allowed_relationships
        self.node_list = list()
        self.edge_list = list()
        self.id_index = dict()
        self.vocab_index = dict() 
        self.used_relationship_set = set()  
        self.root_nodes = list()
        self._orphans = None
        self._leaves = None
        self._modified = True

        if self.allowed_relationships:
            if 'is_a' not in self.allowed_relationships:
                print("WARNING: 'is_a' is a required relationship type within OBO ontologies.\nAdding 'is_a' to the allowed_relationships list.")
                self.allowed_relationships.append('is_a')

    @property
    def orphans(self):
        if self._modified:
            self._update_graph()
        return self._orphans

    @property
    def leaves(self):
        if self._modified:
            self._update_graph()
        return self._leaves
    
    def valid_node(self, node):
        # Filter here for obsolete?
        if not self.namespace_filter:
            return True
        elif node.namespace == self.namespace_filter:
            return True
        else:
            return False

    def valid_relationship(self, edge):
        if not self.allowed_relationships:
            return True
        elif edge.relationship in self.allowed_relationships:
            return True
        else:
            return False

    def valid_edge(self, edge):
        if edge.parent_node.id in self.id_index and edge.child_node.id in self.id_index:
            return True
        else:
            return False

    def _update_graph(self):
        self._modified = False
        self._orphans = set([node for node in self.node_list if not node.obsolete and not node.parent_node_set and node not in self.root_nodes])
        self._leaves = set([node for node in self.node_list if not node.obsolete and not node.child_node_set])

    def add_node(self, node):
        self._modified = True
        self.node_list.append(node)
        self.id_index[node.id] = node
        for word in re.findall(r"[\w'-]+", node.name + " " + node.definition):
            try:
                self.vocab_index[word].add(node)
            except KeyError:
                self.vocab_index[word] = set([node])

    def remove_node(self, node):
        for graph_node in self.node_list:
            if node in graph_node.parent_node_set:
                graph_node.parent_node_set.remove(node)
            elif node in graph_node.child_node_set:
                graph_node.child_node_set.remove(node)
            for edge in graph_node.edges:
                if node is edge.parent_node or node is edge.child_node:
                    graph_node.edges.remove(edge)                    
        for word in re.findall(r"[\w'-]+", node.name + " " + node.definition):
            try:
                self.vocab_index[word].remove(node)
            except KeyError:
                pass
            else:
                if not self.vocab_index[word]:
                    del self.vocab_index[word]
        del self.id_index[node.id]
        self.node_list.remove(node)

    def add_edge(self, edge):
        self._modified = True
        self.edge_list.append(edge)

    def remove_edge(self, edge):
        self._modified = True
        self.id_index[edge.parent_id].remove_edge(edge)
        self.id_index[edge.child_id].remove_edge(edge)
        self.edge_list.remove(edge)

    def connect_nodes(self):
        self._modified = True
        for edge in self.edge_list:
            edge.parent_node = self.id_index[edge.parent_id]
            edge.child_node = self.id_index[edge.child_id]
            self.id_index[edge.parent_id].add_edge(edge, self.allowed_relationships)
            self.id_index[edge.child_id].add_edge(edge, self.allowed_relationships)

    def filter_nodes(self, keyword_list):
        for word in keyword_list:
            if word not in self.vocab_index.keys():
                keyword_list.remove(word)
        filtered_nodes = set.union(*[node_set for node_set in [self.vocab_index[word] for word in keyword_list]])
        if self.namespace_filter:
            filtered_nodes = [node for node in filtered_nodes if node.namespace == self.namespace_filter]
        return filtered_nodes

    def filter_edges(self, filtered_nodes):
        filtered_edges = [edge for edge in self.edge_list if edge.parent_node in filtered_nodes and edge.child_node in filtered_nodes]
        if self.allowed_relationships:
            filtered_edges = [edge for edge in filtered_edges if edge.relationship in self.allowed_relationships]
        return filtered_edges

    def nodes_between(self, start_node, end_node):
        if start_node.ancestors and end_node.descendants:
            return start_node.ancestors.intersection(end_node.descendants)
        else:
            return set()


class AbstractNode(object):

    """A node contaning all basic properties of an OBO node. The parser 
    currently has direct access to datamembers (id, name, definition, 
    namespace, edges, and obsolete)."""
    
    def __init__(self):
        self.id = str()
        self.name = str()
        self.definition = str()
        self.namespace = str()
        self.edges = set()
        self.parent_node_set = set()
        self.child_node_set = set()
        self.obsolete = False
        self._modified = True
        self._descendants = None
        self._ancestors = None

    @property
    def descendants(self):
        if self._modified:
            self._update_node()
        return self._descendants

    @property
    def ancestors(self):
        if self._modified:
            self._update_node()
        return self._ancestors
    
    def _update_node(self):
        self._modified = False
        self._update_descendants()
        self._update_ancestors()

    def add_edge(self, edge, allowed_relationships):
        self._modified = True
        self.edges.add(edge)
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

    def remove_edge(self, edge):
        self._modified = True
        if edge.child_id == self.id:
            self.parent_node_set.remove(edge.parent_node)
        elif edge.parent_id == self.id:
            self.child_node_set.remove(edge.child_node)
        self.edges.remove(edge)

    def _update_descendants(self):
        descendant_set = set()
        children = list(self.child_node_set) 
        while len(children) > 0:
            child = children[0]
            descendant_set.add(child)
            if not child._modified:
                descendant_set.update(child._descendants)
            else:
                children.extend([new_child for new_child in child.child_node_set if new_child not in descendant_set and new_child not in children])
            children.remove(child)
        self._descendants = descendant_set

    def _update_ancestors(self):
        ancestors_set = set()
        parents = list(self.parent_node_set)
        while len(parents) > 0:
            parent = parents[0]
            ancestors_set.add(parent)
            if not parent._modified:
                ancestors_set.update(parent._ancestors)
            else:
                parents.extend([new_parent for new_parent in parent.parent_node_set if new_parent not in ancestors_set and new_parent not in parents])
            parents.remove(parent)
        self._ancestors = ancestors_set


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
        else:
            return self._parent_id

    @parent_id.setter
    def parent_id(self, new_parent):
        self._parent_id = new_parent

    @property
    def child_id(self):
        if self.child_node :
            return self.child_node.id
        else:
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
