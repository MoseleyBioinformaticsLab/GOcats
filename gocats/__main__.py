#!/usr/bin/env python3

"""
The Gene Ontology Categories Suite (GOcats)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides methods for the creation of directed acyclic concept subgraphs of Gene Ontology, along with methods
for evaluating those subgraphs.

Command line implementation:

    Usage:
        gocats categorize_dataset <dataset_file> <term_mapping> <output_directory> <mapped_dataset_filename> [--dataset_type=<GAF> --entity_col=<0> --go_col=<1> --retain_unmapped_annotations]
        gocats remap_goterms <go_database> <goa_gaf> <ancestor_filename> <namespace_filename> [--allowed_relationships=<relationships> --identifier_column=<column>]

    Options:
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
        gocats.create_subgraphs(args)
    elif args['categorize_dataset']:
        gocats.categorize_dataset(args)
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
