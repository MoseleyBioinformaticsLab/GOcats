# GOcats

GOcats is an Open Biomedical Ontology (OBO) parser and categorizing utility--currently specialized for the Gene Ontology
(GO)--which can sort ontology terms into conceptual categories that a user provides.

## Important note: cite your use of GOcats
See the CITATION file for instructions. 

## Getting Started

It is recommended that you clone this repository into a project directory within the home directory. 

You will also need a local copy of the Gene Ontology OBO flat file, available here: 
http://purl.obolibrary.org/obo/go.obo

GOcats is able to map annotations within Gene Association Files (GAFs) into categories specified by the user. These 
categories are specified by creating a csv file where column 1 is the name of the category and column 2 is a list of 
keywords associated with that category concept, separated by semicolons (;). See 
ARK.GOcats3/gocats/exampledata/examplecategories.csv as an example of 25 subcellular location categories. In its current
version, this will be the main use of GOcats. 

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

### Installing

#### GOcats

Clone the repo after installing the dependencies
```
cd
git clone https://gitlab.cesb.uky.edu/eugene/ARK.GOcats3.git
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

## Authors

* **Eugene Hinderer** - [ehinderer](https://github.com/ehinderer)
