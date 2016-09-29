# GOcats3/OBOcats

GOcats3/OBOcats is an Open Biomedical Ontology (OBO) parser and categorizer--currently specialized for the Gene Ontology (GO)--which can sort ontology terms into conceptual categories that a user provides. It is being redeveloped from GOcats version 2 available here: https://gitlab.cesb.uky.edu/eugene/ARK.goLocalization. Later, it will be fully extended into OBOcats, which will parse and categorize any ontology in the OBO Foundry.
Currently in development.

## Getting Started

It is recommended that you clone this respository into a project directory within the home directory. 

You will also need a local copy of the Gene Ontology OBO flat file, available here: http://purl.obolibrary.org/obo/go.obo

GOcats3/OBOcats is able to map annotations within Gene Associaition Files (GAFs) into categories specified by the user. These categories are specified by creating a csv file where column 1 is the name of the category and column 2 is a list of keywords assocaiated with that category concept, separated by semicolons (;). See ARK.GOcats3/obocats/exampledata/examplecategories.csv as an example of 25 subcellular location categories. In its current version, this will be the main use of GOcats3. 

If you would like to perform the analyses carried out in the development of GOcats3 which involve mapping comparisons to OWLTools' Map2Slim and to UniProt's Subcellular Location Controlled Vocabulary, please install the "Additional Packages" listed under the Prerequisites section and see the Running the Tests section.

### Prerequisities

#### Generating GOcats category mapping and mapping GAFs (standard usage)

Python3 / pip

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

JSONPickle

Fefora 24 / Ubuntu 16.04
```
sudo pip3 install jsonpickle
```

#### Additional Packages (for running development tests)

##### OWLTools prerequisites (see Installing OWLTools under Installing or visit https://github.com/owlcollab/owltools):

Maven / Java

Fedora 24
```

```

```
Give examples
```

### Installing

A step by step series of examples that tell you have to get a development env running

Stay what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* Dropwizard - Bla bla bla
* Maven - Maybe
* Atom - ergaerga

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
