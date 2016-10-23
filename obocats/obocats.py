# !/usr/bin/python3
""" Open Biomedical Ontologies Categories (OboCats)

Usage:
    obocats filter_subgraphs <database_file> <keyword_file> <output_directory> [--supergraph_namespace=<None> --subgraph_namespace=<None> --supergraph_relationships=[] --subgraph_relationships=[] --map_supersets --output_termlist --output_idtranslation]
    obocats subgraph_overlap <obocats_mapping> <uniprot_mapping> <map2slim_mapping> <output_directory> [--inclusion_index]
    obocats categorize_dataset <gaf_dataset> <term_mapping> <output_directory> <GAF_name>
    obocats compare_mapping <mapped_gaf> <manual_dataset> [--group_annotations=<None>] [--save_assignments=<filename>]
Options:
    -h --help                            Shows this screen.
    --version                            Shows version.
    --supergraph_namespace=<None>        Filters the supergraph to a given namespace.
    --subgraph_namespace=<None>          Filters the subgraph to a given namespace.
    --supergraph_relationships=[]        A provided list will denote which relationships are allowed in the supergraph.
    --subgraph_relationships=[]          A provided list will denote which relationships are allowed in the subgraph.
    --map_supersets                      Maps all terms to all root nodes, regardless of if a root node supercedes another.
    --output_termlist                    Outputs a list of all terms in the supergraph as a JsonPickle file in the output directory.
    --output_idtranslation               Outputs a dictionary mapping of ontology IDs to their names. 
    --inclusion_index                    Calculates inclusion index of terms between categories among separate mapping sources.
    --group_annotations=<union>          Choose how to group multiple UniProt annotations (union|intersection) [default=union]
    --save_assignments=<filename>        Save a file with all genes and their GO assignments.

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
    elif args['categorize_dataset']:
        categorize_dataset(args)
    elif args['compare_mapping']:
        compare_mapping(args)

# Need a SubGraphCollection object

# FIXME: JsonPickle is reaching max recusion depth because of the fact that objects point to each gitother a lot.  
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
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
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
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    database_name = os.path.basename(args['<database_file>'])
    graph_class = {'go.obo': godag.GoGraph(supergraph_namespace, supergraph_relationships)}
    supergraph = graph_class[database_name]
    parsing_class = {'go.obo': parser.GoParser(database, supergraph)}
    parsing_class[database_name].parse()

    if args['--output_termlist']:
        tools.json_save(list(supergraph.id_index.keys()), os.path.join(args['<output_directory>'], "termlist"))

    if args['--output_idtranslation']:
        idtranslation = dict()
        for id, node in supergraph.id_index.items():
            idtranslation[id] = node.name
        tools.json_save(idtranslation, os.path.join(args['<output_directory>'], "idtranslation"))

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
        print("I mapped supersets")
        category_subsets = None

    collection_id_mapping = dict()
    collection_node_mapping = dict()
    collection_content_mapping = dict()
    for subgraph in subgraph_collection.values():
        for node_id, rep_node in subgraph.root_id_mapping.items():
            try:
                collection_id_mapping[node_id].update([rep_node])
            except KeyError:
                collection_id_mapping[node_id] = set([rep_node])
        for node, rep_node in subgraph.root_node_mapping.items():
            try:
                collection_node_mapping[node].update(rep_node)
            except KeyError:
                collection_node_mapping[node] = set([rep_node])
        for rep_node, content in subgraph.content_mapping.items():
            collection_content_mapping[rep_node] = content
    
    # Remove root nodes that are subsets of existing root nodes from mapping
    if category_subsets:
        for node_id, root_id_list in collection_id_mapping.items():
            for subset_id, superset_ids in category_subsets.items():
                if subset_id in root_id_list:
                    [root_id_list.remove(node) for node in superset_ids if node in root_id_list]
    # do the same for node_object_mapping 

    print(supergraph.relationship_count)
    print(supergraph.used_relationship_set)

    tools.json_save(collection_id_mapping, os.path.join(args['<output_directory>'], "OC_id_mapping"))
    tools.json_save(collection_content_mapping, os.path.join(args['<output_directory>'], "OC_content_mapping"))
    # FIXME: 
    # tools.json_save(collection_node_mapping, os.path.join(args['<output_directory>'], "OC_node_mapping"))

    # Making a file for network visualization via Cytoscape 3.0
    with open(os.path.join(args['<output_directory>'], "NetworkTable.csv"), 'w', newline='') as network_table:
        edgewriter = csv.writer(network_table, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for term_id, root_id_list in collection_id_mapping.items():
            for root_id in root_id_list:
                edgewriter.writerow([term_id, root_id])

def find_category_subsets(subgraph_collection):
    is_subset_of = dict()
    for subgraph in subgraph_collection.values():
        for next_subgraph in subgraph_collection.values():
            if subgraph.representative_node.id != next_subgraph.representative_node.id and subgraph.representative_node.id in next_subgraph.root_id_mapping.keys():
                try:
                    is_subset_of[subgraph.representative_node.id].add(next_subgraph.representative_node.id)
                except KeyError:
                    is_subset_of[subgraph.representative_node.id] = {next_subgraph.representative_node.id}
    return is_subset_of

def subgraph_overlap(args):
    import pandas as pd
    import pyupset as pyu
    if not os.path.exists(args['<output_directory>']):
        os.makedirs(args['<output_directory>'])
 
    inc_index_table = []
    obocats_mapping = tools.json_load(args['<obocats_mapping>'])
    uniprot_mapping = tools.json_load(args['<uniprot_mapping>'])
    map2slim_mapping = tools.json_load(args['<map2slim_mapping>'])

    location_categories = set(list(obocats_mapping.keys())+list(uniprot_mapping.keys())+list(map2slim_mapping.keys()))
    for location in [x for x in location_categories if x not in set(uniprot_mapping.keys()).intersection(*[set(obocats_mapping.keys()), set(map2slim_mapping.keys())])]:
        uniprot_mapping[location] = [location]
    shared_locations = set(uniprot_mapping.keys()).intersection(*[set(obocats_mapping.keys()), set(map2slim_mapping.keys())])
    for location in shared_locations:
        go_id_string = str(location)[3:]
        gc_set = pd.DataFrame({'Terms': obocats_mapping[location]})
        up_set = pd.DataFrame({'Terms': uniprot_mapping[location]})
        m2s_set = pd.DataFrame({'Terms': map2slim_mapping[location]})
        set_dict = {'GOcats': gc_set, 'UniProt': up_set, 'Map2Slim': m2s_set}
        pyuobject = pyu.plot(set_dict, unique_keys=['Terms'])
        pyuobject['figure'].savefig(os.path.join(args['<output_directory>'], 'CategorySubgraphIntersection_'+go_id_string))

        if args['--inclusion_index']:
            from tabulate import tabulate
            inc_index = len(set(uniprot_mapping[location]).intersection(set(obocats_mapping[location])))/len(uniprot_mapping[location])
            if godag_dict is None:
                inc_index_table.append([location, inc_index, set(obocats_mapping[location]), len(uniprot_mapping[location])])
            else:
                inc_index_table.append([go_id_string, location, inc_index, len(obocats_mapping[location]), len(uniprot_mapping[location])])

    if args['--inclusion_index']:
        if godag_dict_loaded is False:
            print('Subdag inclusion indices for GOcats and UniProt CV locations: ', '\n',
                  tabulate(inc_index_table, headers=['Location', 'Inclusion Index', 'GC subgraph size', 'UP subgraph size']))
        else:
            print('Subdag inclusion indices for GOcats and UniProt CV locations: ', '\n',
                  tabulate(sorted(inc_index_table, key=lambda x: x[0]), headers=['Location', 'GO term', 'Inclusion Index', 'GC subgraph size', 'UP subgraph size']))

def categorize_dataset(args):
    loaded_gaf_array = tools.parse_gaf(args['<gaf_dataset>'])
    mapping_dict = tools.json_load(args['<term_mapping>'])
    output_directory = os.path.realpath(args['<output_directory>'])
    gaf_name = args['<GAF_name>']
    mapped_gaf_array = []
    unmapped_genes = []

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for line in loaded_gaf_array:
        if line[4] in mapping_dict.keys():
            mapped_terms = mapping_dict[line[4]]
            for term in mapped_terms:
                mapped_gaf_array.append(line[0:4]+[term]+line[5:-1])
        else:
            unmapped_genes.append(line[1])
    tools.writeout_gaf(mapped_gaf_array, os.path.join(output_directory, gaf_name))
    tools.list_to_file(os.path.join(output_directory, 'UnmappedGenes'), unmapped_genes)

def compare_mapping(args):

    # This method needs to be reworked completely.\
    """Compares the agreement in annotation assignment between a GAF produced by Obcats (PARAMETER <mapped_gaf>) and
    a gold-standard dataset, provided in csv format (PARAMETER <manual-dataset>)."""
    from tabulate import tabulate
    import catcompare
    mapped_gaf_dict = tools.make_gaf_dict(args['<mapped_gaf>'], keys='go_term')
    location_breakdown_table = []
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    comparison_results = {}

    #  TODO: Rename and clean up this method.
    def mini_compare(ensg_id, ensg_go_set, uniprot_go_set, comparison_results):

        if ensg_go_set.union(uniprot_go_set) == ensg_go_set.intersection(uniprot_go_set):  # and len(ensg_go_set.union(uniprot_go_set)) != 0:  EDIT should this ever happen? Correctly not-assigning non-assignments demonstrates accuracy. However these cases are non-informative.
            comparison_results[ensg_id] = 'complete'
            return
        elif len(ensg_go_set.intersection(uniprot_go_set)) == 0:
            comparison_results[ensg_id] = 'none'
            return
        elif 0 < len(ensg_go_set.intersection(uniprot_go_set)) < len(ensg_go_set.union(uniprot_go_set)):
            comparison_results[ensg_id] = 'partial'
            if uniprot_go_set.issuperset(ensg_go_set):
                comparison_results[ensg_id] = 'superset'
                return
            return
    hpa_dataset_dict = catcompare.make_dataset_dict(os.path.realpath(args['<manual_dataset>']), True, 'Supportive')

    ensg_uniprot_mapping = {}
    comment_line = re.compile('^yourlist:\w+')
    comma_match = re.compile('\w+,\w+')
    gene_assignment_tuples = []
    #  TODO this mapping file needs to be an argument and/or have some extensive usage documentation
    with open(str(curr_dir) + '/exampledata/ENSG-UniProtKB_mapping.tab') as tab_file:
        for line in csv.reader(tab_file, delimiter='\t'):
            if not re.match(comment_line, str(line)):
                if re.match(comma_match, line[0]):  # Multiple ENSG IDs for a single Uniprot ID (skipping these)
                    pass
                else:
                    if line[0] in ensg_uniprot_mapping.keys():
                        ensg_uniprot_mapping[line[0]].append(line[1])
                    else:
                        ensg_uniprot_mapping[line[0]] = [line[1]]

    #  TODO clean this up. Maybe separate sub-functions for union and intersection.
    hpa_ensg_id_count = 0
    ensg_in_mapping = 0
    hpa_ensg_not_in_mapping = []
    error_out = []  # List for storing UniProt IDs not found in the mapped GAF knowledge base files.
    for ensg_id, ensg_go_list in hpa_dataset_dict.items():  # HPA_dataset has ENSG IDs not in the mapping file: 39 cases
        if ensg_id not in ensg_uniprot_mapping.keys():
            hpa_ensg_not_in_mapping.append(ensg_id)
        hpa_ensg_id_count += 1
        ensg_go_set = set(ensg_go_list)
        if ensg_id in ensg_uniprot_mapping.keys():
            ensg_in_mapping += 1
            mapped_uniprot_id_list = ensg_uniprot_mapping[ensg_id]
            uniprot_go_list = []
            if args['--group_annotations'] == 'union':
                for uniprot_id in mapped_uniprot_id_list:
                    if uniprot_id in mapped_gaf_dict.keys():
                        uniprot_go_list.extend(mapped_gaf_dict[uniprot_id])
                if uniprot_go_list == []:
                    error_out.extend(mapped_uniprot_id_list)
                uniprot_go_set = set(uniprot_go_list)
            elif args['--group_annotations'] == 'intersection':
                for uniprot_id in mapped_uniprot_id_list:
                    if uniprot_id in mapped_gaf_dict.keys():
                        uniprot_go_list.append(set(mapped_gaf_dict[uniprot_id]))
                if uniprot_go_list == []: # Must be written as '== []' and not 'is []'
                    uniprot_go_set = set()
                else:
                    uniprot_go_set = set.intersection(*uniprot_go_list)  # Asterisk needed. Passes in the sets within the list
            mini_compare(ensg_id, ensg_go_set, uniprot_go_set, comparison_results)  # ensg go list are go assignments from HPA, uniprot go list is go assignment from goCats mapping
            gene_assignment_tuples.append((ensg_id, sorted(mapped_uniprot_id_list), sorted(uniprot_go_set), sorted(ensg_go_set), comparison_results[ensg_id]))  # Saving gene assignments prior to set evaluation.

    for location in set([item for sublist in hpa_dataset_dict.values() for item in sublist]):  # A flattening of the list of lists in hpa dataset dict locations. HPA dataset locaitons should be used as opposed to mapping methods' locations because we want to account for ALL locations involved. These are all of the locations mapped in GO slims and in the Category file. There might be cases in which the mapping methods didnt find an assignment for a particular location in the knowledgebase, this would exclude a category from making it to this list.
        complete = len(list(filter(lambda x: x[4] == 'complete' and (location in x[2] and location in x[3]), gene_assignment_tuples)))
        partial = len(list(filter(lambda x: x[4] == 'partial' and (location in x[2] and location in x[3]), gene_assignment_tuples)))
        superset = len(list(filter(lambda x: x[4] == 'superset' and (location in x[2] and location in x[3]), gene_assignment_tuples)))
        none = len(list(filter(lambda x: x[4] == 'none' and (location in x[2] or location in x[3]), gene_assignment_tuples)))
            
        location_breakdown_table.append([location, complete, partial, superset, none])
    print('Number of genes with go location assignments per agreement type (compared with raw data)', '\n', tabulate(location_breakdown_table, headers=['Location', 'Complete', 'Partial', 'Superset', 'None']))

    #  TODO: Find a new way to do this that is more functional (can be used to access information later.)
    complete = 0
    partial = 0
    superset = 0
    no_match = 0
    for category in comparison_results.values():
        if category is 'complete':
            complete += 1
        elif category is 'partial':
            partial += 1
        elif category is 'superset':
            superset += 1
        elif category is 'none':
            no_match += 1
    print('complete: ', complete, '\n', 'partial: ', partial, '\n', 'superset: ', superset, '\n', 'none: ', no_match, '\n', 'Total: ', complete+partial+superset+no_match)

    if args['--save_assignments']:
        file_name = args['--save_assignments']
        tools.list_to_file(file_name, sorted(gene_assignment_tuples, key=lambda gene_id: gene_id[0]))


if __name__ == '__main__':
    args = docopt.docopt(__doc__, version='OboCats 0.1.1')
    main(args)
