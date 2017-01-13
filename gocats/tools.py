# !/usr/bin/python3
"""Functions for handling I/O tasks (and more!) with GOcats."""
import jsonpickle
import sys
import os
import re
import csv
csv.field_size_limit(sys.maxsize)


def json_save(obj, filename):
    """Saves PARAMETER obj in file PARAMETER filename. use_jsonpickle=True used to prevent jsonPickle from encoding
    dictkeys to strings."""
    f = open(filename+".json_pickle", 'w')
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
    with open(file_location+".txt", 'wt') as out_file:
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


# Functions for handling Gene Annotation Files
def writeout_gaf(data, file_handle):
    with open(file_handle, 'w') as gaf_file:
        gafwriter = csv.writer(gaf_file, delimiter='\t')
        for line in data:
            gafwriter.writerow([item for item in line])


def parse_gaf(file_handle):
    comment_line = re.compile('^!')
    gaf_array = []
    with open(os.path.realpath(file_handle)) as gaf_file:
        for line in csv.reader(gaf_file, delimiter='\t'):
            if not re.match(comment_line, str(line[0])):
                gaf_array.append(line)
    return gaf_array


def itemize_gaf(gaf_file):
    location_gene_dict = {}
    with open(gaf_file, 'r') as file:
        for line in csv.reader(file, delimiter='\t'):
            if len(line) > 1:
                if line[4] not in location_gene_dict.keys():
                    location_gene_dict[line[4]] = set([line[1]])
                elif line[4] in location_gene_dict.keys() and line[1] not in location_gene_dict[line[4]]:
                    location_gene_dict[line[4]].update([line[1]])
                else:
                    pass
    return location_gene_dict


def make_gaf_dict(gaf_file, keys):
    comment_line = re.compile('^\'!')
    gaf_dict = {}
    with open(gaf_file, 'r') as file:
        for line in csv.reader(file, delimiter='\t'):
            if len(line) > 1:
                if keys == 'go_term':  # Here go terms are mapping to all of the DB Object Symbols in the GAF.
                    if line[4] not in gaf_dict.keys():
                        gaf_dict[line[4]] = set([line[2]])
                    elif line[4] in gaf_dict.keys() and line[2] not in gaf_dict[line[4]]:
                        gaf_dict[line[4]].update([line[2]])
                    else:
                        pass
                elif keys == 'db_object_symbol':
                    if line[0] == 'UniProtKB' and line[2] not in gaf_dict.keys():
                        gaf_dict[line[2]] = set([line[4]])
                    elif line[0] == 'UniProtKB' and line[2] in gaf_dict.keys():
                        gaf_dict[line[2]].add(line[4])
                    else:
                        print('ERROR: Reference DB not recognized: '+str(line[0]))
        return gaf_dict
