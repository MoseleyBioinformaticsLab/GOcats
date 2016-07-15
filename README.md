GOcats3/OBOcats
GOcats3 is an Open Biomedical Ontology (OBO) parser and categorizer currently specialized for the Gene Ontology (GO) which can sort ontology terms into conceptual categories that a user provides. It is being redeveloped from GOcats version 2 available here: https://gitlab.cesb.uky.edu/eugene/ARK.goLocalization. Later, it will be extended into OBOcats, which will parse and categorize any ontology in the OBO Foundry.

USAGE:
Currently in heavy development. 
You can test various aspects that I've scripted so far in /tests. Just make sure that you download any files that may be required in the scripts and change the file location to where it's located on your machine. GOcats currently parses only go.obo files available here: http://geneontology.org/page/download-ontology. 
To run the scripts, move to the GOcats3 directory and run:

python3 -m obocats.tests.'run_sctipt'

for example:
python3 -m obocats.tests.gocats_full_basic_test 


Will update this as more functions become available. 
