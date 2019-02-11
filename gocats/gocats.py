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
import jsonpickle
from . import ontologyparser
from . import godag
from . import subdag
from . import tools
from . import _version

jsonpickle.set_encoder_options('json', sort_keys=True, indent=2)
__version__ = _version.__version__


def json_format_graph(graph_object, graph_identifier):
    "Creates a dictionary representing the edges in the graph and formats it in such a way that it can be encoded into JSON for comparing the graph objects between versions of GOcats."
    json_dict = dict()

    for edge in graph_object.edge_list:
        json_dict[str(graph_identifier)+'_'+edge.json_edge[0]] = edge.json_edge[1]

    return json_dict


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


def build_graph_interpreter(database_file, supergraph_namespace=None, allowed_relationships=None, relationship_directionality='gocats'):
    """Creates a graph object of GO, which can be traversed and queried within a Python interpreter.

    :param file_handle database_file: Ontology database file.
    :param str supergraph_namespace: Optional - Filter graph to a sub-ontology namespace.
    :param list allowed_relationships: Optional - Filter graph to use only those relationships listed.
    :param relationship_directionality: Optional - Any string other than 'gocats' will retain all original GO relationship directionalities. Defaults to reverseing has_part direction.
    :return: A Graph object of the ontology provided.
    :rtype: :py:obj:`class`
    """
    database = open(database_file, 'r')
    graph = godag.GoGraph(supergraph_namespace, allowed_relationships)
    go_parser = ontologyparser.GoParser(database, graph, relationship_directionality=relationship_directionality)
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
    :param --go-basic-scoping: OPTIONAL-Creates a GO graph similar to go-basic with only scoping-type relationships (is_a and part_of).
    :param --network_table_name=<None>: OPTIONAL-Make a specific name for the network table produced from the subgraphs (defaults to NetworkTable.csv)
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
    if args['--go-basic-scoping']:
        supergraph_relationships = ['is_a', 'part_of']
        subgraph_relationships = ['is_a', 'part_of']
    if args['--test']:
        test = True
    else:
        test = False

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
            subgraph_collection[subgraph_name] = subdag.SubGraph.from_filtered_graph(supergraph, subgraph_name, keyword_list, subgraph_namespace, subgraph_relationships)

    # Handling superset mapping
    if not args['--map_supersets']:
        category_subsets = find_category_subsets(subgraph_collection)
    else:
        print("NOTE: supersets were mapped.")
        category_subsets = None

    collection_id_mapping = dict()
    collection_node_mapping = dict()
    collection_content_mapping = dict()
    for subgraph_name, subgraph in subgraph_collection.items():
        for node_id, category_node_id in subgraph.root_id_mapping.items():
            try:
                collection_id_mapping[node_id].update([category_node_id])
            except KeyError:
                collection_id_mapping[node_id] = set([category_node_id])
        for node, category_node in subgraph.root_node_mapping.items():
            try:
                collection_node_mapping[node].update(category_node)
            except KeyError:
                collection_node_mapping[node] = {category_node}
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
                           [node.name for node in subgraph.category_node.child_node_set], len(subgraph.node_list) - subgraph.seeded_size,
                           len(subgraph.node_list) - len(subgraph.root_id_mapping.keys()),
                           len(subgraph.root_id_mapping.keys()))
            report_file.write(out_string)

    # FIXME: cannot json save due to recursion of objects within objects...
    # tools.jsonpickle_save(collection_node_mapping, os.path.join(args['<output_directory>'], "GC_node_mapping"))

    if args['--network_table_name']:
        network_table_name = args['--network_table_name']
    else:
        network_table_name = "Network_table.csv"

    # Making a file for network visualization via Cytoscape 3.0
    with open(os.path.join(args['<output_directory>'], network_table_name), 'w', newline='') as network_table:
        edgewriter = csv.writer(network_table, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for term_id, root_id_list in collection_id_mapping.items():
            for root_id in root_id_list:
                edgewriter.writerow([term_id, root_id])

    if test:
        json_graph_destination_file = os.path.join(args['<output_directory>'], str(__version__)+'_graph_output.json')
        with open(json_graph_destination_file, 'w') as destfile:
            destfile.write(jsonpickle.encode(json_format_graph(supergraph, 'supergraph')))
            for subgraph_name, subgraph in subgraph_collection.items():
                destfile.write(jsonpickle.encode(json_format_graph(subgraph, subgraph_name)))

        jsonpickle_supergraph_destination_file = os.path.join(args['<output_directory>'], str(__version__)+'_supergraph_output.jsonpickle')
        jsonpickle_clean_graph(supergraph)
        with open(jsonpickle_supergraph_destination_file, 'w') as destfile:
            destfile.write(jsonpickle.encode(supergraph))

        for subgraph_name, subgraph in subgraph_collection.items():
            jsonpickle_clean_graph(subgraph)
            jsonpickle_subgraph_destination_file = os.path.join(args['<output_directory>'], str(__version__)+'_'+subgraph_name+'_output.jsonpickle')
            with open(jsonpickle_subgraph_destination_file, 'w') as destfile:
                destfile.write(jsonpickle.encode(subgraph))


def jsonpickle_clean_graph(graph):
    # remove circular references from the nodes
    for node in graph.node_list:
        node.edges = None
        if node.parent_node_set:
            node.parent_node_set = sorted([str(node2.id) for node2 in node.parent_node_set])
        if node.child_node_set:
            node.child_node_set = sorted([str(node2.id) for node2 in node.child_node_set])
        if node._descendants:
            node._descendants = sorted([str(node2.id) for node2 in node._descendants])
        if node._ancestors:
            node._ancestors = sorted([str(node2.id) for node2 in node._ancestors])

    # remove sets or unneeded references from the graph
    if hasattr(graph, "super_graph") and graph.super_graph:
        graph.super_graph = None
    if graph._orphans:
        graph._orphans = sorted([str(node2.id) for node2 in graph._orphans])
    if graph._leaves:
        graph._leaves = sorted([str(node2.id) for node2 in graph._leaves])
    for vocab in graph.vocab_index:
        graph.vocab_index[vocab] = sorted([str(node2.id) for node2 in graph.vocab_index[vocab]])
    if graph.used_relationship_set:
        graph.used_relationship_set = sorted([relationship for relationship in graph.used_relationship_set])


# TODO: the workaround for accessing the sole item in the set here is hacky, fix this later.
def find_category_subsets(subgraph_collection):
    """Finds subgraphs which are subsets of other subgraphs to remove redundancy, when specified.

    :param subgraph_collection: A dictionary of subgraph objects (keys: subgraph name, values: subgraph object).
    :return: A dictionary relating which subgraph objects are subsets of other subgraphs (keys: subset subgraph, values: superset subgraphs).
    :rtype: :py:obj:`dict`
    """
    is_subset_of = dict()
    for subgraph in subgraph_collection.values():
        for next_subgraph in subgraph_collection.values():
            if len(subgraph.category_node.child_node_set) == 1 and len(next_subgraph.category_node.child_node_set) == 1:
                if next(iter(subgraph.category_node.child_node_set)).id != next(iter(next_subgraph.category_node.child_node_set)).id and next(iter(subgraph.category_node.child_node_set)).id in next_subgraph.root_id_mapping.keys():
                    try:
                        is_subset_of[next(iter(subgraph.category_node.child_node_set)).id].add(next(iter(next_subgraph.category_node.child_node_set)).id)
                    except KeyError:
                        is_subset_of[next(iter(subgraph.category_node.child_node_set)).id] = {next(iter(next_subgraph.category_node.child_node_set)).id}
    return is_subset_of


def categorize_dataset(args):
    """Reads in a Gene Annotation File (GAF) and maps the annotations contained therein to the categories organized by
    GOcats or other methods. Outputs a mapped GAF and a list of unmapped genes in the specified output directory.

    :param dataset_file: A file containing gene annotations.
    :param term_mapping: A dictionary mapping category-defining ontology terms to their subgraph children terms. May be produced by GOcats or another method.
    :param output_directory: Specify the directory where the output file will be stored.
    :param mapped_dataset_filename: Specify the desired name of the mapped GAF.
    :param --dataset_type: Enter file type for dataset [GAF|TSV|CSV]. Defaults to GAF.
    :param --entity_col=<0>: If CSV or TSV file type, indicate which column the entity IDs are listed. Defaults to 0.
    :param --go_col: If CSV or TSV file type, indicate which column the GO IDs are listed. Defaults to 1.
    :param --retain_unmapped_annotations: If specified, annotations that are not mapped to a concept are copied into the mapped dataset output file with its original annotation.
    :return: None
    :rtype: :py:obj:`None`
    """
    if args['--dataset_type']:
        dataset_type = args['--dataset_type']
    else:
        dataset_type = None
    if args['--entity_col']:
        entity_id_index = int(args['--entity_col'])
    else:
        entity_id_index = 0
    if args['--go_col']:
        go_id_index = int(args['--go_col'])
    else:
        go_id_index = 1

    mapping_dict = tools.jsonpickle_load(args['<term_mapping>'])
    output_directory = os.path.realpath(args['<output_directory>'])
    mapped_dataset_filename = args['<mapped_dataset_filename>']
    unmapped_entities = set()
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    if dataset_type == "GAF" or not dataset_type:
        loaded_gaf_array = tools.parse_gaf(args['<dataset_file>'])
        mapped_gaf_array = list()
        for line in loaded_gaf_array:
            if line[4] in mapping_dict.keys():
                mapped_terms = mapping_dict[line[4]]
                for term in mapped_terms:
                    mapped_gaf_array.append(line[0:4] + [term] + line[5:-1])
            else:
                if line[2] == '':
                    unmapped_entities.add('NO_GENE:' + line[1])
                else:
                    unmapped_entities.add(line[2])
        tools.write_out_gaf(mapped_gaf_array, os.path.join(output_directory, mapped_dataset_filename))
        tools.list_to_file(os.path.join(output_directory, mapped_dataset_filename + '_unmappedEntities'), unmapped_entities)

    elif dataset_type == "CSV":
        mapped_rows = []
        with open(os.path.realpath(args['<dataset_file>']), 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)
            for row in csv_reader:
                mapped_row = row
                if mapped_row[go_id_index] in mapping_dict.keys():
                    for concept_term in mapping_dict[mapped_row[go_id_index]]:
                        mapped_row[go_id_index] = concept_term
                        mapped_rows.append(mapped_row)
                else:
                    unmapped_entities.add(mapped_row[entity_id_index])
                    if args['--retain_unmapped_annotations']:
                        mapped_rows.append(mapped_row)
            mapped_rows.insert(0, header)
        with open(os.path.join(output_directory, mapped_dataset_filename), 'w') as output_csv:
            csv_writer = csv.writer(output_csv, delimiter=',')
            for row in mapped_rows:
                csv_writer.writerow([item for item in row])
        tools.list_to_file(os.path.join(output_directory, 'unmappedEntities'), unmapped_entities)
