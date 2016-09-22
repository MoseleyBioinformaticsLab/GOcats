# !/usr/bin/python3
""" Open Biomedical Ontologies Categories (OboCats)

Usage:
    obocats filter_subgraphs <database_file> <keyword_file> <output_directory> [--supergraph_namespace=<None> --subgraph_namespace=<None> --supergraph_relationships=[] --subgraph_relationships=[] --map_supersets --output_termlist]
    obocats subgraph_overlap <obocats_mapping> <uniprot_mapping> <map2slim_mapping> <output_directory> [--inclusion_index]
Options:
    -h --help                            Shows this screen.
    --version                            Shows version.
    --supergraph_namespace=<None>        Filters the supergraph to a given namespace.
    --subgraph_namespace=<None>          Filters the subgraph to a given namespace.
    --supergraph_relationships=[]        A provided list will denote which relationships are allowed in the supergraph.
    --subgraph_relationships=[]          A provided list will denote which relationships are allowed in the subgraph.
    --map_supersets                      Maps all terms to all root nodes, regardless of if a root node supercedes another.
    --output_termlist                    Outputs a list of all terms in the supergraph as a JsonPickle file in the output directory.
    --inclusion_index                    Calculates inclusion index of terms between categories among separate mapping sources

"""
from datetime import date
import os
import re
import csv
import dag
import parser
import godag
import subdag
import docopt
import tools


def main(args):
    if args['filter_subgraphs']:
        filter_subgraphs(args)
    elif args['subgraph_overlap']:
        subgraph_overlap(args)

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
    tools.json_save(graph, os.path.join(output_directory, "{}_{}".format(database_name[:-4], date.today())))

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

    if args['--output_termlist']:
        tools.json_save(list(supergraph.id_index.keys()), os.path.join(args['<output_directory>'], "termlist"))

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

    # Handling superset mapping
    if not args['--map_supersets']:
        category_subsets = find_category_subsets(subgraph_collection)
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

    tools.json_save(collection_id_mapping, os.path.join(args['<output_directory>'], "OC_id_mapping"))

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

def subgraph_overlap(args):
    import pandas as pd
    import pyupset as pyu
    if not os.path.exists(args['<output_directory>']):
        os.makedirs(args['<output_directory>'])
 
    inc_index_table = []
    gocats_mapping = tools.json_load(args['<obocats_mapping>'])
    uniprot_mapping = tools.json_load(args['<uniprot_mapping>'])
    map2slim_mapping = tools.json_load(args['<map2slim_mapping>'])

    location_categories = set(list(gocats_mapping.keys())+list(uniprot_mapping.keys())+list(map2slim_mapping.keys()))
    for location in [x for x in location_categories if x not in set(uniprot_mapping.keys()).intersection(*[set(gocats_mapping.keys()), set(map2slim_mapping.keys())])]:
        uniprot_mapping[location] = [location]
    shared_locations = set(uniprot_mapping.keys()).intersection(*[set(gocats_mapping.keys()), set(map2slim_mapping.keys())])
    for location in shared_locations:
        go_id_string = str(location)[3:]
        gc_set = pd.DataFrame({'Terms': gocats_mapping[location]})
        up_set = pd.DataFrame({'Terms': uniprot_mapping[location]})
        m2s_set = pd.DataFrame({'Terms': map2slim_mapping[location]})
        set_dict = {'GOcats': gc_set, 'UniProt': up_set, 'Map2Slim': m2s_set}
        pyuobject = pyu.plot(set_dict, unique_keys=['Terms'])
        pyuobject['figure'].savefig(os.path.join(args['<output_directory>'], 'CategorySubgraphIntersection_'+go_id_string))

        if args['--inclusion_index']:
            from tabulate import tabulate
            inc_index = len(set(uniprot_mapping[location]).intersection(set(gocats_mapping[location])))/len(uniprot_mapping[location])
            if godag_dict is None:
                inc_index_table.append([location, inc_index, set(gocats_mapping[location]), len(uniprot_mapping[location])])
            else:
                inc_index_table.append([go_id_string, location, inc_index, len(gocats_mapping[location]), len(uniprot_mapping[location])])

    if args['--inclusion_index']:
        if godag_dict_loaded is False:
            print('Subdag inclusion indices for GOcats and UniProt CV locations: ', '\n',
                  tabulate(inc_index_table, headers=['Location', 'Inclusion Index', 'GC subgraph size', 'UP subgraph size']))
        else:
            print('Subdag inclusion indices for GOcats and UniProt CV locations: ', '\n',
                  tabulate(sorted(inc_index_table, key=lambda x: x[0]), headers=['Location', 'GO term', 'Inclusion Index', 'GC subgraph size', 'UP subgraph size']))

if __name__ == '__main__':
    args = docopt.docopt(__doc__, version='OboCats 0.0.1')
    main(args)
