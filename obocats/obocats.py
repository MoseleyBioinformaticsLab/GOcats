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
import dag
import parser
import godag
import subdag
import docopt


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
            subgraph_collection[subgraph_name] = subdag.SubGraph.from_filtered_graph(supergraph, keyword_list, subgraph_namespace, subgraph_relationships)

    if not args['--map_supersets']:
        category_subsets = find_category_subsets(subgraph_collection)
#        for key, value in category_subsets.items():
#            print(supergraph.id_index[key].name, [supergraph.id_index[id].name for id in value])
#        print(category_subsets)
    else:
        category_subsets = None

    collection_id_mapping = dict()
    collection_node_mapping = dict()
    for subgraph in subgraph_collection.values():
        for node_id, root_node_ids in subgraph.root_id_mapping.items():
            try:
                collection_id_mapping[node_id].update(root_node_ids)
            except KeyError:
                collection_id_mapping[node_id] = set(root_node_ids)
        for node, root_nodes in subgraph.root_node_mapping.items():
            try:
                collection_node_mapping[node].update(root_nodes)
            except KeyError:
                collection_node_mapping[node] = set([root_nodes])

    json_save(collection_id_mapping, os.path.join(args['<output_directory>'], "{}_SubGraphMapping.p").format(re.findall("\w+", os.path.basename(args['<keyword_file>']))[0]))

def find_category_subsets(subgraph_collection):
    is_subset_of = dict()
    for subgraph in subgraph_collection.values():
        for next_subgraph in subgraph_collection.values():
            if subgraph.top_node.id in next_subgraph.root_id_mapping.keys():
                try:
                    is_subset_of[subgraph.top_node.id].add(next_subgraph.top_node.id)
                except KeyError:
                    is_subset_of[subgraph.top_node.id] = {next_subgraph.top_node.id}
    return is_subset_of

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
