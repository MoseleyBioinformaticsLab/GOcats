# !/usr/bin/python3
import re


class OboGraph(object):

    """A pythonic graph of a generic Open Biomedical Ontology (OBO) directed 
    acyclic graph (DAG)."""

    def __init__(self, namespace_filter=None, allowed_relationships=None):
        self.namespace_filter = namespace_filter
        self.allowed_relationships = allowed_relationships
        self.word_split = re.compile(r"[\w\'\-]+")
        self.node_list = list()
        self.edge_list = list()
        self.id_index = dict()
        self.vocab_index = dict()
        self.relationship_index = dict()
        self.used_relationship_set = set()
        self.relationship_count = dict()
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
        """A set of nodes in the graph which have no parents."""
        if self._modified:
            self._update_graph()
        return self._orphans

    @property
    def leaves(self):
        """A set of nodes in the graph which have no children."""
        if self._modified:
            self._update_graph()
        return self._leaves
    
    def valid_node(self, node):
        """Returns True if a node is not obsolete and is contained within the given ontology namespace contraint."""
        if not node.obsolete and (not self.namespace_filter or node.namespace == self.namespace_filter):
            return True
        return False

    def valid_edge(self, edge):
        """Returns True if an edge is within the list of allowed edges and connects two nodes that are both contained in
        the graph in question."""
        if (edge.parent_node.id in self.id_index and edge.child_node.id in self.id_index) and (not self.allowed_relationships or edge.relationship_id in self.allowed_relationships):
            return True
        return False

    def _update_graph(self):
        """Repopulates graph orphans and leaves."""
        self._orphans = set([node for node in self.node_list if not node.obsolete and not node.parent_node_set and node not in self.root_nodes])
        self._leaves = set([node for node in self.node_list if not node.obsolete and not node.child_node_set and node.parent_node_set])
        self._modified = False

    def add_node(self, node):
        """Adds a node object to the graph, adds an object pointer to the vocabulary index to reference nodes to every
        word in the node name and definition."""
        self.node_list.append(node)
        self.id_index[node.id] = node
        for word in re.findall(r"[\w\'\-]+", node.name + " " + node.definition):
            try:
                self.vocab_index[word].add(node)
            except KeyError:
                self.vocab_index[word] = set([node])
        self._modified = True

    def remove_node(self, node):
        """Removes a node from the graph and deletes node references from all entries in the vocabulary index."""
        if node not in self.node_list:
            pass
        else:
            for graph_node in self.node_list:
                if node in graph_node.parent_node_set:
                    graph_node.parent_node_set.remove(node)
                elif node in graph_node.child_node_set:
                    graph_node.child_node_set.remove(node)
                for edge in graph_node.edges:
                    if node is edge.parent_node or node is edge.child_node:
                        graph_node.edges.remove(edge)                    
            for word in re.findall(r"[\w\'\-]+", node.name + " " + node.definition):
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
        try:
            self.relationship_count[edge.relationship_id] += 1
        except KeyError:
            self.relationship_count[edge.relationship_id] = 1
        self._modified = True

    def remove_edge(self, edge):
        self.id_index[edge.parent_id].remove_edge(edge)
        self.id_index[edge.child_id].remove_edge(edge)
        self.edge_list.remove(edge)
        self._modified = True

    def add_relationship(self, relationship):
        self.relationship_index[relationship.id] = relationship
        self.modified = True

    def instantiate_valid_edges(self):
        """Instatntiate edge if both nodes of the edge are in the graph. Searches by node id because node objects are
        not referenced at the edges at the time this method is called."""
        del_edges = set()
        for edge in self.edge_list:
            if edge.node_pair_id[0] in self.id_index.keys() and edge.node_pair_id[1] in self.id_index.keys():
                edge.relationship = self.relationship_index[edge.relationship_id]
                edge.connect_nodes((self.id_index[edge.node_pair_id[0]], self.id_index[edge.node_pair_id[1]]), self.allowed_relationships)
            else:
                del_edges.add(edge)
        for edge in del_edges:
            self.edge_list.remove(edge)

        self._modified = True

    def node_depth(self, sample_node):
        """Returns an integer representative of how many nodes are between the given node and the root node of the
        graph."""
        if sample_node in self.root_nodes:
            return 0
        depth = 1
        root_node_set = set(self.root_nodes)
        parent_set = sample_node.parent_node_set
        while parent_set:
            if parent_set & root_node_set:  # There is an intersection between the parent set and the root_node_set
                break
            depth += 1
            parent_set = set().union(*[parent.parent_node_set for parent in parent_set])
        return depth

    def filter_nodes(self, search_string_list):
        """Returns a list of node objects that contain vocabulary matching the keywords provided in the search string
        list. Nodes are selected by searching through the vocablary index."""
        search_string_list_words = [re.findall(self.word_split, word) for word in search_string_list]
        search_string_word_set = set([word for sublist in search_string_list_words for word in sublist])
        filtered_nodes = set.union(*[node_set for node_set in [self.vocab_index[word] for word in search_string_word_set if word in self.vocab_index]])
        if self.namespace_filter:
            filtered_nodes = [node for node in filtered_nodes if node.namespace == self.namespace_filter]
        return filtered_nodes

    def filter_edges(self, filtered_nodes):
        """Returns a list of edges in the graph that connect the nodes provided in the filtered nodes list."""
        filtered_edges = [edge for edge in self.edge_list if edge.parent_node in filtered_nodes and edge.child_node in filtered_nodes]
        if self.allowed_relationships:
            filtered_edges = [edge for edge in filtered_edges if edge.relationship_id in self.allowed_relationships]
        return filtered_edges
 
    def nodes_between(self, start_node, end_node):
        """Returns a set of nodes that occur along all paths between the start node and the end node. If no paths exist,
        an empty set is returned."""
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
        # Will add new sets for equivalence, actor/actee, ordinal, etc
        
    @property
    def descendants(self):
        """Returns the set of nodes that are recursively forward of a node with a scoping-type relationship."""
        if self._modified:
            self._update_node()
        return self._descendants

    @property
    def ancestors(self):
        """Returns set of nodes that are recursively reverse of a node with a scoping-type relationship."""
        if self._modified:
            self._update_node()
        return self._ancestors
    
    def _update_node(self):
        """Repopulates ancestor and descendent sets for a node."""
        self._update_descendants()
        self._update_ancestors()
        self._modified = False

    def add_edge(self, edge, allowed_relationships):
        """Adds a given edge to the node's edge list and sets parent and child nodes given the edge represents an
        allowed relationship."""
        # TODO: Need to capture non-parent/child relationship types, such as actor/actee and equivalence
        # FIXME: Should we add edges that represent non-allowed relationships?
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
        """Returns the ID of a node which is forward with respect to the edge."""
        if self.relationship:
            return self.relationship.forward(self.node_pair_id)
        return None

    @property
    def child_id(self):
        """Returns the ID of a node which is reverse with resepct to the edge."""
        if self.relationship:
            return self.relationship.reverse(self.node_pair_id)
        return None

    @property
    def forward_node(self):
        """Returns the node object which is forward with respect to the edge."""
        if self.node_pair and self.relationship and type(self.relationship) is DirectionalRelationship:
            return self.relationship.forward(self.node_pair) 
        return None

    @property
    def reverse_node(self):
        """Returns the node object which is reverse with respect to the edge."""
        if self.node_pair and self.relationship and type(self.relationship) is DirectionalRelationship:
            return self.relationship.reverse(self.node_pair) 
        return None
    
    @property
    def parent_node(self):
        """Returns the node object with is forward with respect to the edge in scoping-type relationsihps."""
        if self.relationship:
            return self.relationship.forward(self.node_pair)
        return None

    @property
    def child_node(self):
        """Returns the node object with is reverse with respect to the edge in scoping-type relationsihps."""
        if self.relationship:
            return self.relationship.reverse(self.node_pair) 
        return None

    # Will finish these later
    @property
    def actor_node(self):
        return

    @property
    def recipient_node(self):
        return

    @property
    def ordinal_prior_node(self):
        return

    @property
    def ordinal_post_node(self):
        return

    @property
    def other_node(self, node):
        return

    def connect_nodes(self, node_pair, allowed_relationships):
        """Adds the edge object to the node objects (node pair) that are connected by the edge."""
        self.node_pair = node_pair
        node_pair[0].add_edge(self, allowed_relationships)
        node_pair[1].add_edge(self, allowed_relationships)


