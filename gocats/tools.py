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
def write_out_gaf(data, filename):
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
