import gocats
import pytest

this_version = str(gocats.__version__)


def hinderer_categories():
    # use the 01-12-2016 version of go.obo to get same results as manuscript_3.
    gocats.create_subgraphs({
    '<database_file>': '/mlab/data/databases/GeneOntology/01-12-2016/go.obo', '<keyword_file>': './gocats/exampledata/example_subdags.csv',
    '<output_directory>': '/mlab/data/eugene/'+this_version+'_output', '--supergraph_namespace': 'cellular_component',
    '--subgraph_namespace': 'cellular_component', '--supergraph_relationships': None, '--subgraph_relationships': None,
    '--map_supersets': False, '--output_termlist': True, '--go-basic-scoping': None, '--network_table_name': None
    })

hinderer_categories()
