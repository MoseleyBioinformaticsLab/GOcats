#/usr/bin/python3
"""
Compares mappings made by Map2Slim to mappings made by GOcats
Used to determine the extent to which evaluating non-scoping
relationships with Map2Slim in a scoping context affects GO 
term mapping errors. 

USAGE: python3 ErrorAnalysis.py <gocats_directory> <map2slim_mapping_file> <GO_file> 
"""
import os
import jsonpickle
import sys
sys.path.append(sys.argv[1])
import gocats

with open(sys.argv[2], 'r') as m2s_file:
    json_str = m2s_file.read()
    m2s_mapping_tuples = jsonpickle.decode(json_str)

full_graph = gocats.build_graph_interpreter(sys.argv[3], allowed_relationships=['is_a','part_of','has_part'])
cc_graph = gocats.build_graph_interpreter(sys.argv[3], supergraph_namespace='cellular_component', allowed_relationships=['is_a','part_of','has_part'])
mf_graph = gocats.build_graph_interpreter(sys.argv[3], supergraph_namespace='molecular_function', allowed_relationships=['is_a','part_of','has_part'])
bp_graph = gocats.build_graph_interpreter(sys.argv[3], supergraph_namespace='biological_process', allowed_relationships=['is_a','part_of','has_part'])

def all_possible_mappings(node_list):
    node_mapping_tuples = set()
    for node1 in node_list:
        for node2 in node_list:
            if node1 != node2 and node1.ancestors.intersection(node2.descendants):
                node_mapping_tuples.add((node1.id, node2.id))
    return node_mapping_tuples

def erroneous_m2s_tuples(m2s_tuples, gc_tuples):
    return m2s_tuples - m2s_tuples.intersection(gc_tuples)

full_mapping_tuples = all_possible_mappings(full_graph.node_list) 
cc_mapping_tuples = all_possible_mappings(cc_graph.node_list)
mf_mapping_tuples = all_possible_mappings(mf_graph.node_list)
bp_mapping_tuples = all_possible_mappings(bp_graph.node_list)

full_m2s_errors = erroneous_m2s_tuples(m2s_mapping_tuples, full_mapping_tuples)
cc_m2s_errors = erroneous_m2s_tuples(m2s_mapping_tuples, cc_mapping_tuples)
mf_m2s_errors = erroneous_m2s_tuples(m2s_mapping_tuples, mf_mapping_tuples)
bp_m2s_errors = erroneous_m2s_tuples(m2s_mapping_tuples, bp_mapping_tuples)

print("Full GO\n-------------------------\n# of mapping errors: {}\n% of erroneous mappings: {}\n# of correct mappings: {}\n# of gocats mappings: {}".format(len(full_m2s_errors), (len(full_m2s_errors)/len(full_mapping_tuples)), (len(m2s_mapping_tuples.intersection(full_mapping_tuples))), len(full_mapping_tuples)))
print("# of m2s mappings for all GO: {}".format(len(m2s_mapping_tuples)))

print("CC ONLY\n-------------------------\n# of mapping errors: {}\n% of erroneous mappings: {}\n# of correct mappings: {}\n# of gocats mappings: {}".format(len(cc_m2s_errors), (len(cc_m2s_errors)/len(cc_mapping_tuples)), (len(m2s_mapping_tuples.intersection(cc_mapping_tuples))), len(cc_mapping_tuples)))

print("MF ONLY\n-------------------------\n# of mapping errors: {}\n% of erroneous mappings: {}\n# of correct mappings: {}\n# of gocats mappings: {}".format(len(mf_m2s_errors), (len(mf_m2s_errors)/len(mf_mapping_tuples)), (len(m2s_mapping_tuples.intersection(mf_mapping_tuples))), len(mf_mapping_tuples)))

print("BP ONLY\n-------------------------\n# of mapping errors: {}\n% of erroneous mappings: {}\n# of correct mappings: {}\n# of gocats mappings: {}".format(len(bp_m2s_errors), (len(bp_m2s_errors)/len(bp_mapping_tuples)), (len(m2s_mapping_tuples.intersection(bp_mapping_tuples))), len(bp_mapping_tuples)))

