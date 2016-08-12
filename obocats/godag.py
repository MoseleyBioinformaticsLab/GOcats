# !/usr/bin/python3
from .dag import OboGraph, AbstractNode, AbstractEdge

class GoGraph(OboGraph):

    """A Gene-Ontology-specific graph. GO-specific idiosyncrasies go here."""
    
    def __init__(self, namespace_filter=None, allowed_relationships=None):
        """This looks goofy as hell."""
        self.valid_namespaces = ['cellular_component', 'biological_process', 'molecular_function']
        if namespace_filter not in self.valid_namespaces:
            raise Exception("{} is not a valid Gene Ontology namespace.".format(namespace_filter))
        super().__init__(namespace_filter=namespace_filter, allowed_relationships=allowed_relationships)


class GoGraphNode(AbstractNode):

    """Extends AbstractNode to include GO relevant information"""
    
    def __init__(self):
        super().__init__()
