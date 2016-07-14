# !/usr/bin/python3
from .. import dag
from .. import parser

obo_oparser = parser.OboParser()
little_godag = dag.GoGraph('cellular_component')
with open('~/little_go.obo', 'r') as database:
	obo_parser.parse_go(database, little_godag)

print(little_godag.node_list)
