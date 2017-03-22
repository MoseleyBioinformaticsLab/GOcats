# !/usr/bin/python3
"""
The Gene Ontology Categories Suite (GOcats)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides methods for the creation of directed acyclic concept subgraphs of Gene Ontology, along with methods
for evaluating those subgraphs.
"""
import os
import sys
import re
import csv
from . import ontologyparser
from . import godag
from . import subdag
from . import tools


# Need a SubGraphCollection object
def build_graph(args):
    """**Not yet implemented**

    Try build_graph_interpreter to create a GO graph object to explore within a Python interpreter."""
    # FIXME: JsonPickle is reaching max recursion depth because of the fact that objects point to one another.
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
    graph_class = {'go.obo': godag.GoGraph(supergraph_namespace, allowed_relationships)}
    graph = graph_class[database_name]
    parsing_class = {'go.obo': ontologyparser.GoParser(database, graph)}
    parsing_class[database_name].parse()
    database.close()


def build_graph_interpreter(database_file, supergraph_namespace=None, allowed_relationships=None):
    """Creates a graph object of GO, which can be traversed and queried within a Python interpreter.

    :param file_handle database_file: Ontology database file.
    :param str supergraph_namespace: Optional - Filter graph to a sub-ontology namespace.
    :param list allowed_relationships: Optional - Filter graph to use only those relationships listed.
    :return: A Graph object of the ontology provided.
    :rtype: :py:obj:`class`
    """
    database = open(database_file, 'r')
    graph = godag.GoGraph(supergraph_namespace, allowed_relationships)
    go_parser = ontologyparser.GoParser(database, graph)
    go_parser.parse()
    database.close()
    return graph


