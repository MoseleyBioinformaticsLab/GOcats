# GOcats

GOcats is an Open Biomedical Ontology (OBO) parser and categorizing utility--currently specialized for the Gene Ontology (GO)--which can sort ontology terms into conceptual categories that a user provides.

See documentation on readthedocs for up-to-date documentation, detailed API reference, and tutorials: gocats.readthedocs.io/en/latest

The sections below pertain to experimentation implemented in

Hinderer EW, Moseley NHB. GOcats: A tool for categorizing Gene Ontology into subgraphs of user-defined concepts. PLoS One. 2020;15(6):1-29.

Hinderer EW, Flight RM, Dubey R, Macleod JN, Moseley HNB. Advances in Gene Ontology utilization improve statistical power of annotation enrichment. PLoS One. 2019;14(8):1-20.

## Important note: cite your use of GOcats
See the CITATION file for instructions.

## Getting Started

It is recommended that you clone this repository into a project directory within the home directory.

You will also need a local copy of the Gene Ontology OBO flat file, available here: http://purl.obolibrary.org/obo/go.obo

GOcats is able to map annotations within Gene Association Files (GAFs) into categories specified by the user. These categories are specified by creating a csv file where column 1 is the name of the category and column 2 is a list of keywords associated with that category concept, separated by semicolons (;). See GOcats/gocats/exampledata/examplecategories.csv as an example of 25 subcellular location categories. In its current version, this will be the main use of GOcats.

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

#### Plotting figures and tables

Fedora 24
```
sudo dnf install gcc-c++ libpng-devel freetype-devel libffi-devel python3-tkinter
sudo pip3 install --upgrade pip
sudo pip3 install numpy pandas tabulate cairocffi pyupset py2cytoscape matplotlib
```
Ubuntu 16.04
```
sudo apt get install gcc libpng-dev freetype2-demos libffi-dev python3-tk
sudo pip3 install --upgrade pip
sudo pip3 install numpy pandas tabulate cairocffi pyupset py2cytoscape matplotlib
```

### Installing

#### GOcats

Clone the repo after installing the dependencies (you will need permission to
  access the gitlab server. If you do not have access, you probably got this
  project directory from FigShare, in which case these steps are unnecessary).
```
cd
git clone https://eugene@gitlab.cesb.uky.edu/eugene/GOcats.git
```

Checkout the manuscript_3 branch for the most recent version
```
cd GOcats
git fetch
git checkout manuscript_3
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
python3 ~/GOcats/gocats/gocats.py create_subgraphs /path_to_ontology_file ~/ARK.GOcats/gocats/exampledata/examplecategories.csv ~/Output --supergraph_namespace=cellular_component --subgraph_namespace=cellular_component --output_termlist
```
This will output several files in the 'Output' directory including:
```
GC_content_mapping.json_pickle  # A python dictionary with category-defining GO terms as keys and a list of all subgraph contents as values.
GC_id_mapping.json_pickle  # A python dictionary with every GO term of the specified namespace as keys and a list of category root terms as values.
```

Mapping GO terms in a GAF
```
python3 ~/GOcats/gocats/gocats.py categorize_dataset YOUR_GAF.goa YOUR_OUTPUT_DIRECTORY/GC_id_mapping.json_pickle YOUR_OUTPUT_DIRECTORY MAPPED_GAF_NAME.goa
```

## Running the tests and producing manuscript results

##### The following run scripts are located in GOcats/runscripts. See doc strings in each script for information on how to run each. NOTE: All prerequisites must be installed before running the following scripts. Make sure to check each script to ensure that the installation path to OWLTools is correct.  

**run.sh** - This script runs all figure and table-producing scripts in the GOcats/runscripts directory and places output tables, figures and data in the specified <output_dir>.

**GenerateHindererCategories.sh** - Used to produce S1 and Tables 1, and 2. This script produces inclusion index values, Jaccard index values, and other information for the example subgraph categories described by Hinderer and Moseley.

**GenerateHPAMappingComparison.sh** - Used to produce Figures 7a, and 8a and Tables 6 and 8. Note: Requires OWLTools-map2slim OWLTools available here: https://github.com/owlcollab/owltools/wiki/Map2Slim Assuming OwlTools is installed under ~$HOME/owltools If not, edit OWLTOOLS_DIR to the appropriate directory.

**GenerateGenericHPAMappingComparison.sh** - Used to produce Figures 7b and 8b. This script produces knowledgebase mappings from the HPA raw data and from the knowledgebases to a set of categories representing a more generic version of HPA's localization annotations. These were chosen by Hinderer and Moseley to resolve discrepancies in term granularity observed between knowledgebase annotations and experimental data annotations.

**GenerateVisualizationData.sh** - Used to produce data for Figure 3a-c. Network tables produced by this script can be loded into Cytoscape for network visualization. GOcats/runscripts/run.sh can automatically load up and format the Cytoscape networks if an active Cytoscape session is opened to port 1234. To do this, navigate to your Cytoscape directory and run the following before executing run.sh: sh cytoscape.sh -R 1234

**SpeedTest.sh** - Used to report speed comparisons between GOcats and Map2Slim.

##### The following test and supporting scripts are located in GOcats/gocats:

**hpmappingtesting.py** - Produces the data for Table 4.

**gofull.py** - Used to gather graph information across all of GO or specific sections of GO. Specifically used to gather information about the number of each relation in GO.

**plotfigures.py** - Creates figures 7a-b and 8a-b from the data produced from other run scripts. Be sure to run all run scripts and note the
location of the output directories before running this script.

**cytoscapegraph.py** - Loads and automatically formats visualization data produced by GenerateVisualizationData.sh in an active Cytoscape session. See comments in GOcats/runscripts/run.sh for more information.

**testfindancestors.py** - Creates ancestor lists of GO terms from annotations in a Gene Annotation File using several methods of ancestor finding.

##### The following run scripts are located in GOcats/gocats/tests/Map2SlimMappingTest:

**run.sh** - Produces the data used in Table 5. Once run, the results are stored in GOcats/gocats/tests/Map2SlimMappingTest/logs. NOTE! These scripts contain custom commands for a TORQUE cluster that can only be run in-house and are thus not reproducible outside of our lab. Contact corresponding author for questions.

##### Other results:

Information for Table 7 was entered manually to describe how the custom generic categories encompassed the previously-used categories.

Information for Table 9 was compiled using the build_graph_interpreter command in gocats.py for each constraint (all GO, cellular_component, molecular_function, and biological_process) and accessing the graph object's 'relationship_count' variable to tally the use of each relationship type. The rest of the information was entered manually.

## Authors

* **Eugene Hinderer** - [ehinderer](https://github.com/ehinderer)
