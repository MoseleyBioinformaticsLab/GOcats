#!/usr/bin/env python3

"""
The Gene Ontology Categories Suite (GOcats)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides methods for the creation of directed acyclic concept subgraphs of Gene Ontology, along with methods
for evaluating those subgraphs.

Command line implementation::

    Usage:
        gocats create_subgraphs <database_file> <keyword_file> <output_directory> [--supergraph_namespace=<None> --subgraph_namespace=<None> --supergraph_relationships=[] --subgraph_relationships=[] --network_table_name=<None> --map_supersets --output_termlist --go-basic-scoping --test]
        gocats categorize_dataset <dataset_file> <term_mapping> <output_directory> <mapped_dataset_filename> [--dataset_type=<GAF> --entity_col=<0> --go_col=<1> --retain_unmapped_annotations]

    Options:
        -h | --help                          Shows this screen.
        --version                            Shows version.
        --supergraph_namespace=<None>        Filters the supergraph to a given namespace.
        --subgraph_namespace=<None>          Filters the subgraph to a given namespace.
        --supergraph_relationships=[]        A provided list will denote which relationships are allowed in the supergraph.
        --subgraph_relationships=[]          A provided list will denote which relationships are allowed in the subgraph.
        --map_supersets                      Maps all terms to all root nodes, regardless of if a root node subsumes another.
        --output_termlist                    Outputs a list of all terms in the supergraph as a JsonPickle file in the output directory.
        --dataset_type=<GAF>                 Enter file type for dataset [GAF|TSV|CSV]. Defaults to GAF.
        --entity_col=<0>                     If CSV or TSV file type, indicate which column the entity IDs are listed. Defaults to 0.
        --go_col=<1>                         If CSV or TSV file type, indicate which column the GO IDs are listed. Defaults to 1.
        --retain_unmapped_annotations        If specified, annotations that are not mapped to a concept are copied into the mapped dataset output file with its original annotation.
        --go-basic-scoping                   Creates a GO graph similar to go-basic with only scoping-type relationships (is_a and part_of).
        --network_table_name=<None>          Custom name for the output NetworkTable.csv to be used with Cytoscape. Defaults to Network Table.csv
        --test                               Outputs json files to compare versions of GOcats.
"""

import docopt
from . import gocats
from ._version import __version__


def main(args):
    if args['create_subgraphs']:
        gocats.create_subgraphs(args)
    elif args['categorize_dataset']:
        gocats.categorize_dataset(args)

if __name__ == '__main__':
    args = docopt.docopt(__doc__, version=str('GOcats Version ') + __version__)
    main(args)