class AbstractRelationship(object):

    """A relationship as defined by a [typedef] stanza in an OBO ontology and augmented by GOcats to better interpret
    semantic correspondence."""

    def __init__(self):
        self.id = str()
        self.name = str()
        self.category = str()  # TODO: change category to correspondence_classes DO everywhere.


class DirectionalRelationship(AbstractRelationship):

    """A singly-directional relationship edge connecting two nodes in the graph. The two nodes are designated 'forward'
    and 'reverse.' The 'forward' node semantically supercedes the 'reverse' node in a way that depends on the context of
    the type of relationship describing the edge to which it is applied."""

    def __init__(self):
        super().__init__()
        self.inverse_relationship_id = None
        self.inverse_relationship = None
        self.direction = 1  # Defaults as toward node2 (node2 is the 'forward' node)

    def forward(self, pair):
        """Returns the tuple position of the node in a node pair that semantically supercedes the other and is
        independent of the directionality of the edge. Default position is 1."""
        return pair[self.direction]

    def reverse(self, pair):
        """Returns the tuple position of the node in a node pair that semantically subcedes the other and is independent
         of the directionality of the edge. Default position is 1."""
        return pair[(self.direction+1) % 2]


class NonDirectionalRelationship(AbstractRelationship):

    """A non-directional relationship whose edge directionality is either non-existant or semantically irrelevant."""
    
    def __init__(self):
        return    
