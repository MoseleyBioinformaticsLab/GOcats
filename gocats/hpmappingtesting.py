# !/usr/bin/python3
"""Used to calculate estimated potential false mappings, potential false mappings, and total possible mappings that
occur along paths containing the has_part relationship in GO. This python script produces the results for table 4 in the
manuscript.

Usage: python3 hpmappingtesting.py <ontology_file>
"""
import gocats
import itertools
from sys import argv

ontology_file_path = argv[1]
cc_graph = gocats.build_graph_interpreter(ontology_file_path, supergraph_namespace='cellular_component', allowed_relationships=['is_a', 'part_of', 'has_part'])
cc_no_hp_graph = gocats.build_graph_interpreter(ontology_file_path, supergraph_namespace='cellular_component', allowed_relationships=['is_a', 'part_of'])
mf_graph = gocats.build_graph_interpreter(ontology_file_path, supergraph_namespace='molecular_function', allowed_relationships=['is_a', 'part_of', 'has_part'])
mf_no_hp_graph = gocats.build_graph_interpreter(ontology_file_path, supergraph_namespace='molecular_function', allowed_relationships=['is_a', 'part_of'])
bp_graph = gocats.build_graph_interpreter(ontology_file_path, supergraph_namespace='biological_process', allowed_relationships=['is_a', 'part_of', 'has_part'])
bp_no_hp_graph = gocats.build_graph_interpreter(ontology_file_path, supergraph_namespace='biological_process', allowed_relationships=['is_a', 'part_of'])

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
    """Considering a problematic relationship edge, returns a set of ancestor nodes that could result in a problematic
    mapping.

    :param edge: :class:`dag.AbstractEdge` object
    :return: A set subtraction of `dag.AbstractEdge.parent` ancestors from `dag.AbstractEdge.child` ancestors.
    :rtype: :py:obj:`set`
    """
    child_ancestors = set(edge.child_node.ancestors)
    child_ancestors.add(edge.child_node)
    parent_ancestors = set(edge.parent_node.ancestors)
    parent_ancestors.add(edge.parent_node)

    return child_ancestors - parent_ancestors


def _potential_false_descendants(edge):
    """Considering a problematic relationship edge, returns a set of descendant nodes that could result in a problematic
    mapping.

    :param edge: :class:`dag.AbstractEdge` object
    :return: A set subtraction of `dag.AbstractEdge.child` descendants from `dag.AbstractEdge.parent` descendants.
    :rtype: :py:obj:`set`
    """
    parent_descendants = set(edge.parent_node.descendants)
    parent_descendants.add(edge.parent_node)
    child_descendants = set(edge.child_node.descendants)
    child_descendants.add(edge.child_node)

    return parent_descendants - child_descendants


def potential_false_mappings(edge_list):
    """Returns a set of mapping pairs (tuples of nodes) that results from a cartesian product of the sets of potential
    false descendants and potential false ancestors calculated for a list or set of problematic edges.

    :param list edge_list: A list of :class:`dag.AbstractEdge` objects.
    :return: Cartesian product of sets produced by :func:`_potential_false_ancestors` and :func:`_potential_false_descendants`.
    :rtype: :py:obj:`set`
    """
    pmf = set()
    for edge in edge_list:
        pmf.update(set(itertools.product(*[_potential_false_descendants(edge), _potential_false_ancestors(edge)])))
    return pmf


def all_possible_mappings(node_list):
    """Given a list of all nodes in a graph, returns a set of mapping pairs (tuples of nodes) that results from a
    cartesian product of all sets of descendant nodes to their respective ancestor nodes. Ignores self mappings.

    :param list node_list: A list of all :class:`dag.AbstractNode` objects in a graph.
    :return: A set of all tuples representing every term-to-term mapping possible in the graph.
    :rtype: :py:obj:`set` of :py:obj:`tuple`s.
    """
    node_mapping_tuples = set()
    for node1 in node_list:
        for node2 in node_list:
            if node1 != node2 and node1.ancestors.intersection(node2.descendants):
                node_mapping_tuples.add((node1, node2))
    return node_mapping_tuples

# cellular_component
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
print("All possible mappings without 'has_part': ", len(all_possible_mf_no_hp_mappings))
print("Intersection of possible true mappings and potentially false 'has_part' mappings: ", len(all_possible_mf_mappings.intersection(potential_false_mf_hp_mappings)))

print("-----biological_process-----")
print("Potentially false 'has part' mappings: ", len(potential_false_bp_hp_mappings))
print("All possible mappings: ", len(all_possible_bp_mappings))
print("All possible mappings without 'has_part': ", len(all_possible_bp_no_hp_mappings))
print("Intersection of possible true mappings and potentially false 'has_part' mappings: ", len(all_possible_bp_mappings.intersection(potential_false_bp_hp_mappings)))
