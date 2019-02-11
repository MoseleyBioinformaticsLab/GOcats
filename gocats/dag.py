# !/usr/bin/python3
"""
Contains necessary objects for creating a Directed Acyclic Graph (DAG) object to represent Open Biomedical Ontologies
(OBO).
"""
import re


class OboGraph(object):

    """A pythonic graph of a generic Open Biomedical Ontology (OBO) directed
    acyclic graph (DAG).
    """

    def __init__(self, namespace_filter=None, allowed_relationships=None):
        """`OboGraph` initializer. Leave `namespace_filter` and `allowed_relationship` as :py:obj:`None` to create the
        entire ontology graph. Otherwise, provide filters to limit what information is pulled into the graph.

        :param str namespace_filter: Specify the namespace of a sub-ontology namespace, if one is available for the ontology.
        :param list allowed_relationships: Specify a list of relationships to utilize in the graph, other relationships will be ignored.
        """
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
        """:py:obj:`property` defining a set of nodes in the graph which have no parents. When the graph is modified,
        calls :func:`_update_graph` to repopulate the sets of orphan and leaf nodes.

        :return: Set of 'orphan' :class:`gocats.dag.AbstractNode` objects.
        :rtype: :py:class:`set`
        """
        if self._modified:
            self._update_graph()
        return self._orphans

    @property
    def leaves(self):
        """:py:obj:`property` defining a set of nodes in the graph which have no children. When the graph is modified,
        calls :func:`_update_graph` to repopulate the sets of orphan and leaf nodes.

        :return: Set of 'leaf' :class:`gocats.dag.AbstractNode` objects.
        :rtype: :py:class:`set`
        """
        if self._modified:
            self._update_graph()
        return self._leaves

    def valid_node(self, node):
        """Defines condition of a valid node. Node is valid if it is not obsolete and is contained within the given
        ontology namespace constraint.

        :param node: A :class:`gocats.dag.AbstractNode` object
        :return: True if node is valid, False otherwise
        :rtype: :py:obj:`True` or :py:obj:`False`
        """
        if not node.obsolete and (not self.namespace_filter or node.namespace == self.namespace_filter):
            return True
        return False

    def valid_edge(self, edge):
        """Defines condition of a valid edge. Edge is valid if it is within the list of allowed edges and connects two
        nodes that are both contained in the graph in question.

        :param edge: A :class:`gocats.dag.AbstractEdge` object
        :return: True if node is valid, False otherwise
        :rtype: :py:obj:`True` or :py:obj:`False`
        """
        if (edge.parent_node.id in self.id_index and edge.child_node.id in self.id_index) and (not self.allowed_relationships or edge.relationship_id in self.allowed_relationships):
            return True
        return False

    def _update_graph(self):
        """Repopulates graph orphans and leaves sets.

        :return: None
        :rtype: :py:obj:`None`
        """
        self._orphans = set([node for node in self.node_list if not node.obsolete and not node.parent_node_set and node not in self.root_nodes])
        self._leaves = set([node for node in self.node_list if not node.obsolete and not node.child_node_set and node.parent_node_set])
        self._modified = False

    def add_node(self, node):
        """Adds a node object to the graph, adds an object pointer to the vocabulary index to reference nodes to every
        word in the node name and definition. Sets modification state to :py:obj:`True`.

        :param node: A :class:`gocats.dag.AbstractNode` object.
        :return: None
        :rtype: :py:obj:`None`
        """
        self.node_list.append(node)
        self.id_index[node.id] = node
        for word in re.findall(r"[\w\'\-]+", node.name + " " + node.definition):
            try:
                self.vocab_index[word].add(node)
            except KeyError:
                self.vocab_index[word] = set([node])  # Don't replace with set literal
        self._modified = True

    def remove_node(self, node):
        """Removes a node from the graph and deletes node references from all entries in the vocabulary index. Sets
        modification state to :py:obj:`True`.

        :param node: A :class:`gocats.dag.AbstractNode` object.
        :return: None
        :rtype: :py:obj:`None`
        """
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
        """Adds an edge object to the graph, and counts the edge relationship type. Sets modification state to
        :py:obj:`True`.

        :param edge: A :class:`gocats.dag.AbstractEdge` object.
        :return: None
        :rtype: :py:obj:`None`
        """
        self.edge_list.append(edge)
        try:
            self.relationship_count[edge.relationship_id] += 1
        except KeyError:
            self.relationship_count[edge.relationship_id] = 1
        self._modified = True

    def remove_edge(self, edge):
        """Removes an edge object from the graph, and removes references to that edge from the node objects involved.
        Sets modification state to :py:obj:`True`.

        :param edge: A :class:`gocats.dag.AbstractEdge` object.
        :return: None
        :rtype: :py:obj:`None`
        """
        self.id_index[edge.parent_id].remove_edge(edge)
        self.id_index[edge.child_id].remove_edge(edge)
        self.edge_list.remove(edge)
        self._modified = True

    def add_relationship(self, relationship):
        """Adds a :class:`gocats.dag.AbstractRelationship` object to the graph's relationship index, referenced by
        that relationships ID. Sets modification state to :py:obj:`True`.

        :param relationship: A :class:`gocats.dag.AbstractRelationship` object.
        :return: None
        :rtype: :py:obj:`None`
        """
        self.relationship_index[relationship.id] = relationship
        self._modified = True

    def instantiate_valid_edges(self):
        """Add all edge references to their respective nodes and vice versa if both nodes of the edge are in the graph.
        This is carried out by :func:`AbstractEdge.connect_nodes`. Also adds :class:`gocats.dag.AbstractRelationship`
        object reference to each edge. If both nodes are not in the graph, the edge is deleted from the graph. Sets
        modification state to :py:obj:`True`.

        :return: None
        :rtype: :py:obj:`None`
        """
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
        """Returns an integer representing how many nodes are between the given node and the root node of the graph
        (depth level).

        :param sample_node: A :class:`gocats.dag.AbstractNode` object.
        :return: Depth level.
        :rtype: :py:obj:`int`
        """
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
        list. Nodes are selected by searching through the vocablary index.

        :param search_string_list: A :py:obj:`list` of search strings provided in the keyword_file provided to :func:`gocats.gocats.create_subgraphs`.
        :return: A list of :class:`gocats.dag.AbstractNode` objects.
        :rtype: :py:obj:`list`
        """
        search_string_list_words = [re.findall(self.word_split, word) for word in search_string_list]
        search_string_word_set = set([word for sublist in search_string_list_words for word in sublist])
        filtered_nodes = set.union(*[node_set for node_set in [self.vocab_index[word] for word in search_string_word_set if word in self.vocab_index]])
        if self.namespace_filter:
            filtered_nodes = [node for node in filtered_nodes if node.namespace == self.namespace_filter]
        return filtered_nodes

    def filter_edges(self, filtered_nodes):
        """Returns a list of edges in the graph that connect the nodes provided in the filtered nodes list.

        :param filtered_nodes: List of filtered nodes provided by :func:`filter_nodes`.
        :return: A list of :class:`gocats.dag.AbstractEdge` objects.
        :rtype: :py:obj:`list`
        """
        filtered_edges = [edge for edge in self.edge_list if edge.parent_node in filtered_nodes and edge.child_node in filtered_nodes]
        if self.allowed_relationships:
            filtered_edges = [edge for edge in filtered_edges if edge.relationship_id in self.allowed_relationships]
        return filtered_edges

    def nodes_between(self, start_node, end_node):
        """Returns a set of nodes that occur along all paths between the start node and the end node. If no paths exist,
        an empty set is returned.

        :param start_node: :class:`gocats.dag.AbstractNode` object to start the paths.
        :param end_node: :class:`gocats.dag.AbstractNode` object to end the paths.
        :return: A set of :class:`gocats.dag.AbstractNode` objects if there is at least one path between the parameters, an empty set otherwise.
        :rtype: :py:obj:`set`
        """
        if start_node.ancestors and end_node.descendants:
            return start_node.ancestors.intersection(end_node.descendants)
        else:
            return set()


class AbstractNode(object):

    """A node containing all basic properties of an OBO node. The parsing object, :class:`gocats.ontologyparser.OboParser`
    currently has direct access to data members (id, name, definition, namespace, edges, and obsolete) so that
    information from the database file can be added to the object.
    """

    def __init__(self):
        """`AbstractNode` initializer
        """
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
        """:py:obj:`property` defining a set of nodes in the graph that are recursively reverse of a node with a
        scoping-type relationship. When the node is modified, calls :func:`gocats.dag.AbstractNode._update_node` to
        repopulate the sets of descendants and ancestors. This represents a "lazy" evaluation of node descendants.

        :return: Set of :class:`gocats.dag.AbstractNode` objects
        :rtype: :py:class:`set`
        """
        if self._modified:
            self._update_node()
        return self._descendants

    @property
    def ancestors(self):
        """:py:obj:`property` defining a set of nodes in the graph that are recursively forward of a node with a
        scoping-type relationship. When the node is modified, calls :func:`gocats.dag.AbstractNode._update_node` to
        repopulate the sets of descendants and ancestors. This represents a "lazy" evaluation of node ancestors.

        :return: Set of :class:`gocats.dag.AbstractNode` objects
        :rtype: :py:class:`set`
        """
        if self._modified:
            self._update_node()
        return self._ancestors

    def _update_node(self):
        """Repopulates ancestor and descendant sets for a node. Sets modification state to :py:obj:`True`.

        :return: None
        :rtype: :py:obj:`None`
        """
        self._update_descendants()
        self._update_ancestors()
        self._modified = False

    def add_edge(self, edge, allowed_relationships):
        """Adds a given :class:`gocats.dag.AbstractEdge` to a each :class:`gocats.dag.AbstractNode` objects that the
        edge connects. If there is a filter for the types of relationships allowed, edges with non-allowed relationship
        types are not processed. Sets modification state to :py:obj:`True`.

        :return: None
        :rtype: :py:obj:`None`
        """
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
        """Removes a given :class:`gocats.dag.AbstractEdge` the :class:`gocats.dag.AbstractNode` object. Also removes
        parent or child node references that the edge referenced. Sets modification state to :py:obj:`True`.

        :return: None
        :rtype: :py:obj:`None`
        """
        if edge.child_id == self.id:
            self.parent_node_set.remove(edge.parent_node)
        elif edge.parent_id == self.id:
            self.child_node_set.remove(edge.child_node)
        self.edges.remove(edge)
        self._modified = True

    def _update_descendants(self):
        """Used for the lazy evaluation of graph descendants of the current :class:`gocats.dag.AbstractNode` object.
        Creates internal :py:obj:`set` variable, descendant_set. Iterates through node children until the bottom of the
        graph is reached. The descendant_set is a set of all nodes across all paths encountered from the current node.

        :return: None
        :rtype: :py:obj:`None`
        """
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
        """Used for the lazy evaluation of graph ancestors of the current :class:`gocats.dag.AbstractNode` object.
        Creates internal :py:obj:`set` variable, ancestors_set. Iterates through node parents until the top of the graph
        is reached. The ancestors_set is a set of all nodes across all paths encountered from the current node.

        :return: None
        :rtype: :py:obj:`None`
        """
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

    """An OBO edge which links two ontology term nodes and contains a relationship type describing now the two nodes are
     related.
    """

    def __init__(self, node1_id, node2_id, relationship_id, node_pair=None):
        """`AbstractEdge` initializer. Node pair refers to a :py:obj:`tuple` of :class:`gocats.dag.AbstractNode` objects that are
        connected by the edge. Defaults to :py:obj:`None` and is later populated.

        :param str node1_id: The ID of the first term referenced from the ontology file's relationship line.
        :param str node2_id: The ID of the second term referenced from the ontology file's relationship line.
        :param str relationship_id: The ID of the relationship in the ontology file's relationship line.
        :param tuple node_pair: Default-:py:obj:`None`, provide a :py:obj:`tuple` containing two :class:`gocats.dag.AbstractNode` objects if they are already created and able to be referenced.
        """
        self.node_pair_id = (node1_id, node2_id)
        self.node_pair = node_pair
        self.relationship_id = relationship_id
        self.relationship = None

    @property
    def json_edge(self):
        """:py:obj:`property` which returns a tuple where position 0 is a unique string representation of the edge made by combining the ID of the reverse node and the id of the forward nodes and where position 1 is a list of two node IDs: the reverse and forward node.

        :return: :py:obj:`tuple` of a unique :class:`AbstractEdge` ID and a list of that edge object's reverse and forward node IDs, respectively. Returns an empty :py:obj:str at a position for which there are no forward or reverse nodes in the graph.
        :rtype: :py:obj:`tuple`
        """
        reverse_node_id = self.reverse_node.id
        forward_node_id = self.forward_node.id
        return (str(reverse_node_id+forward_node_id), [reverse_node_id, forward_node_id])

    @property
    def parent_id(self):
        """:py:obj:`property` defining the ID of the node forward of the current :class:`gocats.dag.AbstractEdge`
        object.

        :return: :py:obj:`str` ID of the forward node in the node_pair associated with the edge if the edge's relationship is assigned, :py:obj:`None` otherwise.
        :rtype: :py:obj:`str` or :py:obj:`None`
        """
        if self.relationship:
            return self.relationship.forward(self.node_pair_id)
        return None

    @property
    def child_id(self):
        """:py:obj:`property` defining the ID of the node reverse of the current :class:`gocats.dag.AbstractEdge` object.

        :return: :py:obj:`str` ID of the reverse node in the node_pair associated with the edge if the edge's relationship is assigned, :py:obj:`None` otherwise.
        :rtype: :py:obj:`str` or :py:obj:`None`
        """
        if self.relationship:
            return self.relationship.reverse(self.node_pair_id)
        return None

    @property
    def forward_node(self):
        """:py:obj:`property` defining the :class:`gocats.dag.AbstractNode` object forward of the current
        :class:`gocats.dag.AbstractEdge` object.

        :return: :class:`gocats.dag.AbstractNode` object of the forward node in the node_pair associated with the edge if the edge's relationship is assigned, the node_pair is assigned, and the type of relationship is instantiated by :class:`gocats.dag.DirectionalRelationship` :py:obj:`None` otherwise.
        :rtype: :class:`gocats.dag.AbstractNode` or :py:obj:`None`
        """
        if self.node_pair and self.relationship and type(self.relationship) is DirectionalRelationship:
            return self.relationship.forward(self.node_pair)
        return None

    @property
    def reverse_node(self):
        """:py:obj:`property` defining the :class:`gocats.dag.AbstractNode` object reverse of the current
        :class:`gocats.dag.AbstractEdge` object.

        :return: :class:`gocats.dag.AbstractNode` object of the reverse node in the node_pair associated with the edge if the edge's relationship is assigned, the node_pair is assigned, and the type of relationship is instantiated by :class:`gocats.dag.DirectionalRelationship` :py:obj:`None` otherwise.
        :rtype: :class:`gocats.dag.AbstractNode` or :py:obj:`None`
        """
        if self.node_pair and self.relationship and type(self.relationship) is DirectionalRelationship:
            return self.relationship.reverse(self.node_pair)
        return None

    @property
    def parent_node(self):
        """:py:obj:`property` defining the :class:`gocats.dag.AbstractNode` object forward of the current
        :class:`gocats.dag.AbstractEdge` object. This designation will be unique to scoping-type relationships, although
        this is **not yet specified**.

        :return: :class:`gocats.dag.AbstractNode` object of the forward node in the node_pair associated with the edge if the edge's relationship is assigned, the node_pair is assigned, and the type of relationship is instantiated by :class:`gocats.dag.DirectionalRelationship` :py:obj:`None` otherwise.
        :rtype: :class:`gocats.dag.AbstractNode` or :py:obj:`None`
        """
        if self.relationship:
            return self.relationship.forward(self.node_pair)
        return None

    @property
    def child_node(self):
        """:py:obj:`property` defining the :class:`gocats.dag.AbstractNode` object reverse of the current
        :class:`gocats.dag.AbstractEdge` object. This designation will be unique to scoping-type relationships, although
        this is **not yet specified**.

        :return: :class:`gocats.dag.AbstractNode` object of the reverse node in the node_pair associated with the edge if the edge's relationship is assigned, the node_pair is assigned, and the type of relationship is instantiated by :class:`gocats.dag.DirectionalRelationship` :py:obj:`None` otherwise.
        :rtype: :class:`gocats.dag.AbstractNode` or :py:obj:`None`
        """
        if self.relationship:
            return self.relationship.reverse(self.node_pair)
        return None

    # Will finish these later
    @property
    def actor_node(self):
        """**not yet implemented**

        :return: None
        :rtype: :py:obj:`None`
        """
        return

    @property
    def recipient_node(self):
        """**not yet implemented**

        :return: None
        :rtype: :py:obj:`None`
        """
        return

    @property
    def ordinal_prior_node(self):
        """**not yet implemented**

        :return: None
        :rtype: :py:obj:`None`
        """
        return

    @property
    def ordinal_post_node(self):
        """**not yet implemented**

        :return: None
        :rtype: :py:obj:`None`
        """
        return

    @property
    def other_node(self, node):
        """**not yet implemented**

        :return: None
        :rtype: :py:obj:`None`
        """
        return

    def connect_nodes(self, node_pair, allowed_relationships):
        """Adds the current edge object to the :class:`gocats.dag.AbstractNode` objects that are connected by the edge.
        Populates the node_pair with :class:`gocats.dag.AbstractNode` objects.

        :return: None
        :rtype: :py:obj:`None`
        """
        self.node_pair = node_pair
        node_pair[0].add_edge(self, allowed_relationships)
        node_pair[1].add_edge(self, allowed_relationships)


class AbstractRelationship(object):

    """A relationship as defined by a [typedef] stanza in an OBO ontology and augmented by GOcats to better interpret
    semantic correspondence.
    """

    def __init__(self):
        """`AbstractRelationship` initializer.
        """
        self.id = str()
        self.name = str()
        self.category = str()  # TODO: change category to correspondence_classes DO everywhere.


class DirectionalRelationship(AbstractRelationship):

    """A singly-directional relationship edge connecting two nodes in the graph. The two nodes are designated 'forward'
    and 'reverse.' The 'forward' node semantically succeeds the 'reverse' node in a way that depends on the context of
    the type of relationship describing the edge to which it is applied.
    """

    def __init__(self):
        """`DirectionalRelationship` initializer.
        """
        super().__init__()
        self.inverse_relationship_id = None
        self.inverse_relationship = None
        self.direction = 1  # Defaults as toward node2 (node2 is the 'forward' node)

    def forward(self, pair):
        """Returns the forward node in a node pair that semantically succeeds the other and is independent of the
        directionality of the edge. Default position is the second position [1].

        :param tuple pair: A pair of :class:`gocats.dag.AbstractNode` objects.
        :return: The forward :class:`gocats.dag.AbstractNode` object as determined by the pre-defined semantic directionality of the relationship.
        """
        return pair[self.direction]

    def reverse(self, pair):
        """Returns the reverse node in a node pair that semantically precedes the other and is independent of the
        directionality of the edge. Default position is the second position [1].

        :param tuple pair: A pair of :class:`gocats.dag.AbstractNode` objects.
        :return: The reverse :class:`gocats.dag.AbstractNode` object as determined by the pre-defined semantic directionality of the relationship.
        """
        return pair[(self.direction+1) % 2]


class NonDirectionalRelationship(AbstractRelationship):

    """A non-directional relationship whose edge directionality is either non-existent or semantically irrelevant.
    """
    def __init__(self):
        """`NonDirectionalRelationship` initializer.
        """
        return
