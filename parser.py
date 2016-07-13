# !/usr/bin/python3
import re
from dag import AbstractNode, GoDagNode, Edge

class OboParser(object):

    """Parses the Gene Ontology file line-by-line and calls GoDAG based on conditions met through regular
    expressions."""

    term_match = re.compile('^\[Term\]')
    subset_match = re.compile('^subset:')
    id_match = re.compile('^id:')
    name_match = re.compile('^name:')
    namespace_match = re.compile('^namespace:')
    def_match = re.compile('^def:')
    obsolete_match = re.compile('^is_obsolete:\strue')
    is_a_match = re.compile('^is_a:')
    part_of_match = re.compile('^relationship:\spart_of')
    has_part_match = re.compile('^relationship:\shas_part')
    endterm_match = re.compile('^\s+')
    space_split = re.compile('\s|\.\s|,\s|:\s|;\s|\)\.|\s\(|\"\s|\.\"|,\"')  # Temporarily removed hyphen condition.

    def parse_go(self, database_file, graph):
        """Parses the database using a PARAMETER graph which handles the database, PARAMETER database_file."""
        is_term = False
        graph.init_derived()

        for line in database_file:

            if not is_term and re.match(self.term_match, line):
                is_term = True
                node = GoDagNode()
                node_edge_list = []

            elif is_term and re.match(self.id_match, line):
            	curr_term_id = line[4:-1]
                node.set_id(line[4:-1])

            elif is_term and re.match(self.name_match, line):
                go_name = re.split(self.space_split, line)[1:-1]
                node.set_name(go_name)

            elif is_term and re.match(self.namespace_match, line):
                sub_ontology = re.split(self.space_split, line)[1:-1]
                node.set_sub_ontology(sub_ontology)

            elif is_term and re.match(self.def_match, line):
                go_definition = re.split(self.space_split, line)[1:-1]
                node.set_definition(go_definition)

            elif is_term and re.match(self.is_a_match, line):
                i = re.split(self.space_split, line)
                node_edge = Edge()
                node_edge.set_parent_id(i[1])
                node_edge.set_child_id(curr_term_id)
                node_edge.set_relationship(i[0])
                node_edge_list.append(node_edge)
                node_edge = None

            elif is_term and re.match(self.part_of_match, line):
                p = re.split(self.space_split, line)
                node_edge = Edge()
                node_edge.set_parent_id(p[2])
                node_edge.set_child_id(curr_term_id)
                node_edge.set_relationship(p[1])
                node_edge_list.append(node_edge)
                node_edge = None

            elif is_term and re.match(self.has_part_match, line):
                h = re.split(self.space_split, line)
                node_edge = Edge()
                node_edge.set_parent_id(h[2])
                node_edge.set_child_id(curr_term_id)
                node_edge.set_relationship(h[1])
                node_edge_list.append(node_edge)
                node_edge = None

            elif is_term and re.match(self.obsolete_match, line):
                node.set_obsolete()

            elif is_term False and re.match(self.endterm_match, line):
                graph.add_node(node)
                for edge in node_edge_list:
                	graph.add_edge(edge)
                is_term = False
                # do I need to reinitialized these?
                node = None
                node_edge_list = []
                curr_term_id = ''
                go_name = []
                sub_ontology = ''
                go_defiintion = []
                i = []
                p = []
                h = []

"""Parsing for other ontologies can go below here."""