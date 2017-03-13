# !usr/bin/python3
"""
UniProt subcellular location parser and graph creation module command line implementation::

    Usage:
        uniprotsubcellparser.py build_subdags <cv_file> <output_directory> [--visualize]

    Options:
        -h --help                     Show this screen.
        --visualize                   Visualize subdags after creation
"""
import os
import re
import docopt
import tools
import version


def main(args):
    if args['build_subdags']:
        build_subdags(args)


def build_subdags(args):
    # Uniprot Subcellular Location text file location
    sl = open(args['<cv_file>'], 'r')  # 'exampledata/uniprotparse/subcell.txt'
    uniprot_collection = list()
    go_translated_dict = dict()
    uniprot_multi_root = dict()

    uniprot_subcell_results_dir = os.path.realpath(args['<output_directory>'])
    if not os.path.exists(uniprot_subcell_results_dir):
        os.makedirs(uniprot_subcell_results_dir)

    # Main execution for the program
    scparser = SubcellParser()
    udag = UniprotDAG()
    scparser.parse(udag, sl)

    for top_node in udag.top_nodes:
        UniprotSubDAG(udag, top_node, uniprot_collection)

    for subdag in uniprot_collection:
        for top_node, contents in subdag.items():
            if args['--visualize']:
                print(udag.go_to_name_mapping[top_node])
                c = 1
                for i in contents:
                    print(' -'*c, udag.go_to_name_mapping[i])
                    c += 1
            go_translated_dict[top_node] = contents

    for top_node, contents in go_translated_dict.items():
        for location in contents:
            if location in uniprot_multi_root.keys() and top_node not in uniprot_multi_root[location]:
                uniprot_multi_root[location].append(top_node)
            else:
                uniprot_multi_root[location] = [top_node]

    tools.jsonpickle_save(go_translated_dict, os.path.join(uniprot_subcell_results_dir, 'UP_content_mapping'))
    tools.jsonpickle_save(uniprot_multi_root, os.path.join(uniprot_subcell_results_dir, 'UP_root_mapping'))


class SubcellParser():

    """Parses Uniprot's subcell.txt to build a DAG version of the term relationships."""

    start_match = re.compile('^\_\_*')
    id_match = re.compile('^ID')
    part_match = re.compile('^HP')
    is_match = re.compile('^HI')
    go_match = re.compile('^GO')
    end_match = re.compile('^\/\/')
    space_split = re.compile('\s|\.|\-|\,|\s|\;\s|\)\.|\s\(|\"\s|\.\"|\,\"')

    def parse(self, visitor, file_handle):
        """Parses the PARAMETER file_handle file using the PARAMETER visitor. NOTE THIS WAS UNDER """
        file_start = False
        is_term = False
        visitor.init_derived()
        for line in file_handle:
            if file_start is False and re.match(SubcellParser.start_match, line):
                file_start = True
            elif is_term is False and file_start == True and re.match(SubcellParser.id_match, line):
                is_term = True
                visitor.set_curr_id(line[5:-2])
            elif is_term is not False and re.match(SubcellParser.is_match, line):
                visitor.set_is(line[5:-2])
            elif is_term is not False and re.match(SubcellParser.part_match, line):
                visitor.set_part(line[5:-2])
            elif is_term is not False and re.match(SubcellParser.go_match, line):
                    go_line = re.split(SubcellParser.space_split, line)
                    visitor.set_go(go_line[3])
            elif is_term is not False and re.match(SubcellParser.end_match, line):
                visitor.make_entry()
                is_term = False
        visitor.destroy_troublemakers()
        visitor.set_top_nodes()


class UniprotDAG:

    """A graph representation of the Uniprot subcellular locations. Acts as a visitor to the file_handle to save
    information without altering the file."""

    def __init__(self):
        """Creates containers for DAG creation."""
        self.DAG_dict = dict()
        self.go_to_name_mapping = dict()
        self.curr_id = None
        self.go_id = None
        self.is_a = list()
        self.part_of = list()
        self.top_nodes = list()
        self.destroy_list = list()

    def init_derived(self):
        """Reinitializes the relationship lists."""
        self.is_a = list()
        self.part_of = list()

    def set_curr_id(self, curr_id):
        """Sets the current ID of the term being parsed."""
        self.curr_id = curr_id.lower()

    def set_is(self, is_line):
        """Sets the current 'is a' relationship partner."""
        self.is_a.append(is_line.lower())

    def set_part(self, part_line):
        """Sets the current 'part of' relationship partner."""
        self.part_of.append(part_line.lower())

    def set_go(self, go_line):
        """Sets the current GO ID."""
        self.go_id = go_line

    def destroy_troublemakers(self):  # Trouble makers are separate CV terms that share the same GO term
        for term in self.destroy_list:
            del self.DAG_dict[term]

    def make_entry(self):
        """At the end of a term, saves all currently assigned information to a dictionary entry. Reinitializes all
        variables."""
        if self.go_id is not None:  # Some of them don't have GO ids
            if self.go_id in self.go_to_name_mapping:
                self.destroy_list.append(self.curr_id)  # Remove terms that refer to the same GO term.
            self.DAG_dict[self.curr_id] = {
                'name': self.curr_id,
                'is_a': self.is_a,
                'part_of': self.part_of,
                'go_id': self.go_id
                 }
            self.go_to_name_mapping[self.go_id] = self.curr_id

        self.curr_id = None
        self.go_id = None
        self.init_derived()

    def set_top_nodes(self):
        """Signifies all top-nodes in the Uniprot controlled vocabulary by finding all terms without parents."""
        self.top_nodes = [node for key, node in self.DAG_dict.items() if node['is_a'] == [] and node['part_of'] == []]


class UniprotSubDAG:

    """Creates a subDAG for every top-node identified in the Uniprot CV. Every node without a parent is assigned as a
    top-node."""

    def __init__(self, udag, top_node, uniprot_collection):
        """Initialization of UniprotSubDAG. Creates containers for subDAG nodes. Calls build_subdag to iterate through
        children of children in the Uniprot DAG to find all children of the top-node. If the top-node contains a GO ID,
        it is saved to the GLOBAL subDAG collection."""
        self.udag = udag
        self.top_node = top_node
        self.subdag_list = list()
        self.subdag_dict = dict()
        self.subdag_list.append(top_node['name'])  # The top_node itself should be considered part of its own category
        self._build_subdag(self.top_node['name'], self.udag.DAG_dict)
        self.subdag_dict[self.top_node['go_id']] = [node['go_id'] for k, node in self.udag.DAG_dict.items() if k in self.subdag_list]
        uniprot_collection.append(self.subdag_dict)

    def _build_subdag(self, term, graph):
        """Because Uniprot subDAG creation is TOP-TOWN, this must be written like this. Children must be found from the
        top-node. Iterates through children of children to find all contents of a top-node."""
        if term != self.top_node['name']:
            self.subdag_list.append(graph[term]['name'])
        child_list = list()
        child_list.extend([node['name'] for key, node in graph.items() if term in node['is_a'] + node['part_of']])
        for item in child_list:
            self._build_subdag(item, graph)

if __name__ == '__main__':
    args = docopt.docopt(__doc__, version='UniProtSubcellParser Version ' + version.__version__)
    main(args)
