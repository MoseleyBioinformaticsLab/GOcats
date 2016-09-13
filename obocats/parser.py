# !/usr/bin/python3
import re
from .dag import AbstractEdge, AbstractRelationship
from .godag import GoGraphNode


class OboParser(object):

    """Parses the Gene Ontology file line-by-line and calls GoGraph based on 
    conditions met through regular expressions."""
    
    def __init__(self):
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

        # May use later.
        #self.comment = re.compile('\!.+')
        #self.subset = re.compile('^subset:')


class GoParser(OboParser):

    """A parser specific to Gene Ontology"""

    def __init__(self, database_file, go_graph):
        super().__init__()
        self.database_file = database_file
        self.go_graph = go_graph
        self.relationship_mapping = {"ends_during": ("temporal", 1, 2), "happens_during": ("temporal", 1, 2), "has_part": ("scaling", 2, 1),
                                     "negatively_regulates": ("active", 1, 2),  "never_in_taxon": ("other", 1, 2), "occurs_in", ("scaling", 1, 2),
                                     "part_of": ("scaling", 1, 2), "positively_regulates": ("active", 1, 2), "regulates": ("active", 1, 2),
                                     "starts_during": ("temporal", 1, 2), "is_a": ("scaling", 1, 2)}

    def parse(self):
        # TODO: find all relationship types using TypeDef stanza
        is_term = False
        is_typedef = False

        for line in self.database_file:

            if not is_term and not is_typedef and re.match(self.term_stanza, line):
                is_term = True
                node = GoGraphNode()
                node_edge_list = []

            if not id_typedef and not is_term and re.match(self.typedef_stanza, line):
                is_typedef = True
                relationship_obj = AbstractRelationship() 

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
                    node_edge = AbstractEdge(re.findall(self.go_term, line)[0], curr_stanza_id, 'is_a')  # node2, node1, relationship
                    node_edge_list.append(node_edge)
                    is_a_relationship = AbstractRelationship()
                    is_a_relationship.id = "is_a"
                    is_a_relationship.name = "is a"
                    self.go_graph.add_relationship(is_a_relationship)

                elif re.match(self.relationship_match, line):
                    relationship_id = re.findall("[\w]+", line)[1]  # line example: relationship: part_of GO:0040025 ! vuval development
                    node_edge = AbstractEdge(re.findall(self.go_term, line)[0], curr_stanza_id, relationship_id)
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
                    relationship_obj.inverse_relationship = re.findall(r"[\w+\:]+", line)[1]

                elif re.match(self.end_stanza, line):
                    properties = self.relationship_mapping[relationship_obj.id]
                    relationship_obj.category = properties[0]
                    relationship_obj.specific_concept_position = properties[1]
                    relationship_obj.generic_concept_position = properties[2]
                    self.go_graph.add_relationship(relationship_obj)
                    is_typedef = False

