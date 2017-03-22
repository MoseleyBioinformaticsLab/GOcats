# !/usr/bin/python3
"""
Defines a Gene Ontology-specific graph which may have special properties when compared to other OBO formatted
ontologies.
"""
from .dag import OboGraph, AbstractNode


class GoGraph(OboGraph):

    """A Gene-Ontology-specific graph. GO-specific idiosyncrasies go here."""
    
    def __init__(self, namespace_filter=None, allowed_relationships=None):
        """`GoGraph` initializer. Inherits and specializes properties from :class:`gocats.dag.OboGraph`.

        :param str namespace_filter: Specify the namespace of a sub-ontology namespace, if one is available for the ontology.
        :param list allowed_relationships: Specify a list of relationships to utilize in the graph, other relationships will be ignored.
        """
        self.valid_namespaces = ['cellular_component', 'biological_process', 'molecular_function', None]
        if namespace_filter not in self.valid_namespaces:
            raise Exception("{} is not a valid Gene Ontology namespace.\nPlease select from the following: {}".format(namespace_filter, self.valid_namespaces))

        super().__init__(namespace_filter, allowed_relationships)


class GoGraphNode(AbstractNode):

    """Extends AbstractNode to include GO relevant information."""
    
    def __init__(self):
        """`GoGraphNode` initializer. Inherits all properties from :class:`gocats.dag.AbstractNode`.
        """
        super().__init__()
