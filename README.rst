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

Links
~~~~~

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

Make sure you have git installed_:

.. code:: bash

   cd ~/
   git clone <PLACEHOLDER_URL>

Install on Windows
------------------
Windows installation not yet available. Sorry about that.

Quickstart
~~~~~~~~~~

For instructions on how to format your keyword list and advanced argument usage, consult the tutorial, guide, and API
documentation <PLACEHOLDER_URL>.

Subgraphs can be created from the command line:

.. code:: bash

   python3 ~/ARK.GOcats/gocats/gocats.py create_subgraphs /path_to_ontology_file ~/ARK.GOcats/gocats/exampledata/examplecategories.csv ~/Output --supergraph_namespace=cellular_component --subgraph_namespace=cellular_component --output_termlist

Mapping files can be found in the output directory:

   - GC_content_mapping.json_pickle  # A python dictionary with category-defining GO terms as keys and a list of all subgraph contents as values.
   - GC_id_mapping.json_pickle  # A python dictionary with every GO term of the specified namespace as keys and a list of category root terms as values.

GAF mappings can also be made from the command line:

.. code:: bash

   python3 ~/ARK.GOcats/gocats/gocats.py categorize_dataset YOUR_GAF.goa YOUR_OUTPUT_DIRECTORY/GC_id_mapping.json_pickle YOUR_OUTPUT_DIRECTORY MAPPED_GAF_NAME.goa


License
~~~~~~~

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

.. _installed: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git/
.. _ehinderer: https://github.com/ehinderer
.. _hunter-moseley: https://github.com/hunter-moseley