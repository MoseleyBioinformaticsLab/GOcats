# !/usr/bin/python3
import re
from .dag import AbstractNode, GoGraphNode, Edge

class OboParser(object):

    """Parses the Gene Ontology file line-by-line and calls GoGraph based on conditions met through regular
    expressions."""
    
    term_stanza = re.compile('\[Term\]')
    go_term = re.compile('GO\:\d{7}')
    term_id = re.compile('^id:')
    term_name = re.compile('^name:')
    go_namespace = re.compile('^namespace:')
    term_definition = re.compile('^def:')
    obsolete = re.compile('^is_obsolete:\strue')
    is_a = re.compile('^is_a:')
    relationship_match = ('^relationship:')
    endterm_stanza = re.compile('^\s+')
    space_split = re.compile('\s|\.\s|,\s|:\s|;\s|\)\.|\s\(|\"\s|\.\"|,\"')  # Temporarily removed hyphen condition.
    # May use later. 
    #typedef_stanza = re.compile('^\[Typedef\]')
    #comment = re.compile('\!.+')
    #subset = re.compile('^subset:')

    def parse_go(self, database_file, graph):
        # TODO: find all relationship types in go and add to a list of relationship types 
        # TODO: ensure that graph is GOgraph. in the future, don't want to use parse_go for non-go objects.
        """Parses the database using a PARAMETER graph which handles the database, PARAMETER database_file.
        Handles Gene Ontology (GO) obo files. Uses GoGraphNode() objects and should be opperated on GoGraph
        objects."""
        is_term = False

        for line in database_file:

            if not is_term and re.match(self.term_stanza, line):
                is_term = True
                node = GoGraphNode()
                node_edge_list = []

            elif is_term:
                if re.match(self.term_id, line):
                    node.id = re.findall(self.go_term, line)[0]
                    curr_term_id = node.id

                elif re.match(self.term_name, line):
                    node.name = line[6:-1]  # ignores 'name: '

                elif re.match(self.go_namespace, line):
                    node.sub_ontology = line[11:-1]  # ignores 'namespace: '

                elif re.match(self.term_definition, line):
                    node.definition = re.findall('\"(.*?)\"', line)[0]  # This pattern matches the definition listed within quotes on the line.

                elif re.match(self.is_a, line):
                    node_edge = Edge(re.findall(self.go_term, line)[0], curr_term_id, 'is_a')  # par_id, child_id, relationship
                    node_edge_list.append(node_edge)
                    graph.used_relationship_set.add('is_a')  # I will consider 'is_a' a relationship type although the OBO formatting does not technically connsider it a 'relationship'

                elif re.match(self.relationship_match, line):
                    relationship = re.findall("[\w]+", line)[1]  # line example: relationship: part_of GO:0040025 ! vuval development
                    node_edge = Edge(re.findall(self.go_term, line)[0], curr_term_id, relationship)
                    node_edge_list.append(node_edge)
                    graph.used_relationship_set.add(relationship)

                elif re.match(self.obsolete, line):
                    node.obsolete = True

                elif re.match(self.endterm_stanza, line):
                    graph.add_node(node)
                    for edge in node_edge_list:
                        graph.add_edge(edge)
                    if node_edge_list == [] and node.obsolete == False:  # Have to look at the local edge list because nodes have not been linked with edges yet. Entire graph must be populated first. This is the only way to do this on-the-fly.
                        graph.root_nodes.append(node)
                    is_term = False
