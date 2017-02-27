# !/usr/bin/python3
from dag import OboGraph, AbstractNode


class GoGraph(OboGraph):

    """A Gene-Ontology-specific graph. GO-specific idiosyncrasies go here."""
    
    def __init__(self, namespace_filter=None, allowed_relationships=None):
        self.valid_namespaces = ['cellular_component', 'biological_process', 'molecular_function', None]
        if namespace_filter not in self.valid_namespaces:
            raise Exception("{} is not a valid Gene Ontology namespace.\nPlease select from the following: {}".format(namespace_filter, self.valid_namespaces))

        super().__init__(namespace_filter, allowed_relationships)


class GoGraphNode(AbstractNode):

    """Extends AbstractNode to include GO relevant information."""
    
    def __init__(self):
        super().__init__()
