GOcats
======

.. image:: https://raw.githubusercontent.com/MoseleyBioinformaticsLab/GOcats/master/doc/_static/images/GOcats_logo.png
   :width: 50%
   :align: right
   :target: http://gocats.readthedocs.io/

`GOcats` is an Open Biomedical Ontology (OBO) parser and categorizing utility--currently specialized for the Gene
Ontology (GO)--which can help scientists interpret large-scale experimental results by organizing redundant and highly-
specific annotations into customizable, biologically-relevant concept categories. Concept subgraphs are defined by lists
of keywords created by the user.

Full API documentation, userguide, and tutorial can be found on readthedocs_

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

`GOcats` runs under Python 3.4+ and is available through python3-pip. Install via pip or clone the git repo and install
the following dependencies and you are ready to go!

Install on Linux
----------------

Pip installation
................

Dependencies should be automatically installed using this method. It is strongly recommended that you install with this
method.
.. code:: bash

   pip3 install gocats

GitHub Package installation
...........................

Make sure you have git_ installed:

.. code:: bash

   cd ~/
   git clone https://github.com/MoseleyBioinformaticsLab/GOcats.git

Dependencies
............

`GOcats` requires the following Python libraries:

   * docopt_ for creating the :mod:`gocats` command-line interface.
   * jsonpickle_ for saving Python objects in a JSON serializable form and outputting to a file.

To install dependencies manually:

.. code:: bash

   pip3 install docopt
   pip3 install jsonpickle

Install on Windows
------------------
Windows version not yet available; sorry about that.

Quickstart
~~~~~~~~~~

For instructions on how to format your keyword list and advanced argument usage, consult the `tutorial <doc/tutorial.rst>`_, `guide <doc/guide.rst>`_, and `API <doc/api.rst>`_

Subgraphs can be created from the command line.

.. code:: bash

   python3 -m gocats create_subgraphs /path_to_ontology_file ~/GOcats/gocats/exampledata/examplecategories.csv ~/Output --supergraph_namespace=cellular_component --subgraph_namespace=cellular_component --output_termlist

Mapping files can be found in the output directory:

   - GC_content_mapping.json_pickle  # A python dictionary with category-defining GO terms as keys and a list of all subgraph contents as values.
   - GC_id_mapping.json_pickle  # A python dictionary with every GO term of the specified namespace as keys and a list of category root terms as values.

GAF mappings can also be made from the command line:

.. code:: bash

   python3 -m gocats categorize_dataset YOUR_GAF.goa YOUR_OUTPUT_DIRECTORY/GC_id_mapping.json_pickle YOUR_OUTPUT_DIRECTORY MAPPED_DATASET_NAME.goa


License
~~~~~~~

.. include:: ../LICENSE

Made available under the terms of The Clear BSD License. See full license in LICENSE.

Authors
~~~~~~~

* **Eugene W. Hinderer III** - ehinderer_
* **Hunter N.B. Moseley** - hunter-moseley_

.. _readthedocs: http://gocats.readthedocs.io/en/latest/
.. _docopt: https://github.com/docopt/docopt
.. _jsonpickle: https://jsonpickle.github.io/
.. _git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git/
.. _ehinderer: https://github.com/ehinderer
.. _hunter-moseley: https://github.com/hunter-moseley
