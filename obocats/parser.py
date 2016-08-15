# !/usr/bin/python3
import re
from .dag import AbstractNode, AbstractEdge
from .godag import GoGraphNode

class OboParser(object):

    """Parses the Gene Ontology file line-by-line and calls GoGraph based on 
    conditions met through regular expressions."""
    
    def __init__(self):
        self.term_stanza = re.compile('\[Term\]')
        self.go_term = re.compile('GO\:\d{7}')
        self.term_id = re.compile('^id:')
        self.term_name = re.compile('^name:')
        self.namespace = re.compile('^namespace:')
        self.term_definition = re.compile('^def:')
        self.obsolete = re.compile('^is_obsolete:\strue')
        self.is_a = re.compile('^is_a:')
        self.relationship_match = ('^relationship:')
        self.endterm_stanza = re.compile('^\s+')

        # May use later. 
        #self.typedef_stanza = re.compile('^\[Typedef\]')
        #self.comment = re.compile('\!.+')
        #self.subset = re.compile('^subset:')


class GoParser(OboParser):

    """A parser specific to Gene Ontology"""

    def __init__(self, database_file, go_graph):
        super().__init__()
        self.database_file = database_file
        self.go_graph = go_graph

    def parse(self):
        # TODO: find all relationship types using TypeDef stanza
        is_term = False

        for line in self.database_file:

            if not is_term and re.match(self.term_stanza, line):
                is_term = True
                node = GoGraphNode()
                node_edge_list = []

            elif is_term:
                if re.match(self.term_id, line):
                    node.id = re.findall(self.go_term, line)[0]
                    curr_term_id = node.id

                elif re.match(self.term_name, line):
                    node.name = line[6:-1].lower()  # ignores 'name: '

                elif re.match(self.namespace, line):
                    node.namespace = line[11:-1].lower()  # ignores 'namespace: '

                elif re.match(self.term_definition, line):
                    node.definition = re.findall('\"(.*?)\"', line)[0].lower()  # This pattern matches the definition listed within quotes on the line.

                elif re.match(self.is_a, line):
                    node_edge = AbstractEdge(re.findall(self.go_term, line)[0], curr_term_id, 'is_a')  # par_id, child_id, relationship
                    node_edge_list.append(node_edge)

                elif re.match(self.relationship_match, line):
                    relationship = re.findall("[\w]+", line)[1]  # line example: relationship: part_of GO:0040025 ! vuval development
                    node_edge = AbstractEdge(re.findall(self.go_term, line)[0], curr_term_id, relationship)
                    node_edge_list.append(node_edge)

                elif re.match(self.obsolete, line):
                    node.obsolete = True

                elif re.match(self.endterm_stanza, line):
                    if self.go_graph.valid_node(node):
                        self.go_graph.add_node(node)
                        for edge in node_edge_list:
                            if self.go_graph.valid_relationship(edge):
                                self.go_graph.add_edge(edge)
                                self.go_graph.used_relationship_set.add(edge.relationship)
                        if node_edge_list == [] and node.obsolete == False:  # Have to look at the local edge list because nodes have not been linked with edges yet. Entire graph must be populated first. This is the only way to do this on-the-fly.
                            self.go_graph.root_nodes.append(node)
                    is_term = False
