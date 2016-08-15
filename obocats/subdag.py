from .dag import OboGraph, AbstractNode
import re


class SubGraph(OboGraph):

    """A subgraph of a provided super_graph with node contents filtered to those
    containing words from the provided keyword_list."""
    
    def __init__(self, super_graph):
        super().__init__()
        self.super_graph = super_graph
        self.top_node = None

    @staticmethod
    def find_top_node(graph, keyword_list, node_list):
        candidates = [node for node in node_list if len(set(re.findall(r"[\w'-]+", node.name)).intersection(set(keyword_list))) > 0 and not node.obsolete]
        top_node_scoring = {node: len(graph.descendants(node)) for node in candidates}
        return max(top_node_scoring, key=top_node_scoring.get)

    @staticmethod
    def from_filtered_graph(graph, keyword_list, sub_ontology_filter=None, allowed_relationships=None):
        subgraph = SubGraph(graph)
        keyword_list = [word.lower() for word in keyword_list]
        filtered_nodes = graph.filter_nodes(keyword_list, sub_ontology_filter)
        filtered_edges = graph.filter_edges(filtered_nodes, allowed_relationships)
        for node in filtered_nodes:
            subgraph_node = SubGraphNode(node, allowed_relationships)
            subgraph.add_node(subgraph_node)
        for edge in filtered_edges:
            subgraph.add_edge(edge)
        subgraph.connect_nodes(allowed_relationships)
        subgraph.top_node = subgraph.find_top_node(graph, keyword_list, filtered_nodes)

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
    def obsolete(self):
        return self.super_node.obsolete
