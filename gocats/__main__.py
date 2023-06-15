#!/usr/bin/env python3

"""
The Gene Ontology Categories Suite (GOcats)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides methods for the creation of directed acyclic concept subgraphs of Gene Ontology, along with methods
for evaluating those subgraphs.

Command line implementation::

    Usage:
        gocats create_subgraphs <database_file> <keyword_file> <output_directory> [--supergraph_namespace=<namespace> --subgraph_namespace=<namespace> --supergraph_relationships=<relationships> --subgraph_relationships=<relationships> --network_table_name=<name> --map_supersets --output_termlist --go_basic_scoping --test]
        gocats categorize_dataset <dataset_file> <term_mapping> <output_directory> <mapped_dataset_filename> [--dataset_type=<GAF> --entity_col=<entity> --go_col=<go> --retain_unmapped_annotations]
        gocats remap_goterms <go_database> <goa_gaf> <ancestor_filename> <namespace_filename> [--allowed_relationships=<relationships> --identifier_column=<column>]
        gocats (-h | --help)
        gocats --version

    Options:
        -h --help                                   Shows this screen.
        --version                                   Shows version.
        <database_file>                             GO term database.
        <keyword_file>                              GO term keywords used for finding related GO terms.
        <output_directory>                          Where everything will be saved.
        --supergraph_namespace=<namespace>          Filters the supergraph to a given namespace.
        --subgraph_namespace=<namespace>            Filters the subgraph to a given namespace.
        --supergraph_relationships=<relationships>  Comma separated relationship types defining which allowed in the supergraph. [default: is_a,part_of,has_part]
        --subgraph_relationships=<relationships>    Comma separated relationship types denote which relationships are allowed in the subgraph. [default: is_a,part_of,has_part]
        --network_table_name=<name>                 Custom name for the output NetworkTable.csv to be used with Cytoscape. [default: NetworkTable.csv]
        --map_supersets                             Maps all terms to all root nodes, regardless of if a root node subsumes another.
        --output_termlist                           Outputs a list of all terms in the supergraph as a JsonPickle file in the output directory.
        --go_basic_scoping                          Creates a GO graph similar to go-basic with only scoping-type relationships (is_a and part_of). WARNING, this supersedes relationship definitions.
        <dataset_file>                              A GO dataset file.
        <term_mapping>                              A dictionary mapping category-defining ontology terms to their subgraph children terms. May be produced by GOcats or another method.
        <mapped_dataset_filename>                   The desired name of the mapped GAF.
        --dataset_type=<filetype>                   Enter file type for dataset [GAF|TSV|CSV]. Defaults to GAF. [default: GAF]
        --entity_col=<entity>                       If CSV or TSV file type, indicate which column the entity IDs are listed. Defaults to 0. [default: 0]
        --go_col=<go>                               If CSV or TSV file type, indicate which column the GO IDs are listed. Defaults to 1. [default: 1]
        --retain_unmapped_annotations               If specified, annotations that are not mapped to a concept are copied into the mapped dataset output file with its original annotation.
        <go_database>                               The Gene Ontology file to use
        <goa_gaf>                                   Gene annotation format file
        <ancestor_filename>                         Where to write the JSONized gene to GO Term relationships to
        <namespace_filename>                        Where to save the JSONized GO Term to namespace relationships to
        --allowed_relationships=<relationships>     Comma separated string of term-to-term relationships to allow [default: is_a,part_of,has_part]
        --identifier_column=<column>                Which column has the gene identifiers [default: 1]
        --test                                      Outputs json files to compare versions of GOcats.
"""

import docopt
from . import gocats
from ._version import __version__


def main(args):
    if args['create_subgraphs']:
        database_file = args['<database_file>']
        keyword_file = args['<keyword_file>']
        output_directory = args['<output_directory>']
        if args['--supergraph_namespace']:
            supergraph_namespace = args['--supergraph_namespace']
        else:
            supergraph_namespace = None
        if args['--subgraph_namespace']:
            subgraph_namespace = args['--subgraph_namespace']
        else:
            subgraph_namespace = None
        if args['--supergraph_relationships']:
            supergraph_relationships = args['--supergraph_relationships'].split(",")
        else:
            supergraph_relationships = ["is_a", "part_of", "has_part"]
        if args['--subgraph_relationships']:
            subgraph_relationships = args['--subgraph_relationships'].split(",")
        else:
            subgraph_relationships = ["is_a", "part_of", "has_part"]
        if args['--map_supersets']:
            map_supersets = True
        else:
            map_supersets = False
        if args['--output_termlist']:
            output_termlist = True
        else:
            output_termlist = False
        if args['--go_basic_scoping']:
            go_basic_scoping = True
        else:
            go_basic_scoping = False
        if args['--test']:
            test = True
        
        gocats.create_subgraphs(database_file, keyword_file, output_directory, supergraph_namespace=None, subgraph_namespace=None, supergraph_relationships=['is_a', 'part_of', 'has_part'], subgraph_relationships=['is_a', 'part_of', 'has_part'], map_supersets=False, output_termlist=False, go_basic_scoping=False, network_table_name=None, test=False)

    elif args['categorize_dataset']:
      
        dataset_file = args['<dataset_file>']
        term_mapping = args['<term_mapping>']
        output_directory = args['<output_directory>']
        mapped_dataset_filename = args['<mapped_dataset_filename>']
        
        if args['--dataset_type']:
            dataset_type = args['--dataset_type']
        else:
            dataset_type = "GAF"
        if args['--entity_col']:
            entity_col = int(args['--entity_col'])
        else:
            entity_col = 0
        if args['--go_col']:
            go_col = int(args['--go_col'])
        else:
            go_col = 1
        if args['--retain_unmapped_annotations']:
            retain_unmapped_annotations = True
        else:
            retain_unmapped_annotations = False
        
        gocats.categorize_dataset(dataset_file, term_mapping, output_directory, mapped_dataset_filename, dataset_type, entity_col, go_col, retain_unmapped_annotations)
        
    elif args['remap_goterms']:
        go_database = args['<go_database>']
        goa_gaf = args['<goa_gaf>']
        ancestor_filename = args['<ancestor_filename>']
        namespace_filename = args['<namespace_filename>']
        if args['--allowed_relationships']:
            allowed_relationships = args['--allowed_relationships'].split(",")
        else:
            allowed_relationships = ["is_a", "part_of", "has_part"]
        if args['--identifier_column']:
            identifier_column = int(args['--identifier_column'])
        else:
            identifier_column = 1

        gocats.remap_goterms(go_database, goa_gaf, ancestor_filename, namespace_filename, allowed_relationships, identifier_column)

if __name__ == '__main__':
    args = docopt.docopt(__doc__, help=True, version=str('GOcats Version ') + __version__)
    main(args)
