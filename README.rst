GOcats
======

`GOcats` is an Open Biomedical Ontology (OBO) parser and categorizing utility--currently specialized for the Gene
Ontology (GO)--which can help scientists interpret large-scale experimental results by organizing redundant and highly-
specific annotations into customizable, biologically-relevant concept categories. Concept subgraphs are defined by lists
of keywords created by the user.

Currently, the `GOcats` package can be used to:
   * Create subgraphs of GO which each represent a user-specified concept.
   * Map specific, or fine-grained, GO terms in a Gene Annotation File (GAF) to an arbitrary number of concept
     categories.
   * Explore the Gene Ontology graph within a Python interpreter.

Citation
~~~~~~~~
Please cite the GitHub repository until our manuscript is accepted for publication: https://github.com/MoseleyBioinformaticsLab/GOcats.git

Installation
~~~~~~~~~~~~

`GOcats` runs under Python 3.4+, clone the git repo and install the following dependencies and you are ready to go!

Install on Linux
----------------

Dependency installation
.......................

GOcats requires JSONPickle and docopt:

.. code:: bash

   pip3 install docopt
   pip3 install jsonpickle

Package installation
....................

Make sure you have git_ installed:

.. code:: bash

   cd ~/
   git clone https://github.com/MoseleyBioinformaticsLab/GOcats.git

Install on Windows
------------------
Windows version not yet available; sorry about that.

Quickstart
~~~~~~~~~~

For instructions on how to format your keyword list and advanced argument usage, consult the tutorial, guide, and API
documentation in GOcats/doc.

Subgraphs can be created from the command line. Either navigate to the GOcats directory or add the directory to your
PYTHONPATH:

.. code:: bash

   python3 -m gocats create_subgraphs /path_to_ontology_file ~/GOcats/gocats/exampledata/examplecategories.csv ~/Output --supergraph_namespace=cellular_component --subgraph_namespace=cellular_component --output_termlist

Mapping files can be found in the output directory:

   - GC_content_mapping.json_pickle  # A python dictionary with category-defining GO terms as keys and a list of all subgraph contents as values.
   - GC_id_mapping.json_pickle  # A python dictionary with every GO term of the specified namespace as keys and a list of category root terms as values.

GAF mappings can also be made from the command line:

.. code:: bash

   python3 -m gocats categorize_dataset YOUR_GAF.goa YOUR_OUTPUT_DIRECTORY/GC_id_mapping.json_pickle YOUR_OUTPUT_DIRECTORY MAPPED_GAF_NAME.goa


License
~~~~~~~

Made available under the terms of The Clear BSD License. See full license in LICENSE.

Authors
~~~~~~~

* **Eugene W. Hinderer III** - ehinderer_
* **Hunter N.B. Moseley** - hunter-moseley_

.. _git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git/
.. _ehinderer: https://github.com/ehinderer
.. _hunter-moseley: https://github.com/hunter-moseley
