#!/usr/bin/python3
"""
Parses a gene ontology .obo file and organizes each term into a separate file
within subdirectories of a Map2Slim input directory (./m2sInput).

Organizes up to 500 term files per sub-directory.

Also creates a GAF linking GO terms to themselves. This is necessary for 
creating a mapping of specific GO terms to categories using Map2Slim.

USAGE:
# python3 gotermcollect.py <go.obo> <input_directory>
"""

import os
import re
import csv
from sys import argv

output_dir = os.path.abspath(argv[2])  # The output of this script is the input directory for the remainder of the project.
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Compiles a list of GO terms contained in the provided GO.obo file.
with open(os.path.abspath(argv[1])) as go_file:
    termlist = [re.findall('GO\:\d{7}', line)[0] for line in go_file if re.match('id\:\s+GO\:\d{7}', line)]

# Saves each GO term into separate files.
if os.listdir(output_dir) != []:
    print("--Map2Slim input directory is not empty! Exiting gotermcollect.py")
    exit()
segment_length = 500
segmented_termlist = [termlist[x:x+segment_length] for x in range(0, len(termlist), segment_length)]  # Generator splits the termlist into a list of non-redundant sublists of the terms, each sublist contains 500 of the terms in the list. The remainder are in the last sublist.
for termlist_segment_index in range(len(segmented_termlist)):
    segment_subdir = os.path.join(output_dir, str(termlist_segment_index))
    if not os.path.exists(segment_subdir):
        os.makedirs(segment_subdir)
    for term in segmented_termlist[termlist_segment_index]:
        with open(os.path.join(segment_subdir, str(term)), 'w') as termfile:
            termfile.write(str(term))

# Creates a GAF which associates GO terms to themselves. This allows an evalation of term-to-term mapping from Map2Slim.
gaf_line_format = "UniProtKB	R4GNC1	SRP72		GO:0005737	GO_REF:0000052	IDA		C	Signal recognition particle subunit SRP72	R4GNC1_HUMAN	protein	taxon:9606	20101115	HPA	"  # Placeholder GAF line used for formatting purposes
line_array = re.split('\t', gaf_line_format)
print(line_array)
with open(os.path.join(output_dir, 'GO-GO_GAF.goa'), 'w') as gaf_file:
    gafwriter = csv.writer(gaf_file, delimiter='\t')
    for term in termlist:
        go_go_line = line_array[0:1]+[term]+line_array[2:4]+[term]+line_array[5:-1]
        gafwriter.writerow(go_go_line)