def create_subgraphs(args):
    """Creates a graph object of an ontology, processed into :class:`gocats.dag.OboGraph` or to an object that
    inherits from :class:`gocats.dag.OboGraph`, and then extracts subgraphs which represent concepts that are defined
    by a list of provided keywords. Each subgraph is processed into :class:`gocats.subdag.SubGraph`.

    :param database_file: Ontology database file.
    :param keyword_file: A CSV file with two columns: column 1 naming categories, and column 2 listing search strings (no quotation marks, separated by semicolons).
    :param output_directory: The directory where results are stored.
    :param --supergraph_namespace=<None>: OPTIONAL-Specify a supergraph sub-ontology to filter e.g. cellular_component.
    :param --subgraph_namespace=<None>: OPTIONAL-Specify a subgraph sub-ontology to filter e.g. cellular_component.
    :param --supergraph_relationships=[]: OPTIONAL-Specify a list of relationships to limit in the supergraph e.g. [is_a, part_of].
    :param --subgraph_relationships=[]: OPTIONAL-Specify a list of relationships to limit in subgraphs e.g. [is_a, part_of].
    :param --map_supersets: OPTIONAL-Allow subgraphs to subsume other subgraphs.
    :param --output_termlist: OPTIONAL-Create a translation of ontology terms to their names to improve interpretability of dev test results.
    :return: None
    :rtype: :py:obj:`None`
    """

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

    # Building the supergraph
    database = open(args['<database_file>'], 'r')
    output_directory = args['<output_directory>']
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    database_name = os.path.basename(args['<database_file>'])
    graph_class = {'go.obo': godag.GoGraph(supergraph_namespace, supergraph_relationships)}
    try:
        supergraph = graph_class[database_name]
    except KeyError:
        print("The provided ontology filename was not recognized. Please do not rename ontology files. The accepted list of file names are as follows: \n", graph_class.keys())
        sys.exit()
    parsing_class = {'go.obo': ontologyparser.GoParser(database, supergraph)}
    try:
        parsing_class[database_name].parse()
    except KeyError:
        print("The provided ontology filename was not recognized. Please do not rename ontology files. The accepted list of file names are as follows: \n", graph_class.keys())
        sys.exit()
    if args['--output_termlist']:
        tools.jsonpickle_save(list(supergraph.id_index.keys()), os.path.join(args['<output_directory>'], "termlist"))

    id_translation = dict()
    for id, node in supergraph.id_index.items():
        id_translation[id] = node.name
    tools.jsonpickle_save(id_translation, os.path.join(args['<output_directory>'], "id_translation"))

    database.close()

    # Building and collecting subgraphs
    subgraph_collection = dict()
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
        print("NOTE: supersets were mapped.")
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
    # TODO: do the same for node_object_mapping

    # Save mapping files and create report
    tools.jsonpickle_save(collection_id_mapping, os.path.join(args['<output_directory>'], "GC_id_mapping"))
    tools.json_save(collection_id_mapping, os.path.join(args['<output_directory>'], "GC_id_mapping"))
    tools.jsonpickle_save(collection_content_mapping, os.path.join(args['<output_directory>'], "GC_content_mapping"))
    tools.json_save(collection_content_mapping, os.path.join(args['<output_directory>'], "GC_content_mapping"))
    with open(os.path.join(output_directory, 'subgraph_report.txt'), 'w') as report_file:
        report_file.write(
            'Subgraph data\nSupergraph filter: {}\nSubgraph filter: {}\nGO terms in the supergraph: {}\nGO terms in subgraphs: {}\nRelationship prevalence: {}'.format(
                supergraph_namespace, subgraph_namespace, len(set(supergraph.node_list)),
                len(set(collection_id_mapping.keys())), supergraph.relationship_count))
        for subgraph_name, subgraph in subgraph_collection.items():
            out_string = """
                -------------------------
                {}
                Subgraph relationships: {}
                Seeded size: {}
                Representative node: {}
                Nodes added: {}
                Non-subgraph hits (orphans): {}
                Total nodes: {}
                """.format(subgraph_name, subgraph.relationship_count, subgraph.seeded_size,
                           subgraph.representative_node.name, len(subgraph.node_list) - subgraph.seeded_size,
                           len(subgraph.node_list) - len(subgraph.root_id_mapping.keys()),
                           len(subgraph.root_node_mapping.keys()))
            report_file.write(out_string)

    # FIXME: cannot json save due to recursion of objects within objects...
    # tools.jsonpickle_save(collection_node_mapping, os.path.join(args['<output_directory>'], "GC_node_mapping"))

    # Making a file for network visualization via Cytoscape 3.0
    with open(os.path.join(args['<output_directory>'], "NetworkTable.csv"), 'w', newline='') as network_table:
        edgewriter = csv.writer(network_table, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for term_id, root_id_list in collection_id_mapping.items():
            for root_id in root_id_list:
                edgewriter.writerow([term_id, root_id])


def find_category_subsets(subgraph_collection):
    """Finds subgraphs which are subsets of other subgraphs to remove redundancy, when specified.

    :param subgraph_collection: A dictionary of subgraph objects (keys: subgraph name, values: subgraph object).
    :return: A dictionary relating which subgraph objects are subsets of other subgraphs (keys: subset subgraph, values: superset subgraphs).
    :rtype: :py:obj:`dict`
    """
    is_subset_of = dict()
    for subgraph in subgraph_collection.values():
        for next_subgraph in subgraph_collection.values():
            if subgraph.representative_node.id != next_subgraph.representative_node.id and subgraph.representative_node.id in next_subgraph.root_id_mapping.keys():
                try:
                    is_subset_of[subgraph.representative_node.id].add(next_subgraph.representative_node.id)
                except KeyError:
                    is_subset_of[subgraph.representative_node.id] = {next_subgraph.representative_node.id}
    return is_subset_of


def categorize_dataset(args):
    """Reads in a Gene Annotation File (GAF) and maps the annotations contained therein to the categories organized by
    GOcats or other methods. Outputs a mapped GAF and a list of unmapped genes in the specified output directory.

    :param gaf_dataset: A Gene Annotation File.
    :param term_mapping: A dictionary mapping category-defining ontology terms to their subgraph children terms. May be produced by GOcats or another method.
    :param output_directory: Specify the directory where the output file will be stored.
    :param GAF_name: Specify the desired name of the mapped GAF.
    :return: None
    :rtype: :py:obj:`None`
    """
    loaded_gaf_array = tools.parse_gaf(args['<gaf_dataset>'])
    mapping_dict = tools.jsonpickle_load(args['<term_mapping>'])
    output_directory = os.path.realpath(args['<output_directory>'])
    gaf_name = args['<GAF_name>']
    mapped_gaf_array = list()
    unmapped_genes = set()

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for line in loaded_gaf_array:
        if line[4] in mapping_dict.keys():
            mapped_terms = mapping_dict[line[4]]
            for term in mapped_terms:
                mapped_gaf_array.append(line[0:4] + [term] + line[5:-1])
        else:
            if line[2] == '':
                unmapped_genes.add('NO_GENE:' + line[1])
            else:
                unmapped_genes.add(line[2])
    tools.write_out_gaf(mapped_gaf_array, os.path.join(output_directory, gaf_name))
    tools.list_to_file(os.path.join(output_directory, gaf_name + '_unmappedGenes'), unmapped_genes)
