# !/usr/bin/python3
"""Useful functions for the debugging and analysis of Gene Ontology parsing and super-categorization."""
import jsonpickle
import sys


def json_save(obj, filename):
    """Saves PARAMETER obj in file PARAMETER filename. use_jsonpickle=True used to prevent jsonPickle from encoding
    dictkeys to strings."""
    f = open(filename, 'w')
    json_obj = jsonpickle.encode(obj, keys=True)
    f.write(json_obj)
    f.close()


def json_load(filename):
    """Loads a jsonPickle object from PARAMETER filename. use_jsonpickle=True used to prevent jsonPickle from encoding
    dictkeys to strings."""
    f = open(filename)
    json_str = f.read()
    obj = jsonpickle.decode(json_str, keys=True)
    return obj


def list_to_file(file_location, data):
    """Makes a text document from PARAMETER data, with each line of the document being one item from the list and outputs
    the document into PARAMETER file_location. PARAMETER length may be specified to append
    the length of the list to the filename."""
    with open(file_location, 'wt') as out_file:
        for line in data:
            out_file.write(str(line) + '\n')


def display_name(dataset, go_id):
    """Improves readability of Gene Ontology (GO) terms by dislpaying the english name of a PARAMETER go_id (gene ontology
    ID) within its PARAMETER dataset (gene ontology dictionary)."""
    if isinstance(go_id, list):
        id_list = []
        for i in go_id:
            id_list.append(dataset[i]['name'])
        return id_list
    else:
        return dataset[go_id]['name']
