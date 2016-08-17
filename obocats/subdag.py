from .dag import OboGraph, AbstractNode
import re


class SubGraph(OboGraph):

    """A subgraph of a provided super_graph with node contents filtered to those
    containing words from the provided keyword_list."""
    
    def __init__(self, super_graph, namespace_filter=None, allowed_relationships=None):
        self.super_graph = super_graph
        self.top_node = None
        super().__init__(namespace_filter, allowed_relationships)

    def remove_orphans(self):
        print([node.name for node in self.descendants(self.top_node)])
        for node in self.orphans:
            if node.id == self.top_node.id:
                pass
            elif node not in self.descendants(self.top_node):
                print("Removing node: ", node.name)
                for edge in node.edges:
                    self.remove_edge(edge)
                self.remove_node(node)

    @staticmethod
    def extend_subdag(super_graph, subgraph, node_list, top_node):
        return

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
        filtered_edges = super_graph.filter_edges(filtered_nodes)

        for node in filtered_nodes:
            subgraph_node = SubGraphNode(node, allowed_relationships)
            if subgraph.valid_node(subgraph_node):
                subgraph.add_node(subgraph_node)
        for edge in filtered_edges:
            if subgraph.valid_relationship(edge):
                subgraph.add_edge(edge)

        subgraph.connect_nodes()

        subgraph.top_node = subgraph.find_top_node(subgraph, keyword_list)
        print("subgraph top-node: ", subgraph.top_node.name)

        #while len(subgraph.orphans) > 1:
        #    subgraph.remove_orphans()

        # Need to do the whole orphan node removal/extend subdag functions. 
        #These should go in obograph. 

        return subgraph


class SubGraphNode(AbstractNode):

    """An instance of a node within a subgraph of an OBO ontology (super-graph)
    """
    
    def __init__(self, super_node, allowed_relationships=None):
        self.super_node = super_node
        self.edges = list()  # Overwriting from AbstractNode
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
