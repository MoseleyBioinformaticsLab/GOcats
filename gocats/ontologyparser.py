# !/usr/bin/python3
"""
A parser which reads ontologies in the OBO format and calls appropriate graph objects to store information in a graph
representation. Separate parsing classes within this module operate on distinct ontologies in the OBO Foundry to handle
any subtle differences among ontologies.
"""
import re
from .dag import AbstractEdge, DirectionalRelationship
from .godag import GoGraphNode


class OboParser(object):

    """A scaffolding for parsing OBO formatted ontologies. Contains regular expressions for the basic stanzas and
    information pertinent for creating a graph object of an ontology."""

    def __init__(self):
        """`OboParser` initializer. Contains Regular Expressions for identifying crucial information from OBO formatted
        ontologies.
        """
        self.term_stanza = re.compile('\[Term\]')
        self.go_term = re.compile('GO\:\d{7}')
        self.stanza_id = re.compile('^id:')
        self.stanza_name = re.compile('^name:')
        self.namespace = re.compile('^namespace:')
        self.term_definition = re.compile('^def:')
        self.obsolete = re.compile('^is_obsolete:\strue')
        self.is_a = re.compile('^is_a:')
        self.relationship_match = re.compile('^relationship:')
        self.end_stanza = re.compile('^\s+')
        self.typedef_stanza = re.compile('^\[Typedef\]')
        self.inverse_tag = re.compile('^inverse_of:')

        # May use later.
        # self.comment = re.compile('\!.+')
        # self.subset = re.compile('^subset:')


class GoParser(OboParser):

    """An ontology parser specific to Gene Ontology"""


    def __init__(self, database_file, go_graph, relationship_directionality='gocats'):
        """`GoParser` initializer. Parses a Gene Ontology database file and adds properties found therein to a
        :class:`godag.GoGraph` object. **Importantly:** includes descriptions of semantic directionality of all GO
        relationships.
        :param file_handle database_file: Specify the location of a Gene Ontology .obo file.
        :param go_graph: :class:`gocats.godag.GoGraph` object.
        :return: None
        :rtype: :py:obj:`None`
        """
        super().__init__()
        self.database_file = database_file
        self.go_graph = go_graph
        # 5 types of relationships: scoping, scaling (grouped with scoping for now), spatiotemporal, active, equivalence (not present here), and other.
        # 1 means that the relationship directionality is conventional, 0 means that the semantic directionality points from node 2 to node 1.
        if relationship_directionality == 'gocats':
            self.relationship_mapping = {"ends_during": ("spatiotemporal", 1), "happens_during": ("spatiotemporal", 1), "has_part": ("scoping", 0),
                                         "negatively_regulates": ("active", 1), "never_in_taxon": ("other", 1), "occurs_in": ("spatiotemporal", 1),
                                         "part_of": ("scoping", 1), "positively_regulates": ("active", 1), "regulates": ("active", 1),
                                         "starts_during": ("spatiotemporal", 1), "is_a": ("scoping", 1)}
        else:
            self.relationship_mapping = {"ends_during": ("spatiotemporal", 1), "happens_during": ("spatiotemporal", 1), "has_part": ("scoping", 1),
                                         "negatively_regulates": ("active", 1), "never_in_taxon": ("other", 1), "occurs_in": ("spatiotemporal", 1),
                                         "part_of": ("scoping", 1), "positively_regulates": ("active", 1), "regulates": ("active", 1),
                                         "starts_during": ("spatiotemporal", 1), "is_a": ("scoping", 1)}

    def parse(self):
        """Parses the ontology database file and accesses the ontology graph object to add information found in the
        database. Once all information is added, this function calls the graph's instantiate_valid_edges function to
        connect all nodes in the graph by their edges.

        :return: None
        :rtype: :py:obj:`None`
        """
        is_term = False
        is_typedef = False

        for line in self.database_file:

            if not is_term and not is_typedef and re.match(self.term_stanza, line):
                is_term = True
                node = GoGraphNode()
                node_edge_list = []

            if not is_typedef and not is_term and re.match(self.typedef_stanza, line):
                is_typedef = True
                relationship_obj = DirectionalRelationship()

            elif is_term:
                if re.match(self.stanza_id, line):
                    node.id = re.findall(self.go_term, line)[0]
                    curr_stanza_id = node.id

                elif re.match(self.stanza_name, line):
                    node.name = line[6:-1].lower()  # ignores 'name: '

                elif re.match(self.namespace, line):
                    node.namespace = line[11:-1].lower()  # ignores 'namespace: '

                elif re.match(self.term_definition, line):
                    node.definition = re.findall('\"(.*?)\"', line)[0].lower()  # This pattern matches the definition listed within quotes on the line.

                elif re.match(self.is_a, line):
                    node_edge = AbstractEdge(curr_stanza_id, re.findall(self.go_term, line)[0], 'is_a')  # node1, node2, relationship
                    node_edge_list.append(node_edge)
                    if "is_a" not in self.go_graph.relationship_index:
                        is_a_relationship = DirectionalRelationship()
                        is_a_relationship.id = "is_a"
                        is_a_relationship.name = "is a"
                        is_a_relationship.category = self.relationship_mapping["is_a"][0]
                        is_a_relationship.direction = self.relationship_mapping["is_a"][1]
                        self.go_graph.used_relationship_set.add(is_a_relationship.id)
                        self.go_graph.add_relationship(is_a_relationship)

                elif re.match(self.relationship_match, line):
                    relationship_id = re.findall("[\w]+", line)[1]  # line example: relationship: part_of GO:0040025 ! vuval development
                    node_edge = AbstractEdge(curr_stanza_id, re.findall(self.go_term, line)[0], relationship_id)
                    node_edge_list.append(node_edge)

                elif re.match(self.obsolete, line):
                    node.obsolete = True

                elif re.match(self.end_stanza, line):
                    if self.go_graph.valid_node(node):
                        self.go_graph.add_node(node)
                        for edge in node_edge_list:
                            if not self.go_graph.allowed_relationships or edge.relationship_id in self.go_graph.allowed_relationships:
                                self.go_graph.add_edge(edge)
                                self.go_graph.used_relationship_set.add(edge.relationship_id)
                        if node_edge_list == [] and node.obsolete == False:  # Have to look at the local edge list because nodes have not been linked with edges yet. Entire graph must be populated first. This is the only way to do this on-the-fly.
                            self.go_graph.root_nodes.append(node)  # make root nodes a set of all namespaces used in the ontology.
                    is_term = False

            elif is_typedef:
                if re.match(self.stanza_id, line):
                    relationship_obj.id = re.findall(r"[\w+\:]+", line)[1]

                elif re.match(self.stanza_name, line):
                    relationship_obj.name = re.findall(r"[\w+\:]+", line)[1]

                elif re.match(self.inverse_tag, line):
                    relationship_obj.inverse_relationship_id = re.findall(r"[\w+\:]+", line)[1]

                elif re.match(self.end_stanza, line):
                    properties = self.relationship_mapping[relationship_obj.id]
                    relationship_obj.category = properties[0]
                    relationship_obj.direction = properties[1]
                    self.go_graph.add_relationship(relationship_obj)
                    is_typedef = False

        self.go_graph.instantiate_valid_edges()
