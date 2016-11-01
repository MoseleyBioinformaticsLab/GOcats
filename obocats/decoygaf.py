# !/usr/bin/python3
"""Decoy GAF maker

Usage:
    decoygaf.py make_decoy <ontology_term_list> <output_file>
    decoygaf.py map_terms <mapped_gaf> <output_file>

"""
import docopt
import csv
import re
import tools
import json


def main(args):
    if args['make_decoy']:
        make_decoy(args)
    elif args['map_terms']:
        map_terms(args)


def make_decoy(args):
    """Map2Slim does not output a mapping file relating to how it assigns specific terms to the root that it maps to in
    the GO slim. We can get around this by creating a fake GAF that has the annotated GO term as the ID of the "gene"
    and maintain its annotated GO term. The GAF will contain a single instance of a GO term for each term in the
    sub-ontology. We can then map this phony gaf using the slim of our choice and the resulting mapped GAF can be parsed
    to create the mapping we desire.
    """
    line_format = "UniProtKB	R4GNC1	SRP72		GO:0005737	GO_REF:0000052	IDA		C	Signal recognition particle subunit SRP72	R4GNC1_HUMAN	protein	taxon:9606	20101115	HPA	"  # Random GAF line used for formatting purposes
    line_array = re.split('\t', line_format)

    go_terms = tools.json_load(args['<ontology_term_list>'])

    with open(args['<output_file>'], 'w') as gaf_file:
        gafwriter = csv.writer(gaf_file, delimiter='\t')
        for term in go_terms:
            fake_line = line_array[0:1]+[term]+line_array[2:4]+[term]+line_array[5:-1]
            gafwriter.writerow(fake_line)


def map_terms(args):
    term_mapping = {}
    with open(args['<mapped_gaf>'], 'r') as gaf_file:
        for line in csv.reader(gaf_file, delimiter='\t'):
            if len(line) > 1:
                if line[4] in term_mapping.keys():
                    term_mapping[line[4]].append(line[1])
                else:
                    term_mapping[line[4]] = [line[1]]
    tools.json_save(term_mapping, args['<output_file>'])

    tools.json_save(set(term_mapping['GO:0005886']), "/mlab/data/eugene/M2S_PlasmaMembrane_subgraph")
    with open("/mlab/data/eugene/M2S_PlasmaMembrane_subgraph.json", 'w') as f:
        json.dump(term_mapping['GO:0005886'], f)


if __name__ == '__main__':
    args = docopt.docopt(__doc__, version='GOcats version 2.1.3')
    main(args)
