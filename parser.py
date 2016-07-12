# !/usr/bin/python3
import re


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

    def go_parse(self, graph, file_handle):
        """Parses the database using a PARAMETER visitor which handles the database, PARAMETER file_handle."""
        is_term = False
        visitor.init_derived()

        for line in file_handle:

            if is_term is False and re.match(self.term_match, line):
                is_term = True

            elif is_term is not False and re.match(self.id_match, line):
                visitor.set_curr_id(line[4:-1])

            elif is_term is not False and re.match(self.name_match, line):
                go_name = re.split(self.space_split, line)[1:-1]
                visitor.set_go_name(go_name)

            elif is_term is not False and re.match(self.namespace_match, line):
                go_namespace = re.split(self.space_split, line)[1:-1]
                visitor.set_namespace(go_namespace)

            elif is_term is not False and re.match(self.def_match, line):
                go_definition = re.split(self.space_split, line)[1:-1]
                visitor.set_definition(go_definition)

            elif is_term is not False and re.match(self.is_a_match, line):
                i = re.split(self.space_split, line)
                visitor.append_derived(1, i[1])

            elif is_term is not False and re.match(self.part_of_match, line):
                p = re.split(self.space_split, line)
                visitor.append_derived(2, p[2])

            elif is_term is not False and re.match(self.has_part_match, line):
                h = re.split(self.space_split, line)
                visitor.append_derived(3, h[2])

            elif is_term is not False and re.match(self.obsolete_match, line):
                visitor.make_obsolete()

            elif is_term is not False and re.match(self.endterm_match, line):
                visitor.make_entry()
                is_term = False

"""Parsing for other ontologies can go below here."""