from .dag import OboGraph, AbstractNode


class SubGraph(OboGraph):

    """A subgraph of a provided super_graph with node contents filtered to those
    containing words from the provided keyword_list."""
    
    def __init__(self, super_graph, namespace_filter=None, allowed_relationships=None):
        self.super_graph = super_graph
        self.top_node = None

        if self.super_graph.namespace_filter and self.super_graph.namespace_filter != namespace_filter:
            raise Exception("Unless a namespace_filter is not specified for a parent_graph, a subgraph's namespace_filter must not differ from its parent graph's namespace_filter.\nsubgraph namespace_filter = {}, supergraph namespace_filter = {}").format(namespace_filter, self.super_graph.namespace_filter)
        
        if self.super_graph.allowed_relationships and allowed_relationships and any(relationship not in self.super_graph.allowed_relationships for relationship in allowed_relationships):
            raise Exception("Unless an allowed_relationships list is not specified for a parent graph, a subgraph's allowed_relationships list must be a subset of, or exactly, its parent graph's allowed_relationships list.\nsubgraph allowed_relationships = {}, supergraph allowed_relationships = {}").format(allowed_relationships, self.super_graph.allowed_relationships)
        
        super().__init__(namespace_filter, allowed_relationships)

    def subnode(self, super_node):
        if super_node.id not in self.id_index:
            self.add_node(super_node)
        return self.id_index[super_node.id]

    def add_node(self, super_node):
        self._modified = True
        subgraph_node = SubGraphNode(super_node, self.allowed_relationships)
        if self.valid_node(subgraph_node):
            super().add_node(subgraph_node)

    def connect_subnodes(self):
        self._modified = True
        for subnode in self.node_list:
            for edge in subnode.super_node.edges:
                if edge.parent_node.id == subnode.id and edge.child_node.id in self.id_index:
                    subnode.edges.append(edge)
                    subnode.child_node_set.add(edge.child_node)
                elif edge.child_node.id == subnode.id and edge.parent_node.id in self.id_index:
                    subnode.edges.append(edge)
                    subnode.parent_node_set.add(edge.parent_node)

    @staticmethod
    def find_top_node(subgraph, keyword_list):
        candidates = [node for node in subgraph.node_list if any(word in node.name for word in keyword_list) and node not in subgraph.leaves and not node.obsolete]
        top_node_scoring = {node: len(subgraph.descendants(node)) for node in candidates}
        return max(top_node_scoring, key=top_node_scoring.get)

    @staticmethod
    def from_filtered_graph(super_graph, keyword_list, namespace_filter=None, allowed_relationships=None):

        subgraph = SubGraph(super_graph, namespace_filter, allowed_relationships)

        keyword_list = [word.lower() for word in keyword_list]

        filtered_nodes = super_graph.filter_nodes(keyword_list)

        for super_node in filtered_nodes:
            subgraph.add_node(super_node)

        subgraph.connect_subnodes()

        subgraph.top_node = subgraph.find_top_node(subgraph, keyword_list)

        return subgraph


class SubGraphNode(AbstractNode):

    """An instance of a node within a subgraph of an OBO ontology (super-graph)
    """
    
    def __init__(self, super_node, allowed_relationships=None):
        self.super_node = super_node
        self.edges = list()
        self.parent_node_set = set()
        self.child_node_set = set()

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
    def namespace(self):
        return self.super_node.namespace

    @property
    def obsolete(self):
        return self.super_node.obsolete
