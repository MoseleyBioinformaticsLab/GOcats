# !/usr/bin/python3
""" Open Biomedical Ontologies Categories (OboCats)

Usage:
    obocats filter_subgraphs <database_file> <keyword_file> <output_directory> [--supergraph_namespace=<None> --subgraph_namespace=<None> --supergraph_relationships=[] --subgraph_relationships=[] --map_supersets]

Options:
    -h --help                            Shows this screen.
    --version                            Shows version.
    --supergraph_namespace=<None>        Filters the supergraph to a given namespace.
    --subgraph_namespace=<None>          Filters the subgraph to a given namespace.
    --supergraph_relationships=[]        A provided list will denote which relationships are allowed in the supergraph.
    --subgraph_relationships=[]          A provided list will denote which relationships are allowed in the subgraph.
    --map_supersets                      When spedified

"""
from datetime import date
import os
import re
import csv
import jsonpickle
from . import dag
from . import parser
from . import godag
from . import subdag
from . import docopt


def main(args):
    if args['filter_subgraphs']:
        filter_subgraphs(args)

# FIXME: JsonPickle is reaching max recusion depth because of the fact that objects point to eachother a lot.  
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
    database_name = os.path.basename(args['<database_file>'])
    graph_class = {'go.obo': godag.GoGraph(supergraph_namespace, supergraph_relationships)}
    graph = graph_class[database_name]
    parsing_class = {'go.obo': parser.GoParser(database, graph)}
    parsing_class[database_name].parse()

    database.close()
    graph.connect_nodes()

    print("JsonPickle saving GO object")
    json_save(graph, os.path.join(output_directory, "{}_{}".format(database_name[:-4], date.today())))

def filter_subgraphs(args):
    if args['--supergraph_namespace']:
        supergraph_namespace = args['--supergraph_namespace']
    else:
        supergraph_namespace = None
    if args['--subgraph_namespace']:
        subgraph_namespace = args['--subgraph_namespace']
    else:
        subgraph_namespace = None
    if args['--supergraph_relationships']:
        supergraph_relationships = args['--supergraph_relationships']
    else:
        supergraph_relationships = None
    if args['--subgraph_relationships']:
        subgraph_relationships = args['--subgraph_relationships']
    else:
        subgraph_relationships = None

    # Building the super_graph
    database = open(args['<database_file>'], 'r')
    output_directory = args['<output_directory>']
    database_name = os.path.basename(args['<database_file>'])
    graph_class = {'go.obo': godag.GoGraph(supergraph_namespace, supergraph_relationships)}
    supergraph = graph_class[database_name]
    parsing_class = {'go.obo': parser.GoParser(database, supergraph)}
    parsing_class[database_name].parse()

    database.close()
    supergraph.connect_nodes()

    # Building and collecting subgraphs
    subgraph_collection = {}
    with open(args['<keyword_file>'], newline='') as file:
        reader = csv.reader(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            subgraph_name = row[0]
            keyword_list = [keyword for keyword in re.split(';', row[1])]
            print("Creating subgraph {}".format(subgraph_name))
            subgraph_collection[subgraph_name] = subdag.SubGraph.from_filtered_graph(supergraph, keyword_list, subgraph_namespace, subgraph_relationships)
    for subgraph_name, subgraph in subgraph_collection.items():
        print(subgraph_name, len(subgraph.node_list))

    if not args['--map_supersets']:
        supersets = find_supersets(subgraph_collection)
    else:
        supersets = None
    print(supersets)

    collection_mapping = dict()    
    for subgraph in subgraph_collection.values():
        for node_id, top_node_id in subgraph.mapping.items():
            try:
                collection_mapping[node_id].add(top_node_id)
            except KeyError:
                collection_mapping[node_id] = set([top_node_id])

    json_save(collection_mapping, os.path.join(args['<output_directory>'], "{}_SubGraphMapping.p").format(os.path.basename(args['<keyword_file>'])))

def find_supersets(subgraph_collection):
    is_superset_of = dict()
    for subgraph in subgraph_collection.values():
        current_top_node = subgraph.top_node
        current_contents = subgraph.id_index.keys()
        for next_subgraph in subgraph_collection.values():
            if next_subgraph.top_node.id != current_top_node.id and set(current_contents).issuperset(set(next_subgraph.id_index.keys())):
                is_superset_of[current_top_node.id] = next_subgraph.top_node.id  # The key is a superset of its value
    return is_superset_of

def json_save(obj, file_name):
    """Saves PARAMETER obj in file PARAMETER filename. use_jsonpickle=True used to prevent jsonPickle from encoding
    dictkeys to strings."""
    f = open(file_name, 'w')
    json_obj = jsonpickle.encode(obj, keys=True)
    f.write(json_obj)
    f.close()

def json_load(file_name):
    """Loads a jsonPickle object from PARAMETER filename. use_jsonpickle=True used to prevent jsonPickle from encoding
    dictkeys to strings."""
    f = open(file_name)
    json_str = f.read()
    obj = jsonpickle.decode(json_str, keys=True)
    return obj

if __name__ == '__main__':
    args = docopt.docopt(__doc__, version='OboCats 0.0.1')
    main(args)
