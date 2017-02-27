#!/usr/bin/python3
"""
Creates a list of tuples from map2slim output files, linking individually 
mapped terms to the root term to which they map.

USAGE: # python3 m2s_pickler <map2slim_output_file>
"""
import jsonpickle
import os
import csv
from sys import argv, maxsize
csv.field_size_limit(maxsize)

m2s_output_path = os.path.abspath(argv[1])
node_mapping_tuples = set()

for subdir in os.listdir(m2s_output_path):
    subdir_path = os.path.join(m2s_output_path, subdir)
    for filename in os.listdir(subdir_path):
        with open(os.path.join(subdir_path, filename), 'r') as gaf_file:
            root = filename
            contents = []
            for line in csv.reader(gaf_file, delimiter='\t'):
                if len(line) > 1:
                    contents.append(line[1])
        for term in contents:
            if term != root:
                node_mapping_tuples.add((term, root))

m2s_output = open('MappingTuplesM2S.json_pickle', 'w')
json_m2s_set = jsonpickle.encode(node_mapping_tuples)
m2s_output.write(json_m2s_set)
m2s_output.close()

