# !/usr/bin/python3
import re
from .dag import AbstractNode, GoDagNode, Edge

class OboParser(object):

    """Parses the Gene Ontology file line-by-line and calls GoDAG based on conditions met through regular
    expressions."""

    term_match = re.compile('^\[Term\]')
    typedef_match = re.compile('^\[Typedef\]')
    comment_match = re.compile('\!.+')
    go_term_match = re.compile('GO\:\d{7}')
    subset_match = re.compile('^subset:')
    id_match = re.compile('^id:')
    name_match = re.compile('^name:')
    namespace_match = re.compile('^namespace:')
    def_match = re.compile('^def:')
    obsolete_match = re.compile('^is_obsolete:\strue')
    is_a_match = re.compile('^is_a:')
    relationship_match = ('^relationship:')
    endterm_match = re.compile('^\s+')
    space_split = re.compile('\s|\.\s|,\s|:\s|;\s|\)\.|\s\(|\"\s|\.\"|,\"')  # Temporarily removed hyphen condition.

    def parse_go(self, database_file, graph):
        # TODO: find all relationship types in go and add to a list of relationship types 
        # TODO: ensure that graph is GOgraph. in the future, don't want to use parse_go for non-go objects.

        """Parses the database using a PARAMETER graph which handles the database, PARAMETER database_file.
        Handles Gene Ontology (GO) obo files. Uses GoDagNode() objects and should be opperated on GoGraph
        objects."""
        is_term = False

        for line in database_file:

            if not is_term and re.match(self.term_match, line):
                is_term = True
                node = GoDagNode()
                node_edge_list = []

            elif is_term:
                if re.match(self.id_match, line):
                    curr_term_id = line[4:-1]
                    node.set_id(line[4:-1])

                elif re.match(self.name_match, line):
                    go_name = re.split(self.space_split, line)[1:-1]
                    node.set_name(go_name)

                elif re.match(self.namespace_match, line):
                    sub_ontology = re.split(self.space_split, line)[1:-1]
                    node.set_sub_ontology(sub_ontology[0])

                elif re.match(self.def_match, line):
                    go_definition = re.split(self.space_split, line)[1:-1]
                    node.set_definition(go_definition)

                elif re.match(self.is_a_match, line):
                    i = re.split(self.space_split, line)
                    node_edge = Edge(i[1], curr_term_id, i[0])  # par_id, child_id, relationship
                    node_edge_list.append(node_edge)
                    graph.relationship_set.add(i[0])  # I will consider 'is_a' a relationship type although the OBO formatting does not technically connsider it a 'relationship'

                elif re.match(self.relationship_match, line):
                    r = re.split(self.space_split, line)
                    node_edge = Edge(r[2], curr_term_id, r[1])
                    node_edge_list.append(node_edge)
                    graph.relationship_set.add(r[1])

                elif re.match(self.obsolete_match, line):
                    node.set_obsolete()

                elif re.match(self.endterm_match, line):
                    graph.add_node(node)
                    for edge in node_edge_list:
                        graph.add_edge(edge)
                    if node_edge_list == [] and node.obsolete == False:  # Have to look at the local edge list because nodes have not been linked with edges yet. Entire graph must be populated first. This is the only way to do this on-the-fly.
                        graph.root_nodes.append(node)
                    is_term = False

"""Parsing for other ontologies can go below here."""

"""
elif re.match(self.part_of_match, line):
    p = re.split(self.space_split, line)
    node_edge = Edge(p[2], curr_term_id, p[1])
    node_edge_list.append(node_edge)

elif re.match(self.has_part_match, line):
    h = re.split(self.space_split, line)
    node_edge = Edge(h[2], curr_term_id, h[1])
    node_edge_list.append(node_edge)
"""