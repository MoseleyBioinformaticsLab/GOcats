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
   * Remap ancestor Gene Ontology term relationships and the gene annotations with a set of user defined relationships.
   * Explore the Gene Ontology graph within a Python interpreter.

Citation
~~~~~~~~
Please cite the following papers when using GOcats:

Hinderer EW, Moseley NHB. GOcats: A tool for categorizing Gene Ontology into subgraphs of user-defined concepts. PLoS One. 2020;15(6):1-29.

Hinderer EW, Flight RM, Dubey R, Macleod JN, Moseley HNB. Advances in Gene Ontology utilization improve statistical power of annotation enrichment. PLoS One. 2019;14(8):1-20.

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

   * docopt_ for creating the gocats command-line interface.
   * JSONPickle_ for saving Python objects in a JSON serializable form and outputting to a file.

To install dependencies manually:

.. code:: bash

   pip3 install docopt
   pip3 install jsonpickle

Install on Windows
------------------
GOcats can also be installed on windows through pip.

Quickstart
~~~~~~~~~~

For instructions on how to format your keyword list and advanced argument usage, consult the tutorial, guide, and API documentation at readthedocs_.

Subgraphs can be created from the command line.

.. code:: bash

   python3 -m gocats create_subgraphs /path_to_ontology_file ~/GOcats/gocats/exampledata/examplecategories.csv ~/Output --supergraph_namespace=cellular_component --subgraph_namespace=cellular_component --output_termlist

Mapping files can be found in the output directory:

   - GC_content_mapping.json_pickle  # A python dictionary with category-defining GO terms as keys and a list of all subgraph contents as values.
   - GC_id_mapping.json_pickle  # A python dictionary with every GO term of the specified namespace as keys and a list of category root terms as values.

GAF mappings can also be made from the command line:

.. code:: bash

   python3 -m gocats categorize_dataset YOUR_GAF.goa YOUR_OUTPUT_DIRECTORY/GC_id_mapping.json_pickle YOUR_OUTPUT_DIRECTORY MAPPED_DATASET_NAME.goa

Gene to GO Term remappings with consideration of ``has_part`` relationships can created from the command line:

.. code:: bash

   python3 -m gocats remap_goterms /path_to_ontology_file.obo /path_to_gaf.goa ancestors_output.json namespace_output.json --allowed_relationships=is_a,part_of,has_part --identifier_column=1

Gene to GO terms will be in JSON format in ``ancestor_output.json``, and new GO term to namespace in ``namespace_output.json``.

License
~~~~~~~

Made available under the terms of The Clear BSD License. See full license in LICENSE.

The Clear BSD License

Copyright (c) 2017, Eugene W. Hinderer III, Hunter N.B. Moseley
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted (subject to the limitations in the disclaimer
below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its contributors may be used
  to endorse or promote products derived from this software without specific
  prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS
LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

Authors
~~~~~~~

* **Eugene W. Hinderer III** - ehinderer_
* **Hunter N.B. Moseley** - hunter-moseley_

.. _readthedocs: http://gocats.readthedocs.io/
.. _jsonpickle: https://github.com/jsonpickle/jsonpickle
.. _docopt: https://github.com/docopt/docopt
.. _git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git/
.. _ehinderer: https://github.com/ehinderer
.. _hunter-moseley: https://github.com/hunter-moseley
