# !/usr/bin/python3
import obocats
import itertools

cc_graph = obocats.build_graph_interpreter('/mlab/data/databases/GeneOntology/01-12-2016/go.obo', supergraph_namespace='cellular_component')
cc_no_hp_graph = obocats.build_graph_interpreter('/mlab/data/databases/GeneOntology/01-12-2016/go.obo', supergraph_namespace='cellular_component', allowed_relationships=['is_a', 'part_of'])
mf_graph = obocats.build_graph_interpreter('/mlab/data/databases/GeneOntology/01-12-2016/go.obo', supergraph_namespace='molecular_function')
mf_no_hp_graph = obocats.build_graph_interpreter('/mlab/data/databases/GeneOntology/01-12-2016/go.obo', supergraph_namespace='molecular_function', allowed_relationships=['is_a', 'part_of'])
bp_graph = obocats.build_graph_interpreter('/mlab/data/databases/GeneOntology/01-12-2016/go.obo', supergraph_namespace='biological_process')
bp_no_hp_graph = obocats.build_graph_interpreter('/mlab/data/databases/GeneOntology/01-12-2016/go.obo', supergraph_namespace='biological_process', allowed_relationships=['is_a', 'part_of'])

cc_hp_edges = [edge for edge in cc_graph.edge_list if edge.relationship.id == 'has_part']
mf_hp_edges = [edge for edge in mf_graph.edge_list if edge.relationship.id == 'has_part']
bp_hp_edges = [edge for edge in bp_graph.edge_list if edge.relationship.id == 'has_part']

all_cc_nodes = cc_graph.node_list
all_cc_no_hp_nodes = cc_no_hp_graph.node_list
all_mf_nodes = mf_graph.node_list
all_mf_no_hp_nodes = mf_no_hp_graph.node_list
all_bp_nodes = bp_graph.node_list
all_bp_no_hp_nodes = bp_no_hp_graph.node_list


def _potential_false_ancestors(edge):
    """Considering a problematic relationship edge, returns a set of nodes target that could result in a problematic
    mapping"""
    child_ancestors = edge.child_node.ancestors
    child_ancestors.add(edge.child_node)
    parent_ancestors = edge.parent_node.ancestors
    parent_ancestors.add(edge.parent_node)

    return child_ancestors - parent_ancestors


def _potential_false_descendants(edge):
    """Considering a problematic relationsihp edge, returns a set of source nodes that could result in a problematic
    mapping."""
    parent_descendants = edge.parent_node.descendants
    parent_descendants.add(edge.parent_node)
    child_descendants = edge.child_node.descendants
    child_descendants.add(edge.child_node)

    return parent_descendants - child_descendants


def potential_false_mappings(edge_list):
    pmf = set()
    for edge in edge_list:
        pmf.update(set(itertools.product(*[_potential_false_descendants(edge), _potential_false_ancestors(edge)])))
    return pmf


def all_possible_mappings(node_list):
    node_mapping_tuples = set()
    for node1 in node_list:
        for node2 in node_list:
            if node1 != node2 and node1.ancestors.intersection(node2.descendants):
                node_mapping_tuples.add((node1, node2))
    return node_mapping_tuples

# celluar_component
potential_false_cc_hp_mappings = potential_false_mappings(cc_hp_edges)
all_possible_cc_mappings = all_possible_mappings(all_cc_nodes)
all_possible_cc_no_hp_mappings = all_possible_mappings(all_cc_no_hp_nodes)

# molecular_function
potential_false_mf_hp_mappings = potential_false_mappings(mf_hp_edges)
all_possible_mf_mappings = all_possible_mappings(all_mf_nodes)
all_possible_mf_no_hp_mappings = all_possible_mappings(all_mf_no_hp_nodes)  

# biological_process
potential_false_bp_hp_mappings = potential_false_mappings(bp_hp_edges)
all_possible_bp_mappings = all_possible_mappings(all_bp_nodes)
all_possible_bp_no_hp_mappings = all_possible_mappings(all_bp_no_hp_nodes)

print("-----cellular_component-----")
print("Potentially false 'has part' mappings: ", len(potential_false_cc_hp_mappings))
print("All possible mappings: ", len(all_possible_cc_mappings))
print("All possible mappings without 'has part': ", len(all_possible_cc_no_hp_mappings)) 
print("Intersection of possible true mappings and potentially false 'has_part' mappings: ", len(all_possible_cc_mappings.intersection(potential_false_cc_hp_mappings)))

print("-----molecular_function-----")
print("Potentially false 'has part' mappings: ", len(potential_false_mf_hp_mappings))
print("All possible mappings: ", len(all_possible_mf_mappings))
print("All possible mappings withough 'has_part': ", len(all_possible_mf_no_hp_mappings))
print("Intersection of possible true mappings and potentially false 'has_part' mappings: ", len(all_possible_mf_mappings.intersection(potential_false_mf_hp_mappings)))

print("-----biological_process-----")
print("Potentially false 'has part' mappings: ", len(potential_false_bp_hp_mappings))
print("All possible mappings: ", len(all_possible_bp_mappings))
print("All possible mappings without 'has_part': ", len(all_possible_bp_no_hp_mappings))
print("Intersection of possible true mappings and potentially false 'has_part' mappings: ", len(all_possible_bp_mappings.intersection(potential_false_bp_hp_mappings)))

