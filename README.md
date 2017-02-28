# GOcats

GOcats is an Open Biomedical Ontology (OBO) parser and categorizer--currently specialized for the Gene Ontology (GO)--which can sort ontology terms into conceptual categories that a user provides. It is being redeveloped from a previous version of GOcats available here: https://gitlab.cesb.uky.edu/eugene/ARK.goLocalization. Later, it will be fully extended into OBOcats, which will parse and categorize any ontology in the OBO Foundry.
Currently in development.

## Getting Started

It is recommended that you clone this respository into a project directory within the home directory. 

You will also need a local copy of the Gene Ontology OBO flat file, available here: http://purl.obolibrary.org/obo/go.obo

GOcats is able to map annotations within Gene Associaition Files (GAFs) into categories specified by the user. These categories are specified by creating a csv file where column 1 is the name of the category and column 2 is a list of keywords assocaiated with that category concept, separated by semicolons (;). See ARK.GOcats3/gocats/exampledata/examplecategories.csv as an example of 25 subcellular location categories. In its current version, this will be the main use of GOcats. 

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

##### JSONPickle

Fefora 24 / Ubuntu 16.04
```
sudo pip3 install jsonpickle
```

#### Additional Packages (for running development tests)

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

#### Plotting and analyses 

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

Clone the repo after installing the dependancies
```
cd
git clone https://gitlab.cesb.uky.edu/eugene/ARK.GOcats3.git
```

#### OWLTools (optional)

Clone the repo after installing the dependancies 
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
python3 ~/ARK.GOcats/gocats/gocats.py filter_subgraphs ~/Databases/GeneOntology/01-12-2016/go.obo ~/ARK.GOcats/gocats/exampledata/examplecategories.csv ./Output --supergraph_namespace=cellular_component --subgraph_namespace=cellular_component --output_termlist
```
This will output several files in the 'Output' directory including:
```
OC_content_mapping.json_pickle  # A python dictionary with category-defining GO terms as keys and a list of all subgraph contents as values.
OC_id_mapping.json_pickle  # A python dictionary with every GO term of the specified namespace as keys and a list of category root terms as values.
```

Mapping GO terms in a GAF
```
python3 ~/ARK.GOcats/gocats/gocats.py categorize_dataset YOUR_GAF.goa YOUR_OUTPUT_DIRECTORY/OC_id_mapping.json_pickle YOUR_OUTPUT_DIRECTORY MAPPED_GAF_NAME.goa
```

## Running the tests

Basic tests are located in ARK.GOcats/gocats/tests and can be run individually using the -m option in python
```
cd ~/ARK.GOcats3
python3 -m gocats.tests.gocats_full_basic_test  # Note that this may be broken currently, I am working on fixing this. 
```

To run the analyses against OWLTools and UniProt CV, execute the runscript located in runscripts. It is self-documented as well.
Change into the output directory of your choice

The runscripts opperation is as follows:
```
run.sh <gocats_dir> <GO_file> <output_dir_path>
```

For example:
```
sh ~/ARK.GOcats3/runscripts/run.sh ~/ARK.GOcats3/gocats ~/Databases/GeneOntology/01-12-2016/go.obo ./Output
```

## Contributing

#TODO:edit this section

## Versioning

#TODO:edit this section 

## Authors

* **Eugene Hinderer** - [ehinderer](https://github.com/ehinderer)

#TODO:edit this section

## License

#TODO:edit this section

## Acknowledgments

#TODO:edit this section

