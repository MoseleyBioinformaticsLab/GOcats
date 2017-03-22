# !/usr/bin/python3
"""
A subgraph object of an OBOGraph object.
"""
from .dag import OboGraph, AbstractNode
import re


class SubGraph(OboGraph):

    """A subgraph of a provided supergraph with node contents."""
    
    def __init__(self, super_graph, namespace_filter=None, allowed_relationships=None):
        """`SubGraph initializer. Creates a subgraph object of :class:`gocats.dag.OboGraph`. Leave `namespace_filter`
        and `allowed_relationship` as :py:obj:`None` to create the entire ontology graph. Otherwise, provide filters to
        limit what information is pulled into the subgraph.

        :param obj super_graph: A supergraph object i.e. :class:`gocats.godag.GoGraph`.
        :param str namespace_filter: Specify the namespace of a sub-ontology namespace, if one is available for the ontology.
        :param list allowed_relationships: Specify a list of relationships to utilize in the graph, other relationships will be ignored.
        """
        self.super_graph = super_graph
        if self.super_graph.namespace_filter and self.super_graph.namespace_filter != namespace_filter:
            raise Exception("Unless a namespace_filter is not specified for a parent_graph, a subgraph's namespace_filter must not differ from its parent graph's namespace_filter.\nsubgraph namespace_filter = {}, supergraph namespace_filter = {}").format(namespace_filter, self.super_graph.namespace_filter)
        if self.super_graph.allowed_relationships and allowed_relationships and any(relationship not in self.super_graph.allowed_relationships for relationship in allowed_relationships):
            raise Exception("Unless an allowed_relationships list is not specified for a parent graph, a subgraph's allowed_relationships list must be a subset of, or exactly, its parent graph's allowed_relationships list.\nsubgraph allowed_relationships = {}, supergraph allowed_relationships = {}").format(allowed_relationships, self.super_graph.allowed_relationships)
        super().__init__(namespace_filter, allowed_relationships)
        self.seeded_size = None  # The number of nodes filtered in the keyword search, used for informational purposes only. 
        self.representative_node = None
        self._root_id_mapping = None
        self._root_node_mapping = None
        self._content_mapping = None

    @property
    def root_id_mapping(self):
        """Property describing a mapping :py:obj:`dict` that relates every ontology term ID of subgraphs in
        :class:`gocats.dag.OboGraph` to a :py:obj:`list` of root, subgraph category-representative node IDs.

        :return: :py:obj:`dict` of :class:`gocats.dag.AbstractNode` IDs mapped to a :py:obj:`list` of root :class:`gocats.dag.AbstractNode` IDs.
        :rtype: :py:obj:`dict`
        """
        if (self._modified and self.representative_node) or self._root_id_mapping is None:
            self._root_id_mapping = {node.id: self.representative_node.id for node in self.representative_node.descendants}
            self._root_id_mapping[self.representative_node.id] = self.representative_node.id
        elif not self.representative_node:
            raise Exception("Mapping failed: top-node not identified.")
        return self._root_id_mapping

    @property
    def root_node_mapping(self):
        """Property describing a mapping :py:obj:`dict` that relates every ontology :class:`gocats.dag.AbstractNode`
        object of subgraphs in :class:`gocats.dag.OboGraph` to a :py:obj:`list` of root, subgraph
        category-representative node objects.

        :return: :py:obj:`dict` of :class:`gocats.dag.AbstractNode` objects mapped to a :py:obj:`list` of root :class:`gocats.dag.AbstractNode` objects.
        :rtype: :py:obj:`dict`
        """
        if (self._modified and self.representative_node) or self._root_node_mapping is None:
            self._root_node_mapping = {node: self.representative_node for node in self.representative_node.descendants}
            self._root_node_mapping[self.representative_node] = self.representative_node
        elif not self.representative_node:
            raise Exception("Mapping failed: top-node not identified.")
        return self._root_node_mapping

    @property
    def content_mapping(self):
        """Property describing a mapping :py:obj:`dict` that relates every root ontology
        :class:`gocats.dag.AbstractNode` IDs of subgraphs in a :class:`gocats.dag.OboGraph` to a :py:obj:`list` of their
        subgraph nodes' IDs.

        :return: :py:obj:`dict` of :class:`gocats.dag.AbstractNode` IDs mapped to a :py:obj:`list' of :class:`gocats.dag.AbstractNode` IDs.
        :rtype: :py:obj:`dict`
        """
        if (self._modified and self.representative_node) or self._content_mapping is None:
            self._content_mapping = {self.representative_node.id: [node.id for node in self.representative_node.descendants]}
            self._content_mapping[self.representative_node.id].append(self.representative_node.id)
        elif not self.representative_node:
            raise Exception("Mapping failed: top-node not identified.")
        return self._content_mapping

    def subnode(self, super_node):
        """Defines a :class:`gocats.subdag.SubGraph` node object. Calls :func:`add_node` to convert a supergraph node
        into a :class:`gocats.subdag.SubGraphNode` and add this node to the subgraph.

        :param super_node: A node object from the supergraph i.e. :class:`gocats.godag.GoGraphNode`.
        :return: A :class:`gocats.subdag.SubGraphNode` object.
        :rtype: :py:obj:`class`
        """
        if super_node.id not in self.id_index:
            self.add_node(super_node)
        return self.id_index[super_node.id]

    def add_node(self, super_node):
        """Converts a supergraph node into a :class:`gocats.subdag.SubGraphNode` and adds this node to the subgraph.
        Sets modification state to :py:obj:`True`.

        :param obj super_node: A node object from the supergraph i.e. :class:`gocats.godag.GoGraphNode`.
        :return: None
        :rtype: :py:obj:`None`
        """
        subgraph_node = SubGraphNode(super_node, self.allowed_relationships)
        if self.valid_node(subgraph_node):
            super().add_node(subgraph_node)
        self._modified = True

    # TODO: Rename/reconsider this (needs to be similar to instantiate_valid_edges)
    def connect_subnodes(self):
        """Analogous to :func:`gocats.dag.instantiate_valid_edges` and :func:`gocats.dag.AbstractEdge.connect_nodes`.
        Updates child and parent node sets for each :class:`gocats.subdag.SubGraphNode` in the
        :class:`gocats.subdag.SubGraph`. Adds edge object references to nodes and node object references to edges.
        Counts instances of relationship IDs and sets modification state to :py:obj:`True`.

        :return: None
        :rtype: :py:obj:`None`
        """
        for subnode in self.node_list:
            subnode.update_children([self.id_index[child.id] for child in subnode.super_node.child_node_set if child.id in self.id_index])
            subnode.update_parents([self.id_index[parent.id] for parent in subnode.super_node.parent_node_set if parent.id in self.id_index])
            for edge in subnode.super_node.edges:  # This counts the number of times each relationship type is used in a subgraph
                if edge.forward_node.id in self.id_index and edge.reverse_node.id in self.id_index:
                    try:
                        self.relationship_count[edge.relationship.id] += 1
                    except KeyError:
                        self.relationship_count[edge.relationship.id] = 1
        self._modified = True

    def greedily_extend_subgraph(self):
        """Extends a seeded subgraph to include all supergraph descendants of the nodes. Searches through the supergraph
        to add new node objects.

        :return: None
        :rtype: :py:obj:`None`
        """
        graph_extension_nodes = set([super_node for super_node in self.super_graph.id_index[self.representative_node.id].descendants if super_node.id not in self.id_index])
        for super_node in graph_extension_nodes:
            self.add_node(super_node)
        self.connect_subnodes()
    
    def conservatively_extend_subgraph(self):
        """Extends a seeded subgraph to include only nodes in the supergraph that occur along paths between nodes in the
        subgraph. Searches through the supergraph to add new node objects.

        :return: None
        :rtype: :py:obj:`None`
        """
        graph_extension_nodes = set()
        for subleaf in self.leaves:
            start_node = self.super_graph.id_index[subleaf.id]
            end_node = self.super_graph.id_index[self.representative_node.id]
            graph_extension_nodes.update(self.nodes_between(start_node, end_node))
        for super_node in graph_extension_nodes:
            if super_node.id not in self.id_index and self.valid_node(super_node):
                self.add_node(super_node)
        self.connect_subnodes()

    def remove_orphan_paths(self):
        """**Not currently in use.**

        Removes nodes and their descendants from the subgraph which do not root to the
        category-representative node.

        :return: None
        :rtype: :py:obj:`None`
        """
        for orphan in self.orphans:
            orphaned_descendants = orphan.descendants - self.representative_node.descendants
            if orphaned_descendants:
                for descendant in orphaned_descendants:
                    self.remove_node(descendant)
            self.remove_node(orphan)

    @staticmethod
    def find_representative_node(subgraph, search_string_list):
        """Extracts candidate :class:`gocats.subdag.SubGraphNode` objects from the :class:`gocats.subdag.SubGraph`
        objects based on a list of search strings matching strings in the names of the nodes (using regular
        expressions). Returns the candidate node with the highest number of descendants. Returns the sole node if the
        subgraph only contains one node, aborts if the subgraph is empty.

        :param subgraph: A :class:`gocats.subdag.SubGraph` object.
        :param search_string_list: A :py:obj:`list` of search term :py:obj:`str` entries.
        :return: A candidate term :class:`gocats.subgraph.SubGraphNode` chosen as the subgraph's representative ontology term.
        """
        if len(subgraph.node_list) == 1:
            return subgraph.node_list[0]
        elif not subgraph.node_list:
            raise Exception("Subgraph did not seed any nodes from the supergraph! Aborting.")
        else:
            candidates = [node for node in subgraph.node_list if any(re.search('(?<!\-)'+search_string+'(?!\-)', node.name) for search_string in search_string_list) and node not in subgraph.leaves and not node.obsolete] 
            representative_node_scoring = {node: len(node.descendants) for node in candidates}
            return max(representative_node_scoring, key=representative_node_scoring.get)

    @staticmethod
    def from_filtered_graph(super_graph, keyword_list, namespace_filter=None, allowed_relationships=None, extension='greedy'):
        """Staticmethod for extracting a subgraph from the supergraph by selecting nodes that contain vocabulary in the
        supplied keyword list. Leave `namespace_filter` and `allowed_relationship` as :py:obj:`None` to create the
        entire ontology graph. Otherwise, provide filters to limit what information is pulled into the subgraph.
        Graph `extension` variable defaults to 'greedy' which calls :func:`greedily_extend_subgraph` to add nodes to the
        subgraph after instantiation. Conversely, 'conservative' may be used to call
        :func:`conservatively_extend_subgraph` for this function.

        :param obj super_graph: A supergraph object i.e. :class:`gocats.godag.GoGraph`.
        :param keyword_list: A :py:obj:`list` of :py:obj:`str` entries used to query the supergraph for concepts to be extracted into subgraphs.
        :param str namespace_filter: Specify the namespace of a sub-ontology namespace, if one is available for the ontology.
        :param list allowed_relationships: Specify a list of relationships to utilize in the graph, other relationships will be ignored.
        :param str extension: Specify 'greedy' or 'conservative' to determine how subgraphs will be extended after creation (defaults to greedy).
        :return: A :class:`gocats.subdag.SubGraph` object.
        """
        subgraph = SubGraph(super_graph, namespace_filter, allowed_relationships)
        keyword_list = [word.lower() for word in keyword_list]
        filtered_nodes = super_graph.filter_nodes(keyword_list)
        subgraph.seeded_size = len(filtered_nodes)
        for super_node in filtered_nodes:
            subgraph.add_node(super_node)
        subgraph.connect_subnodes()
        subgraph.representative_node = subgraph.find_representative_node(subgraph, keyword_list)
        subgraph.root_nodes.append(subgraph.representative_node)
        if extension == 'greedy':
            subgraph.greedily_extend_subgraph()
        elif extension == 'conservative':
            subgraph.conservatively_extend_subgraph()
        subgraph_orphans_descendants = set()
        for orphan in subgraph.orphans:
            for node in orphan.descendants:
                subgraph_orphans_descendants.add(node)
        subgraph_orphans_descendants.update([orphan for orphan in subgraph.orphans])
            
        return subgraph


