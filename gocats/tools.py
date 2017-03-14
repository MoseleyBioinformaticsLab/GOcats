# !/usr/bin/python3
"""
Functions for handling some file input and output and reformatting tasks in GOcats.
"""
import json
import jsonpickle
import sys
import os
import re
import csv
csv.field_size_limit(sys.maxsize)


# TODO: move to using JSON not JsonPickle and use sort_keys=True parameter to test outputs between runs
def json_save(obj, filename):
    """Takes a Python object, converts it into a JSON serializable object (if it is not already), and saves it to a file
    that is specified.

    :param obj: A Python :py:obj:`obj`.
    :param file_handle filename: A path to output the resulting JSON file.
    """
    if type(obj) == str or type(obj) == list:
        json_obj = obj
    elif type(obj) == dict:
        json_obj = dict()
        for key, value in obj.items():
            if type(value) == str or type(value) == list:
                new_value = value
            elif type(value) == set:
                new_value = [item for item in value]
            else:
                raise Exception("Data type is not supported!")
            json_obj[key] = new_value
    elif type(obj) == set:
        json_obj = [item for item in obj]
    else:
        raise Exception("Data type is not supported!")
    with open(filename+".json", 'w') as json_file:
        json_text = json.dumps(json_obj, sort_keys=True)
        json_file.write(json_text)


def jsonpickle_save(obj, filename):
    """Takes a Python object, converts it into a JsonPickle string, and writes it out to a file.

    :param obj: A Python :py:obj:`obj`
    :param file_handle filename:  A path to output the resulting JsonPickle file.
    """
    f = open(filename+".json_pickle", 'w')
    json_obj = jsonpickle.encode(obj, keys=True)  # Use_jsonpickle=True used to prevent jsonPickle from encoding dictkeys to strings.
    f.write(json_obj)
    f.close()


def jsonpickle_load(filename):
    """Takes a JsonPickle file and loads in the JsonPickle object into a Python object.

    :param file_handle filename: A path to a JsonPickle file.
    """
    f = open(filename)
    json_str = f.read()
    obj = jsonpickle.decode(json_str, keys=True)  # Use_jsonpickle=True used to prevent jsonPickle from encoding dictkeys to strings.
    return obj


def list_to_file(filename, data):
    """Makes a text document from a :py:obj:`list`  of data, with each line of the document being one item from the list
     and outputs the document into a file.

     :param file_handle filename: A path to the output file.
     :param data: A Python :py:obj:`list`.
     """
    with open(filename + ".txt", 'wt') as out_file:
        for line in data:
            out_file.write(str(line) + '\n')


# Functions for handling Gene Annotation Files
def writeout_gaf(data, filename):
    """Writes out an object representing a Gene Annotation File (GAF) to a file.

    :param list data: A :py:obj:`list` object representing a GAF. Each item in the list represents a row.
    :param file_handle filename: A path and name for the GAF.
    """
    with open(filename, 'w') as gaf_file:
        gafwriter = csv.writer(gaf_file, delimiter='\t')
        for line in data:
            gafwriter.writerow([item for item in line])


def parse_gaf(filename):
    """Converts a Gene Annotation File (GAF) into a :py:obj:`list` object where every item is a row from the GAF.

    :param file_handle filename: Specify the location of the GAF.
    :return: A list representing the GAF.
    :rtype: :py:obj:`list`
    """
    comment_line = re.compile('^!')
    gaf_array = list()
    with open(os.path.realpath(filename)) as gaf_file:
        for line in csv.reader(gaf_file, delimiter='\t'):
            if not re.match(comment_line, str(line[0])):
                gaf_array.append(line)
    return gaf_array


def make_gaf_dict(filename, keys):
    """Creates a :py:obj:`dict` object mapping the "DB Object ID" column values to the "GO ID" column values in a Gene
    Annotation File (GAF) or vice versa.

    :param: file_handle filename: Specify the location of the GAF.
    :param str keys: Dictates whether the "DB Object ID" or  "GO ID" columns are used as keys in the mapping dict, accepts db_object_symbol or go_term
    :returns: :py:obj:`dict` object mapping the GAF DB Object IDs and GO IDs, depending on which `keys` parameter is used.
    :rtype: :py:obj:`dict`
    """
    comment_line = re.compile('^\'!')
    gaf_dict = dict()
    with open(filename, 'r') as file:
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
