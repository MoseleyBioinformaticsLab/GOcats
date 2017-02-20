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
    m2s_full_mapping_tuples = jsonpickle.decode(json_str)

full_graph = gocats.build_graph_interpreter(sys.argv[3], allowed_relationships=['is_a', 'part_of', 'has_part'])
cc_graph = gocats.build_graph_interpreter(sys.argv[3], supergraph_namespace='cellular_component', allowed_relationships=['is_a', 'part_of', 'has_part'])
mf_graph = gocats.build_graph_interpreter(sys.argv[3], supergraph_namespace='molecular_function', allowed_relationships=['is_a', 'part_of', 'has_part'])
bp_graph = gocats.build_graph_interpreter(sys.argv[3], supergraph_namespace='biological_process', allowed_relationships=['is_a', 'part_of', 'has_part'])


def all_possible_mappings(node_list):
    node_mapping_tuples = set()
    for node1 in node_list:
        for node2 in node_list:
            if node1 != node2 and node1.ancestors.intersection(node2.descendants):
                node_mapping_tuples.add((node1.id, node2.id))
    return node_mapping_tuples


def erroneous_m2s_tuples(m2s_tuples, gc_tuples):
    return m2s_tuples - m2s_tuples.intersection(gc_tuples)

gc_full_mapping_tuples = all_possible_mappings(full_graph.node_list)
gc_cc_mapping_tuples = all_possible_mappings(cc_graph.node_list)
gc_mf_mapping_tuples = all_possible_mappings(mf_graph.node_list)
gc_bp_mapping_tuples = all_possible_mappings(bp_graph.node_list)

m2s_cc_mapping_tuples = set([tup for tup in m2s_full_mapping_tuples if (tup[0] and tup[1] in cc_graph.id_index.keys())])
m2s_mf_mapping_tuples = set([tup for tup in m2s_full_mapping_tuples if (tup[0] and tup[1] in mf_graph.id_index.keys())])
m2s_bp_mapping_tuples = set([tup for tup in m2s_full_mapping_tuples if (tup[0] and tup[1] in bp_graph.id_index.keys())])

full_m2s_errors = erroneous_m2s_tuples(m2s_full_mapping_tuples, gc_full_mapping_tuples)
cc_m2s_errors = erroneous_m2s_tuples(m2s_cc_mapping_tuples, gc_cc_mapping_tuples)
mf_m2s_errors = erroneous_m2s_tuples(m2s_mf_mapping_tuples, gc_mf_mapping_tuples)
bp_m2s_errors = erroneous_m2s_tuples(m2s_bp_mapping_tuples, gc_bp_mapping_tuples)

print("Full GO\n-------------------------")
print("Number of GOcats mappings: ", len(gc_full_mapping_tuples))
print("Number of m2s mappings for all GO: ", (len(m2s_full_mapping_tuples)))
print("Number of mapping errors: ", len(full_m2s_errors))
print("Ratio of erroneous mappings to correct mappings in full GO: ", (len(full_m2s_errors)/len(gc_full_mapping_tuples)))
print("Number of correct mappings determined by Map2Slim: ", (len(m2s_full_mapping_tuples.intersection(gc_full_mapping_tuples))))

print("CC sub-ontology\n-------------------------")
print("Number of GOcats mappings: ", len(gc_cc_mapping_tuples))
print("Number of m2s mappings for CC: ", (len(m2s_cc_mapping_tuples)))
print("Number of mapping errors: ", len(cc_m2s_errors))
print("Ratio of erroneous mappings to correct mappings in CC: ", (len(cc_m2s_errors)/len(gc_cc_mapping_tuples)))
print("Number of correct mappings determined by Map2Slim: ", (len(m2s_cc_mapping_tuples.intersection(gc_cc_mapping_tuples))))

print("MF sub-ontology\n-------------------------")
print("Number of GOcats mappings: ", len(gc_mf_mapping_tuples))
print("Number of m2s mappings for MF: ", (len(m2s_mf_mapping_tuples)))
print("Number of mapping errors: ", len(mf_m2s_errors))
print("Ratio of erroneous mappings to correct mappings in MF: ", (len(mf_m2s_errors)/len(gc_mf_mapping_tuples)))
print("Number of correct mappings determined by Map2Slim: ", (len(m2s_mf_mapping_tuples.intersection(gc_mf_mapping_tuples))))

print("BP sub-ontology\n-------------------------")
print("Number of GOcats mappings: ", len(gc_bp_mapping_tuples))
print("Number of m2s mappings for BP: ", (len(m2s_bp_mapping_tuples)))
print("Number of mapping errors: ", len(bp_m2s_errors))
print("Ratio of erroneous mappings to correct mappings in BP: ", (len(bp_m2s_errors)/len(gc_bp_mapping_tuples)))
print("Number of correct mappings determined by Map2Slim: ", (len(m2s_bp_mapping_tuples.intersection(gc_bp_mapping_tuples))))
