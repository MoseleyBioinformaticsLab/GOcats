# !/usr/bin/python3
from .dag import OboGraph, AbstractNode, AbstractEdge

class GoGraph(OboGraph):

    """A Gene-Ontology-specific graph. GO-specific idiosyncrasies go here."""
    
    def __init__(self, sub_ontology=None):
        super().__init__()
        self.sub_ontology = sub_ontology


class GoGraphNode(AbstractNode):

    """Extends AbstractNode to include GO relevant information"""
    
    def __init__(self):
        super().__init__()
        self.sub_ontology = None

