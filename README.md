# GOcats

GOcats is an Open Biomedical Ontology (OBO) parser and categorizing utility--currently specialized for the Gene Ontology (GO)--which can sort ontology terms into conceptual categories that a user provides.

## Getting Started

It is recommended that you clone this repository into a project directory within the home directory. 

You will also need a local copy of the Gene Ontology OBO flat file, available here: http://purl.obolibrary.org/obo/go.obo

GOcats is able to map annotations within Gene Association Files (GAFs) into categories specified by the user. These categories are specified by creating a csv file where column 1 is the name of the category and column 2 is a list of keywords associated with that category concept, separated by semicolons (;). See ARK.GOcats3/gocats/exampledata/examplecategories.csv as an example of 25 subcellular location categories. In its current version, this will be the main use of GOcats. 

If you would like to perform the analyses carried out in the development of GOcats which involve mapping comparisons to OWLTools' Map2Slim and to UniProt's Subcellular Location Controlled Vocabulary, please install the "Additional Packages" listed under the Prerequisites section and see the Running the Tests section.

### Prerequisites

#### Generating GOcats category mapping and mapping GAFs (standard usage)

##### Python3 / pip

Fedora 24
```
sudo dnf install python3-devel
sudo dnf install python3-pip
```

Ubuntu 16.04
```
sudo apt-get install python3-dev
sudo apt-get install python3-pip
```

##### Docopt / JSONPickle

Fedora 24 / Ubuntu 16.04
```
sudo pip3 install docopt
sudo pip3 install jsonpickle
```

#### Additional Packages (for running development tests, and scripts for producing manuscript results)

##### OWLTools prerequisites (see Installing OWLTools under Installing or visit https://github.com/owlcollab/owltools):

###### Maven / Java

Fedora 24
```
sudo dnf install maven java-1.8.0-openjdk-devel
```

Ubuntu
```
sudo apt-get install maven openjdk-8-jdk
```

#### Plotting analyses graphically and in tables

Fedora 24
```
sudo dnf install gcc-c++ libpng-devel freetype-devel libffi-devel python3-tkinter
sudo pip3 install --upgrade pip
sudo pip3 install numpy pandas tabulate cairocffi pyupset
```
Ubuntu 16.04
```
sudo apt get install gcc libpng-dev freetype2-demos libffi-dev python3-tk 
sudo pip3 install --upgrade pip
sudo pip3 install numpy pandas tabulate cairocffi pyupset
```

### Installing

#### GOcats

Clone the repo after installing the dependencies
```
cd
git clone https://gitlab.cesb.uky.edu/eugene/ARK.GOcats3.git
```

#### OWLTools (optional)

Clone the repo after installing the dependencies 
```
cd
git clone https://github.com/owlcollab/owltools
```

Install owltools using maven
```
cd ~/owltools/OWLTools-Parent
mvn clean package
```

You may get build errors. If this happens, I found that this command gets around them without affecting the usage in this project
```
mvn clean package -D maven.test.skip.exec=true
```

#### Example usage

Creating a mapping of GO terms from the Gene Ontology using a category file
```
python3 ~/ARK.GOcats/gocats/gocats.py create_subgraphs /path_to_ontology_file ~/ARK.GOcats/gocats/exampledata/examplecategories.csv ~/Output --supergraph_namespace=cellular_component --subgraph_namespace=cellular_component --output_termlist
```
This will output several files in the 'Output' directory including:
```
GC_content_mapping.json_pickle  # A python dictionary with category-defining GO terms as keys and a list of all subgraph contents as values.
GC_id_mapping.json_pickle  # A python dictionary with every GO term of the specified namespace as keys and a list of category root terms as values.
```

Mapping GO terms in a GAF
```
python3 ~/ARK.GOcats/gocats/gocats.py categorize_dataset YOUR_GAF.goa YOUR_OUTPUT_DIRECTORY/GC_id_mapping.json_pickle YOUR_OUTPUT_DIRECTORY MAPPED_GAF_NAME.goa
```

## Running the tests and producing manuscript results

The following run scripts are located in ARK.GOcats/runscripts. See doc strings in each script for information on how to run each. NOTE: All prerequisites must be installed before running the following scripts. Make sure to check each script to ensure that the installation path to OWLTools is correct.  

run.sh - Produces data for Figures 7a-b, and 8a-b which are taken from the results located in ~/<output_directory>/PlotsAndAnalyses/..AgreementSummary files. Also produces information for Tables 6 and 8 which are taken from results located in ~/<output_directory>/subgraph_report.txt and ~/<output_directory>/PlotsAndAnalyses/HPA_GOcatsAgreementSummary, respectively.  

GOcatsGenericHPAMapping.sh - Produces data for Figures 7b and 8b which are taken from results located in ~/<output_directory>/PlotsAndAnalyses/..AgreementSummary files. 

FullSubgraphInclusion.sh - Produces data for Figures 5 and S1a-v which are taken from results located in ~/<output_directory>/PlotsAndAnalyses/Plots. Also produces Figure 3a and b using line 19 and using the data in ~/<output_directory>/NetworkTable.csv as source and target nodes within Cytoscape to generate the figures. Finally, produces data for Tables 1, 2, and 3 which are taken from results located in ~/<output_directory>/subgraph_report.txt, ~/<output_directory>/GC-UP_InclusionIndex, and ~/<output_directory>/GC-M2S_InclusionIndex, respectively. 

run_map_supersets.sh - Produces data for Figure 3c (see comments in this script for details.) Data produced in ~/<output_directory>/NetworkTable.csv used as source and target nodes in Cytoscape to produce the figure.

The following run script is located in ARK.GOcats/gocats:

hpmappingtesting.py - Prints the data for Table 4.
 
The following run scripts are located in ARK.GOcats/gocats/tests/Map2SlimMappingTest:

run.sh - Produces the data used in Table 5. Once run, the results are stored in ARK.GOcats/gocats/tests/Map2SlimMappingTest/logs. NOTE! These scripts contain custom commands for a TORQUE cluster that can only be run in-house and are thus not reproducible outside of our lab. Contact corresponding author for questions.

Information for Table 7 was entered manually to describe how the custom generic categories encompassed the previously-used categories. 

Information for Table 9 was compiled using the build_graph_interpreter command in gocats.py for each constraint (all GO, cellular_component, molecular_function, and biological_process) and accessing the graph object's 'relationship_count' variable to tally the use of each relationship type. The rest of the information was entered manually. 

## Authors

* **Eugene Hinderer** - [ehinderer](https://github.com/ehinderer)
