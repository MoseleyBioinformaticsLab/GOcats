# !/usr/bin/python3
"""
Decoy Gene Annotation File Creator command line implementation::

    Usage:
        decoygaf.py make_decoy <ontology_term_list> <output_dir> <output_file>
        decoygaf.py map_terms <mapped_gaf> <output_dir> <output_file> [--output_mapping_set=<filepath>]
    Options:
        -h --help                            Shows this screen.
        --output_mapping_set=<filepath>      Saves a JSONPickle file of the mapping produced by the module under the provided filepath.
"""
import os
import docopt
import csv
import re
import tools
import json
import version


def main(args):
    if args['make_decoy']:
        make_decoy(args)
    elif args['map_terms']:
        map_terms(args)


def make_decoy(args):
    """Creates a GAF mapping all terms in an ontology to themselves. A GAF formatted file is created which replaces the
     gene name column with a copy of an the ontology term for every term in an ontology. This can be used to create term
     to term mappings via Map2Slim. See `Map2Slim Mapping Error Testing` in the api documentation for elaboration.

    :param ontology_term_list: File produced by :func:`gocats.create_subgraphs` --output_termlist or another .json_pickle file listing all terms in an ontology.
    :param output_dir: Specify the location of the output directory.
    :param output_file: Specify the name of the decoy GAF.
    :return: None
    :rtype: :py:obj:`None`
    """
    line_format = "UniProtKB	R4GNC1	SRP72		GO:0005737	GO_REF:0000052	IDA		C	Signal recognition particle subunit SRP72	R4GNC1_HUMAN	protein	taxon:9606	20101115	HPA	"  # Random GAF line used for formatting purposes
    line_array = re.split('\t', line_format)

    go_terms = tools.jsonpickle_load(args['<ontology_term_list>'])

    with open(os.path.join(args['<output_dir>'], args['<output_file>']), 'w') as gaf_file:
        gafwriter = csv.writer(gaf_file, delimiter='\t')
        for term in go_terms:
            fake_line = line_array[0:1]+[term]+line_array[2:4]+[term]+line_array[5:-1]
            gafwriter.writerow(fake_line)


def map_terms(args):
    """Maps the terms contained in a mapped decoy GAF. The resulting mapping dictionary is saved to a json_pickle. See
    `Map2Slim Mapping Error Testing` in the api documentation for elaboration.

    :param mapped_gaf: A decoy GAF that has been mapped by Map2Slim
    :param output_dir: Specify the location of the output directory.
    :param output_file: Specify the name of the mapping dictionary json_pickle file.
    :param --output_mapping_set=<filepath>: DEPRECIATED-Used for testing purposes, no longer necessary for use.
    :return: None
    :rtype: :py:obj:`None`
    """
    term_mapping = {}
    with open(args['<mapped_gaf>'], 'r') as gaf_file:
        for line in csv.reader(gaf_file, delimiter='\t'):
            if len(line) > 1:
                if line[4] in term_mapping.keys():
                    term_mapping[line[4]].append(line[1])
                else:
                    term_mapping[line[4]] = [line[1]]
    tools.jsonpickle_save(term_mapping, os.path.join(args['<output_dir>'], args['<output_file>']))

    if args['--output_mapping_set']:
        tools.jsonpickle_save(set(term_mapping[args['--output_mapping_set']]), os.path.join(args['<output_dir>'], 'M2S_PlasmaMembrane_subgraph'))
        with open(os.path.join(args['<output_dir>'], 'M2S_PlasmaMembrane_subgraph.json'), 'w') as f:
            json.dump(args['--output_mapping_set'], f)

if __name__ == '__main__':
    args = docopt.docopt(__doc__, version='DecoyGAF Version ' + version.__version__)
    main(args)
