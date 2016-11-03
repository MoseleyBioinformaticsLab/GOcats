# !/usr/bin/python3
""" Open Biomedical Ontologies Categories (OboCats)

Usage:
    obocats build_graph <database_file> <output_file> [--supergraph_namespace=<None>]
    obocats filter_subgraphs <database_file> <keyword_file> <output_directory> [--supergraph_namespace=<None> --subgraph_namespace=<None> --supergraph_relationships=[] --subgraph_relationships=[] --map_supersets --output_termlist --test_subgraph=<None>]
    obocats subgraph_overlap <obocats_mapping> <uniprot_mapping> <map2slim_mapping> <output_directory> [--inclusion_index --id_translation=<filename>]
    obocats subgraph_inclusion <obocats_mapping> <other_mapping> <output_directory> <filename> [--id_translation=<filename>]
    obocats categorize_dataset <gaf_dataset> <term_mapping> <output_directory> <GAF_name>
    obocats compare_mapping <mapped_gaf> <manual_dataset>  [--group_annotations=<None> --save_assignments=<filename> --id_translation=<filename>]
Options:
    -h --help                            Shows this screen.
    --version                            Shows version.
    --supergraph_namespace=<None>        Filters the supergraph to a given namespace.
    --subgraph_namespace=<None>          Filters the subgraph to a given namespace.
    --supergraph_relationships=[]        A provided list will denote which relationships are allowed in the supergraph.
    --subgraph_relationships=[]          A provided list will denote which relationships are allowed in the subgraph.
    --map_supersets                      Maps all terms to all root nodes, regardless of if a root node supercedes another.
    --output_termlist                    Outputs a list of all terms in the supergraph as a JsonPickle file in the output directory.
    --test_subgraph=<None>               Enter a GO ID to output information describing the mapping differences between OBOcats and Map2Slim.
    --output_idtranslation               Outputs a dictionary mapping of ontology IDs to their names. 
    --inclusion_index                    Calculates inclusion index of terms between categories among separate mapping sources.
    --group_annotations=<union>          Choose how to group multiple UniProt annotations (union|intersection) [default=union]
    --save_assignments=<filename>        Save a file with all genes and their GO assignments.
    --id_translation=<filename>          Specify an id_translation file to associate go terms with their English names.

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
    elif args['subgraph_inclusion']:
        subgraph_inclusion(args)
    elif args['categorize_dataset']:
        categorize_dataset(args)
    elif args['compare_mapping']:
        compare_mapping(args)

# Need a SubGraphCollection object
# FIXME: JsonPickle is reaching max recusion depth because of the fact that objects point to each gitother a lot.  
def build_graph(args):
    if args['--supergraph_namespace']:
        supergraph_namespace = args['--supergraph_namespace']
    else:
        supergraph_namespace = None
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

    #print("JsonPickle saving GO object")
    #tools.json_save(graph, os.path.join(output_directory, "{}_{}".format(database_name[:-4], date.today())))
 
def build_graph_interpreter(database_file, supergraph_namespace=None, allowed_relationships=None):
    database = open(database_file, 'r')
    graph = godag.GoGraph(supergraph_namespace, allowed_relationships)
    go_parser = parser.GoParser(database, graph)
    go_parser.parse()
    database.close()
    graph.connect_nodes()
    return graph

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
    #TODO: do the same for node_object_mapping 

    tools.json_save(collection_id_mapping, os.path.join(args['<output_directory>'], "OC_id_mapping"))
    tools.json_save(collection_content_mapping, os.path.join(args['<output_directory>'], "OC_content_mapping"))
    with open(os.path.join(output_directory, 'subgraph_report.txt'), 'w') as report_file:
        report_file.write('Subgraph data\nSupergraph filter: {}\nSubgraph filter: {}\nGO terms in the supergraph: {}\nGO terms in subgraphs: {}\nRelationship prevalence: {}'.format(supergraph_namespace, subgraph_namespace,len(set(supergraph.node_list)), len(set(collection_id_mapping.keys())), supergraph.relationship_count))
        for subgraph_name, subgraph in subgraph_collection.items():
            out_string = """
                -------------------------
                {}
                Subgraph relationships: {}
                Seeded size: {}
                Representitive node: {}
                Nodes added: {}
                Non-subgraph hits (orphans): {}
                Total nodes: {}
                """.format(subgraph_name, subgraph.relationship_count, subgraph.seeded_size, subgraph.representative_node.name, len(subgraph.node_list) - subgraph.seeded_size, len(subgraph.node_list) - len(subgraph.root_id_mapping.keys()), len(subgraph.root_node_mapping.keys()))
            report_file.write(out_string)
    # FIXME: 
    # tools.json_save(collection_node_mapping, os.path.join(args['<output_directory>'], "OC_node_mapping"))

    # Making a file for network visualization via Cytoscape 3.0
    with open(os.path.join(args['<output_directory>'], "NetworkTable.csv"), 'w', newline='') as network_table:
        edgewriter = csv.writer(network_table, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for term_id, root_id_list in collection_id_mapping.items():
            for root_id in root_id_list:
                edgewriter.writerow([term_id, root_id])

    if args['--test_subgraph']:
        oc_subgraph_set = next(subgraph.representative_node.descendants for subgraph in subgraph_collection if subgraph.representative_node == args['--test_subgraph'])
        output_mapping_differences(supergraph, oc_subgraph_set, output_dir)

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

def subgraph_inclusion(args):
    from tabulate import tabulate
    inc_index_table = []
    output_file = args['<output_directory>']
    obocats_mapping = tools.json_load(args['<obocats_mapping>'])
    other_mapping = tools.json_load(args['<other_mapping>'])
    if args['--id_translation']:
        id_translation_dict = tools.json_load(args['--id_translation'])
    else:
        id_translation_dict = None
    shared_locations = set(other_mapping.keys()).intersection(set(obocats_mapping.keys()))
    for location in shared_locations:
        if id_translation_dict:
            go_id_string = id_translation_dict[location]
        else:
            go_id_string = location
        inc_index = len(set(other_mapping[location]).intersection(set(obocats_mapping[location])))/len(other_mapping[location])
        jaccard_index = len(set(other_mapping[location]).intersection(set(obocats_mapping[location])))/len(set(other_mapping[location]).union(set(obocats_mapping[location])))
        inc_index_table.append([go_id_string, location, inc_index, jaccard_index, len(obocats_mapping[location]), len(other_mapping[location])])
    table = tabulate(sorted(inc_index_table, key=lambda x: x[0]), headers=['Location', 'GO term', 'Inclusion Index', 'Jaccard Index', 'GC subgraph size', 'Other subgraph size'])
    with open(os.path.join(output_file, args['<filename>']), 'w') as outfile:
        outfile.write(table)

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

def categorize_dataset(args):
    loaded_gaf_array = tools.parse_gaf(args['<gaf_dataset>'])
    mapping_dict = tools.json_load(args['<term_mapping>'])
    output_directory = os.path.realpath(args['<output_directory>'])
    gaf_name = args['<GAF_name>']
    mapped_gaf_array = []
    unmapped_genes = set()

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for line in loaded_gaf_array:
        if line[4] in mapping_dict.keys():
            mapped_terms = mapping_dict[line[4]]
            for term in mapped_terms:
                mapped_gaf_array.append(line[0:4]+[term]+line[5:-1])
        else:
            if line[2] == '':
                unmapped_genes.add('NO_GENE:'+line[1])
            else:
                unmapped_genes.add(line[2])
    tools.writeout_gaf(mapped_gaf_array, os.path.join(output_directory, gaf_name))
    tools.list_to_file(os.path.join(output_directory, gaf_name+'_unmappedGenes'), unmapped_genes)

def compare_mapping(args):
    """Compares the agreement in annotation assignment between a GAF produced by Obcats (PARAMETER <mapped_gaf>) and
    a gold-standard dataset, provided in csv format (PARAMETER <manual-dataset>)."""
    from tabulate import tabulate
    import catcompare

    mapped_dataset_gaf_dict = tools.make_gaf_dict(args['<mapped_gaf>'], keys='db_object_symbol')
    hpa_dataset_dict = catcompare.make_dataset_dict(os.path.realpath(args['<manual_dataset>']), True, 'new', 'Supportive')
    location_breakdown_table = []
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    comparison_results = {}
    gene_assignment_tuples = []
    gene_annotation_not_in_knowledgebase = set()

    def compare_entry(object_symbol, raw_data_go_set, knowledgebase_go_set, comparison_results):

        if raw_data_go_set.union(knowledgebase_go_set) == raw_data_go_set.intersection(knowledgebase_go_set):  # and len(raw_data_go_set.union(knowledgebase_go_set)) != 0:  EDIT should this ever happen? Correctly not-assigning non-assignments demonstrates accuracy. However these cases are non-informative.
            comparison_results[object_symbol] = 'complete'
            return
        elif len(raw_data_go_set.intersection(knowledgebase_go_set)) == 0 and (len(raw_data_go_set) > 0 or len(knowledgebase_go_set) > 0):
            comparison_results[object_symbol] = 'none'
            return
        elif 0 < len(raw_data_go_set.intersection(knowledgebase_go_set)) < len(raw_data_go_set.union(knowledgebase_go_set)):
            comparison_results[object_symbol] = 'partial'
            if knowledgebase_go_set.issuperset(raw_data_go_set):
                comparison_results[object_symbol] = 'superset'
                return
        else:
            comparison_results[object_symbol] = 'inconclusive (missing annotations)'
            return

    for gene_name, go_set in hpa_dataset_dict.items():
        if gene_name in mapped_dataset_gaf_dict.keys():
            #print(gene_name, go_set, mapped_dataset_gaf_dict[gene_name])
            compare_entry(gene_name, go_set, mapped_dataset_gaf_dict[gene_name], comparison_results)
            gene_assignment_tuples.append((gene_name, sorted(go_set), sorted(hpa_dataset_dict[gene_name]), comparison_results[gene_name]))  # Saving gene assignments prior to set evaluation.
        else:
            comparison_results[gene_name] = 'not in knowledgebase'
            gene_assignment_tuples.append((gene_name, sorted(go_set), set(), comparison_results[gene_name]))

    if args['--id_translation']:
        id_translation_dict = tools.json_load(args['--id_translation'])
    else: 
        id_translation_dict = None

    #shows a breakdown of agreement per location (annoataion category)
    for location in set([item for sublist in hpa_dataset_dict.values() for item in sublist]):  # A flattening of the list of lists in hpa dataset dict locations. HPA dataset locaitons should be used as opposed to mapping methods' locations because we want to account for ALL locations involved. These are all of the locations mapped in GO slims and in the Category file. There might be cases in which the mapping methods didnt find an assignment for a particular location in the knowledgebase, this would exclude a category from making it to this list.
        complete = len(list(filter(lambda x: x[3] == 'complete' and (location in x[1] and location in x[2]), gene_assignment_tuples)))
        partial = len(list(filter(lambda x: x[3] == 'partial' and (location in x[1] and location in x[2]), gene_assignment_tuples)))
        superset = len(list(filter(lambda x: x[3] == 'superset' and (location in x[1] and location in x[2]), gene_assignment_tuples)))
        none = len(list(filter(lambda x: x[3] == 'none' and (location in x[1] or location in x[2]), gene_assignment_tuples)))
        missing_annotations = len(list(filter(lambda x: x[3] == 'inconclusive (missing annotations)' and (location in x[1] or location in x[2]), gene_assignment_tuples)))
        not_in_knowledgebase = len(list(filter(lambda x: x[3] == 'not in knowledgebase' and (location in x[1] or location in x[2]), gene_assignment_tuples)))

        if id_translation_dict:
            location_name = id_translation_dict[location]
        else:
            location_name = location
        location_breakdown_table.append([location_name, complete, partial, superset, none, missing_annotations, not_in_knowledgebase])
    
    print('Number of genes with go location assignments per agreement type (compared with raw data)', '\n', tabulate(sorted(location_breakdown_table), headers=['Location', 'Complete', 'Partial', 'Superset', 'None', 'Missing Annotations', 'Not in Knowledgebase']))

    #  Shows a breakdown of genes in each agreement category
    complete = 0
    partial = 0
    superset = 0
    no_match = 0
    missing_annotations = 0
    not_in_knowledgebase = 0
    for category in comparison_results.values():
        if category is 'complete':
            complete += 1
        elif category is 'partial':
            partial += 1
        elif category is 'superset':
            superset += 1
        elif category is 'none':
            no_match += 1
        elif category is 'inconclusive (missing annotations)':
            missing_annotations += 1
        elif category is 'not in knowledgebase':
            not_in_knowledgebase += 1
    print('complete: ', complete, '\n', 'partial: ', partial, '\n', 'superset: ', superset, '\n', 'none: ', no_match, '\n', 'missing_annotations: ', missing_annotations, '\n', 'not in knowledgebase: ', not_in_knowledgebase, '\n', 'Total: ', complete+partial+superset+no_match+missing_annotations+not_in_knowledgebase)

    if args['--save_assignments']:
        file_name = args['--save_assignments']
        tools.list_to_file(file_name, sorted(gene_assignment_tuples, key=lambda gene_id: gene_id[0]))

#Fix this to output the results that were output in commit 1b1fd28f630e24909c193f4ed8c1285f62300441. I do not have time to mess with this right now. Get rid of all of the hardcoding.
def output_mapping_differences(obocats_graph, subgraph, output_dir):
    gc_subgraph = subgraph
    m2s_pm = input("Enter the file location of the subgraph equivalent to ")
    go_depth_dict = tools.json_load("/mlab/data/eugene/GODepthDict.json_pickle")

    not_in_gc = m2s_pm - m2s_pm.intersection(gc_pm)
    print(len(not_in_gc))
    missing_node_depths = []
    m2s_descendants_not_in_gc = set()
    for go_id in not_in_gc:
        supergraph_descendants = set([node.id for node in supergraph.id_index[go_id].descendants])
        m2s_descendants_not_in_gc.update(supergraph_descendants.intersection(m2s_pm))
        missing_node_depths.append((go_depth_dict[go_id], go_id, len(supergraph_descendants.intersection(m2s_pm)), len(supergraph_descendants.intersection(gc_pm))))
    print(sorted(missing_node_depths, key=lambda depth: depth[0]))
    print(len(m2s_descendants_not_in_gc))
    print("descendants of 'unencapsulated part of cell' that are in m2s but not in go cats\n", [node.id for node in supergraph.id_index['GO:0097653'].descendants if node.id in m2s_pm and node.id not in gc_pm])
    print(len([node.id for node in supergraph.id_index['GO:0097653'].descendants if node.id in m2s_pm and node.id not in gc_pm]))
    print(len(not_in_gc))


if __name__ == '__main__':
    args = docopt.docopt(__doc__, version='OboCats 0.2.0')
    main(args)
