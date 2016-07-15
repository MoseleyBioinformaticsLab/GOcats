# !/usr/bin/python3
import re


class GoParser(object):

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

    def parse(self, visitor, file_handle):
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
                print(i[0], i[1])
                visitor.append_derived(1, i[1])

            elif is_term is not False and re.match(self.part_of_match, line):
                p = re.split(self.space_split, line)
                print(p[1], p[2])
                visitor.append_derived(2, p[2])

            elif is_term is not False and re.match(self.has_part_match, line):
                h = re.split(self.space_split, line)
                print(h[1], h[2])
                visitor.append_derived(3, h[2])

            elif is_term is not False and re.match(self.obsolete_match, line):
                visitor.make_obsolete()

            elif is_term is not False and re.match(self.endterm_match, line):
                visitor.make_entry()
                is_term = False

class GoDAG(object):

    """GoDAG represents a Visitor DP for use with GoParser."""

    def __init__(self, check_namespace=None):
        """Initialization of Gene Ontology local DAG creation. PARAMETER check_namespace defines which ontology of GO to
        create an object representing the graph structure of the Gene Ontology."""
        self.godag_top_nodes = []
        self.godag_dict = {}
        self.is_a = []
        self.part_of = []
        self.has_part = []
        self.check_namespace = check_namespace
        self.curr_id = None
        self.is_namespace = False
        self.is_obsolete = False

    def set_namespace(self, go_namespace):
        """Assigns the current specified PARAMETER namespace. Can be cellular_component, biological_process, or
        molecular_function."""
        self.go_namespace = go_namespace
        if self.check_namespace is None:
            self.is_namespace = True
        elif self.check_namespace is not None and self.check_namespace in self.go_namespace:
            self.is_namespace = True
        elif self.check_namespace is not None and self.check_namespace not in self.go_namespace:
            pass

    def init_derived(self):
        """Resets all parent and child relationships."""
        self.is_a = []
        self.part_of = []
        self.has_part = []

    def append_derived(self, relationship, value):
        """Depending on PARAMETER relationship type, assigns a parant or child term, PARAMETER value, to the current
        node."""
        if relationship == 1:  # This implementation is bogus, dude.
            self.is_a.append(value)
        elif relationship == 2:
            self.part_of.append(value)
        elif relationship == 3:
            self.has_part.append(value)

    def set_curr_id(self, curr_id):
        """Assigns the PARAMETER current id that is active in the parsing."""
        self.curr_id = curr_id

    def set_definition(self, go_definition):
        """Assigns the PARAMETER definition of the current node."""
        self.go_definition = [w.lower() for w in go_definition]

    def set_go_name(self, go_name):
        """Assigns the PARAMETER name of the current term."""
        self.go_name = [w.lower() for w in go_name]

    def make_obsolete(self):
        """Flags a term as obsolete so it isn't added to the GoDAG."""
        self.is_obsolete = True

    def make_entry(self):
        """Finalizes the creation of an entry once the end of a term has been reached. All data is then reinitialized
        for subsequent terms."""
        if self.is_namespace is True and self.is_obsolete is not True and \
                (self.is_a != [] or self.part_of != [] or self.has_part != []):
            self.godag_dict[self.curr_id] = {
                'id': self.curr_id,
                'name': self.go_name,
                'definition': self.go_definition,
                'is_a': self.is_a,
                'part_of': self.part_of,
                'has_part': self.has_part,
                }

        elif self.is_namespace is True and self.is_obsolete is not True and self.is_a == [] and self.part_of == []:
            self.godag_top_nodes.append(self.curr_id)
            self.godag_dict[self.curr_id] = {
                'id': self.curr_id,
                'name': self.go_name,
                'definition': self.go_definition,
                'is_a': self.is_a,
                'part_of': self.part_of,
                'has_part': self.has_part,
                }

        self.curr_id = None
        self.is_namespace = False
        self.is_organelle = False
        self.go_namespace = []
        self.go_name = []
        self.go_definition = []
        self.init_derived()
        self.is_obsolete = False


parser = GoParser()

go_dag = GoDAG('cellular_component')

parser.parse(go_dag, open('/mlab/data/databases/GeneOntology/05-26-2016/go.obo', 'r'))

