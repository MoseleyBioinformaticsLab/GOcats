#!/usr/bin/env python3

"""
The Gene Ontology Categories Suite (GOcats)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides methods for the creation of directed acyclic concept subgraphs of Gene Ontology, along with methods
for evaluating those subgraphs.

Command line implementation::

    Usage:
        gocats create_subgraphs <database_file> <keyword_file> <output_directory> [--supergraph_namespace=<None> --subgraph_namespace=<None> --supergraph_relationships=[] --subgraph_relationships=[] --map_supersets --output_termlist]
        gocats categorize_dataset <gaf_dataset> <term_mapping> <output_directory> <GAF_name>

    Options:
        -h | --help                          Shows this screen.
        --version                            Shows version.
        --supergraph_namespace=<None>        Filters the supergraph to a given namespace.
        --subgraph_namespace=<None>          Filters the subgraph to a given namespace.
        --supergraph_relationships=[]        A provided list will denote which relationships are allowed in the supergraph.
        --subgraph_relationships=[]          A provided list will denote which relationships are allowed in the subgraph.
        --map_supersets                      Maps all terms to all root nodes, regardless of if a root node subsumes another.
        --output_termlist                    Outputs a list of all terms in the supergraph as a JsonPickle file in the output directory.
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
