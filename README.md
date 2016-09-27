GOcats3/OBOcats

GOcats3 is an Open Biomedical Ontology (OBO) parser and categorizer currently specialized for the Gene Ontology (GO) which can sort ontology terms into conceptual categories that a user provides. It is being redeveloped from GOcats version 2 available here: https://gitlab.cesb.uky.edu/eugene/ARK.goLocalization. Later, it will be extended into OBOcats, which will parse and categorize any ontology in the OBO Foundry.
Currently in development. 

Usage:
    obocats filter_subgraphs <database_file> <keyword_file> <output_directory> [--supergraph_namespace=<None> --subgraph_namespace=<None> --supergraph_relationships=[] --subgraph_relationships=[] --map_supersets --output_termlist --output_idtranslation]
    obocats subgraph_overlap <obocats_mapping> <uniprot_mapping> <map2slim_mapping> <output_directory> [--inclusion_index]
    obocats categorize_dataset <gaf_dataset> <term_mapping> <output_directory> <GAF_name>
    obocats compare_mapping <mapped_gaf> <manual_dataset> [--group_annotations=<None>] [--save_assignments=<filename>]
Options:
    -h --help                            Shows this screen.
    --version                            Shows version.
    --supergraph_namespace=<None>        Filters the supergraph to a given namespace.
    --subgraph_namespace=<None>          Filters the subgraph to a given namespace.
    --supergraph_relationships=[]        A provided list will denote which relationships are allowed in the supergraph.
    --subgraph_relationships=[]          A provided list will denote which relationships are allowed in the subgraph.
    --map_supersets                      Maps all terms to all root nodes, regardless of if a root node supercedes another.
    --output_termlist                    Outputs a list of all terms in the supergraph as a JsonPickle file in the output directory.
    --output_idtranslation               Outputs a dictionary mapping of ontology IDs to their names. 
    --inclusion_index                    Calculates inclusion index of terms between categories among separate mapping sources.
    --group_annotations=<union>          Choose how to group multiple UniProt annotations (union|intersection) [default=union]
    --save_assignments=<filename>        Save a file with all genes and their GO assignments.

To execute individual commands run each through python3 from ARK.GOcats3/obocats/obocats.py
For exapmple: $ python3 ~/ARK.GOcats3/obocats/obocats.py filter_subgraphs your_database_file your_keyword_file your_output_directory --options

Will update this as more functions become available.

Make sure dependancies are installed!
    For analysis of OWLtools' Map2Slim:
        -maven
        -java-1.8.0-openjdk-devel
        - Install OWLtools (https://github.com/owlcollab/owltools)
            - Note install location and make sure its location is correct in ARK.GOcats3/runscripts/run.sh if you intend on using the runscript.
            - Briefly, git clone the repo, move into ~/owltools/OWLTools-Parent and run:
                $ mvn clean package -D maven.test.skip.exec=true
            
    For GOcats3/OBOcats analyses:
        -gcc-c++
        -lapack64-devel
        -python3-devel
        -python3-pip (pip3)
            -pip3 install numpy
            -pip3 install pandas
            -pip3 install pyupset
            -pip3 install tabulate
            -pip3 install cairocffi (careful with this, might need other dependancies)
        -libpng-devel
        -freetype-devel


    