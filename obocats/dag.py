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
        self.relationship_index = dict()
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
        if not node.obsolete and (not self.namespace_filter or node.namespace == self.namespace_filter):
            return True
        return False

    def valid_edge(self, edge):
        if (edge.parent_node.id in self.id_index and edge.child_node.id in self.id_index) and (not self.allowed_relationships or edge.relationship_id in self.allowed_relationships):
            return True
        return False

    def _update_graph(self):
        self._orphans = set([node for node in self.node_list if not node.obsolete and not node.parent_node_set and node not in self.root_nodes])
        self._leaves = set([node for node in self.node_list if not node.obsolete and not node.child_node_set and node.parent_node_set])
        self._modified = False

    def add_node(self, node):
        self.node_list.append(node)
        self.id_index[node.id] = node
        for word in re.findall(r"[\w'-]+", node.name + " " + node.definition):
            try:
                self.vocab_index[word].add(node)
            except KeyError:
                self.vocab_index[word] = set([node])
        self._modified = True

    def remove_node(self, node):
        if node not in self.node_list:
            pass  # The node has already been removed, or has not been added
        else:
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
        self._modified = True

    def add_edge(self, edge):
        self.edge_list.append(edge)
        self._modified = True

    def remove_edge(self, edge):
        self.id_index[edge.parent_id].remove_edge(edge)
        self.id_index[edge.child_id].remove_edge(edge)
        self.edge_list.remove(edge)
        self._modified = True

    def add_relationship(self, relationship):
        self.relationship_index[relationship.id] = relationship
        self.modified = True

    def connect_nodes(self):
        for edge in self.edge_list:
            edge.relationship = self.relationship_index[edge.relationship_id]
            edge.connect_nodes((self.id_index[edge.node_pair_id[0]], self.id_index[edge.node_pair_id[1]]), self.allowed_relationships)
        self._modified = True

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
            filtered_edges = [edge for edge in filtered_edges if edge.relationship_id in self.allowed_relationships]
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
        # new sets for equilavalece, actor/actee, ordinal, etc
        
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
        self._update_descendants()
        self._update_ancestors()
        self._modified = False

    def add_edge(self, edge, allowed_relationships):
        self.edges.add(edge)
        if not allowed_relationships:
            if edge.child_id == self.id:
                self.parent_node_set.add(edge.parent_node)
            elif edge.parent_id == self.id:
                self.child_node_set.add(edge.child_node)
        else:
            if edge.child_id == self.id and edge.relationship_id in allowed_relationships:
                self.parent_node_set.add(edge.parent_node)
            elif edge.parent_id == self.id and edge.relationship_id in allowed_relationships:
                self.child_node_set.add(edge.child_node)
        self._modified = True

    def remove_edge(self, edge):
        if edge.child_id == self.id:
            self.parent_node_set.remove(edge.parent_node)
        elif edge.parent_id == self.id:
            self.child_node_set.remove(edge.child_node)
        self.edges.remove(edge)
        self._modified = True

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
    
    def __init__(self, node1_id, node2_id, relationship_id, node_pair=None):
        self.node_pair_id = (node1_id, node2_id)
        self.node_pair = node_pair
        self.relationship_id = relationship_id
        self.relationship = None

    @property
    def parent_id(self):
        if self.relationship :
            return self.relationship.forward(self.node_pair_id)
        return None


    @property
    def child_id(self):
        if self.relationship :
            return self.relationship.reverse(self.node_pair_id)
        return None

    @property
    def forward_node(self):
        if self.node_pair and self.relationship and type(self.relationship) is DirectionalRelationship :
            return self.relationship_forward(self.node_pair) 
        return None

    @property
    def reverse_node(self):
        if self.node_pair and self.relationship and type(self.relationship) is DirectionalRelationship :
            return self.relationship_reverse(self.node_pair) 
        return None
    
    @property
    def parent_node(self):
        if self.relationship and self.relationship.category == "scoping" :
            return self.relationship_forward(self.node_pair) 
        return None

    @property
    def child_node(self):
        if self.relationship and self.relationship.category == "scoping" :
            return self.relationship_reverse(self.node_pair) 
        return None

    @property
    #to finish later
    def other_node(self, node):
        return

    def connect_nodes(self, node_pair, allowed_relationships):
        self.node_pair = node_pair
        node_pair[0].add_edge(self, allowed_relationships)
        node_pair[1].add_edge(self, allowed_relationships)


class AbstractRelationship(object):

    """A relationship as defined by a [typedef] stanza in an OBO ontology"""

    def __init__(self):
        self.id = str()
        self.name = str()
        self.category = str()


class DirectionalRelationship(AbstractRelationship):

    """A relationship as defined by a [typedef] stanza in an OBO ontology"""

    def __init__(self):
        super().__init__()
        self.inverse_relationship_id = None
        self.inverse_relationship = None
        self.direction = 1

    def forward(self,pair):
        return pair[self.direction]

    def reverse(self,pair):
        return pair[(self.direction+1) % 2]