# !/usr/bin/python3
""" Open Biomedical Ontologies Categories (OboCats)

Usage:
    obocats build_graph <database_file> <output_directory> [--namespace_filter=<None> --allowed_relationships=<None>]
    obocats build_subgraphs <supergraph> <categories_file> <output_directory> [--namespace_filter=<None> --allowed_relationships=<None> --map_supersets] 
"""
from datetime import date
import sys
import re
import csv
import jsonpickle
from . import dag
from . import parser
from . import godag
from . import subdag
from . import docopt


def main(args):
    if args['build_graph']:
        self.build_graph(args)
    elif args['build_subgraphs']:
        self.build_subgraphs(args)

def build_graph(args):
    if args['--namespace_filter']:
        namespace_filter = args(['--namespace_filter'])
    else:
        namespace_filter = None
    if args['--allowed_relationships']:
        allowed_relationships = args['--allowed_relationships']
    else:
        allowed_relationships = None

    database = open(args['<database_file>'], 'r')
    output_directory = args['<output_directory>']
    file_name = os.path.basename(args['<database_file>'])

    graph_class = {'go.obo': godag.GoGraph(namespace_filter, allowed_relationships)}
    graph = graph_class[file_name]

    parsing_class = {'go.obo': parser.GoParser(database, graph)}
    parsing_class[file_name].parse()

    database.close()
    graph.connect_nodes()

    print("JsonPickle saving GO object")
    json_save(graph, os.path.join(output_directory, "{}_{}".format(filename[:-4], date.today())))

def build_subgraphs(args):
    if args['--namespace_filter']:
        namespace_filter = args(['--namespace_filter'])
    else:
        namespace_filter = None
    if args['--allowed_relationships']:
        allowed_relationships = args['--allowed_relationships']
    else:
        allowed_relationships = None

    supergraph = json_load(args['<supergraph>'])
    subgraph_collection = {}
    with open(args['<category_file>'], newline='') as file:
        reader = csv.reader(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            subgraph_name = row[0]
            keyword_list = [keyword for keyword in re.split(';', row[1])]
            print("Creating subgraph {}".format(subgraph_name))
            subgraph_collection[subgraph_name] = subdag.SubGraph.from_filtered_graph(supergraph, keyword_list, namespace_filter, allowed_relationships)
    for subgraph_name, subgraph in subgraph_collection.items():
        json_save(subgraph.mapping, os.path.join(args['<output_directory>'], subgraph_name))


def json_save(obj, filename):
    """Saves PARAMETER obj in file PARAMETER filename. use_jsonpickle=True used to prevent jsonPickle from encoding
    dictkeys to strings."""
    f = open(filename, 'w')
    json_obj = jsonpickle.encode(obj, keys=True)
    f.write(json_obj)
    f.close()

def json_load(filename):
    """Loads a jsonPickle object from PARAMETER filename. use_jsonpickle=True used to prevent jsonPickle from encoding
    dictkeys to strings."""
    f = open(filename)
    json_str = f.read()
    obj = jsonpickle.decode(json_str, keys=True)
    return obj

if __name__ == '__main__':
    args = docopt.docopt(__doc__, version='OboCats 0.0.1')
    main(args)