class SubGraphNode(AbstractNode):

    """An instance of a node within a subgraph of an OBO ontology (supergraph)
    """
    
    def __init__(self, super_node, allowed_relationships=None):
        """SubGraphNode initializer. Inherits from :class:`gocats.dag.AbstractNode` and contains a reference to the
        supergraph node it represents e.g. :class:`gocats.godag.GoGraphNode`.

        :param super_node: A node from the `supergraph`.
        :param allowed_relationships: **Not currently used** Used to specify a list of allowable relationships evaluated between nodes.
        """
        self.super_node = super_node
        self.parent_node_set = set()
        self.child_node_set = set()
        self._modified = True
        self._descendants = None
        self._ancestors = None

    # TODO: add in update_parent_node_set and update_child_node_set with a _modified switch !!!!

    @property
    def super_edges(self):
        """:py:obj:`property` describing the set of edges referenced in the supergraph node, filtered to only those
         edges with nodes in the subgraph node.

        :return: A set of :class:`gocats.subgraph.SubGraphNode` edges that were copied from the supergraph node.
        :rtype: :py:obj:`set`
        """
        edges = set()
        edges.add([edge for edge in self.super_node.edges if edge.parent_node.id in [node.id for node in self.parent_node_set] and edge.child_node.id in [node.id for node in self.child_node_set]])
        return edges

    @property
    def id(self):
        """:py:obj:`property` describing the ID of the supernode

        :return: The ID of a supernode e.g. :class:`gocats.godag.GoGraphNode`
        :rtype: :py:obj:`str`
        """
        return self.super_node.id

    @property
    def name(self):
        """:py:obj:`property` describing the name of the supernode

        :return: The name of a supernode e.g. :class:`gocats.godag.GoGraphNode`
        :rtype: :py:obj:`str`
        """
        return self.super_node.name
    
    @property
    def definition(self):
        """:py:obj:`property` describing the definition of the supernode

        :return: The definition of a supernode e.g. :class:`gocats.godag.GoGraphNode`
        :rtype: :py:obj:`str`
        """
        return self.super_node.definition

    @property
    def namespace(self):
        """:py:obj:`property` describing the namespace of the supernode

        :return: A namespace of a supernode e.g. :class:`gocats.godag.GoGraphNode`
        :rtype: :py:obj:`str`
        """
        return self.super_node.namespace

    @property
    def obsolete(self):
        """:py:obj:`property` describing whether or not supernode is marked as obsolete.

        :return: :py:obj:`True` or :py:obj:`False`
        """
        return self.super_node.obsolete

    def update_parents(self, parent_set):
        """Updates the parent_node_set with a set of new parents provided. Sets modification state to :py:obj:`True`.

        :param parent_set: A set of parent nodes to be added to this objects parent_node set.
        :return: None
        :rtype: :py:obj:`None`
        """
        self.parent_node_set.update(parent_set)
        self._modified = True

    def update_children(self, child_set):
        """Updates the child_node_set with a set of new children provided. Sets modification state to :py:obj:`True`.

        :param child_set: A set of child nodes to be added to this objects child_node set.
        :return: None
        :rtype: :py:obj:`None`
        """
        self.child_node_set.update(child_set)
        self._modified = True
