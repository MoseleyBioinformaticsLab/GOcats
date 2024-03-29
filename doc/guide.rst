User Guide
==========

Description
~~~~~~~~~~~

:mod:`GOcats` is an Open Biomedical Ontology (OBO) parser and categorizing utility--currently specialized for the Gene
Ontology (GO)--which can help scientists interpret large-scale experimental results by organizing redundant and highly-
specific annotations into customizable, biologically-relevant concept categories. Concept subgraphs are defined by lists
of keywords created by the user.

Currently, the `GOcats` package can be used to:
   * Create subgraphs of GO which each represent a user-specified concept.
   * Map specific, or fine-grained, GO terms in a Gene Annotation File (GAF) to an arbitrary number of concept
     categories.
   * Reorganize GO terms based on allowed term-term relationships, and re-create the gene to all direct and ancestor GO terms.
   * Explore the Gene Ontology graph within a Python interpreter.

Installation
~~~~~~~~~~~~

`GOcats` runs under Python 3.4+ and is available through python3-pip. Install via pip or clone the git repo and install
the following dependencies and you are ready to go!

Install on Linux
----------------

Pip installation (method 1)
...........................

Dependencies should automatically be installed using this method. It is strongly recommended that you install with this
method.

.. code:: bash

   pip3 install gocats

GitHub Package installation (method 2)
......................................

Make sure you have git_ installed:

.. code:: bash

   cd ~/
   git clone https://github.com/MoseleyBioinformaticsLab/GOcats.git

Dependencies
............

`GOcats` requires the following Python libraries:

   * docopt_ for creating the :mod:`gocats` command-line interface.
   * JSONPickle_ for saving Python objects in a JSON serializable form and outputting to a file.

To install dependencies manually:

.. code:: bash

   pip3 install docopt
   pip3 install jsonpickle

Install on Windows
------------------
Windows version not yet available. Sorry about that.


Basic usage
~~~~~~~~~~~
To see command line arguments and options, navigate to the project directory and run the --help option:

.. code:: bash

   cd ~/GOcats
   python3 -m gocats --help

:mod:`gocats` can be used in the following ways:

   * To extract subgraphs of Gene Ontology that represent user-defined concepts and create mappings between
     high level concepts and their subgraph content terms.

      1. Create a CSV file, where column 1 is the name of the concept category (this can be anything) and
      column 2 is a list of keywords/phrases delineating that concept (separated by semicolons). See
      :doc:`tutorial` for more information.

      2. Download a Gene Ontology database obo_ file

      3. To create mappings, run the GOcats command, :func:`gocats.gocats.create_subgraphs`. If you installed by cloning
      the repository from GitHub, first navigate to the GOcats project directory or add the directory to the PYTHONPATH.

      .. code:: bash

         python3 -m gocats create_subdags <ontology_database_file> <keyword_file> <output_directory>

      4. Mappings can be found in your specified <output_directory>:

         - GC_content_mapping.json_pickle  # A python dictionary with category-defining GO terms as keys and a list of
           all subgraph contents as values.

         - GC_id_mapping.json_pickle  # A python dictionary with every GO term of the specified namespace as keys and a
           list of category root terms as values.

   * To map gene annotations in a Gene Annotation File (GAF) to a set of user-defined categories.

      1. Create mapping files as defined in the previous section.

      2. Run the :func:`gocats.gocats.categorize_dataset` to map terms to their categories:

      .. code:: bash

         # NOTE: Use the GC_id_mapping.jsonpickle file.
         python3 -m gocats categorize_dataset <GAF_file> <term_mapping_file> <output_directory> <mapped_gaf_filename>

      3. The output GAF will have the specified <mapped_gaf_filename> in the <output_directory>
      
    * To reorganize parent - child Gene Ontology terms relationships and the gene annotations with a set of user defined relationships.
    This has been shown to increase statistical power in GO enrichment calculations (see Hinderer_).
    
      1. Download a Gene Ontology database obo_ file.
      
      2. Download a Gene Ontology gene annotation format gaf_ file.
      
      3. Run the :func:`gocats.gocats.remap_goterms` to generate new gene to annotation relationships:
      
      .. code:: bash
      
          python3 -m gocats remap_goterms <go_database> <goa_gaf> <ancestor_filename> <namespace_filename> [--allowed_relationships=<relationships> --identifier_column=<column>]
          
      4. ``--allowed_relationships`` should be a comma separated string: ``is_a,part_of,has_part``
      
      5. The output <ancestor_filename> will be in JSON format, with genes as the keys, and annotated GO terms as the set.

   * Within the Python interpreter to explore the Gene Ontology graph (advanced usage, see :doc:`tutorial` for more
     information).

      1. If you've installed GOcats via pip, importing should work as expected. Otherwise, navigate to the Git project
      directory, open a Python 3.4+ interpreter, and import GOcats:

      .. code:: Python

         >>> from gocats import gocats as gc

      2. Create the graph object using :func:`gocats.gocats.build_graph_interpreter`:

      .. code:: Python

         >>> # May filter to GO sub-ontology or to a set of relationships.
         >>> my_graph = gc.build_graph_interpreter("path_to_database_file")

         You may now access all properties of the Gene Ontology graph object. Here are a couple of examples:

      .. code:: Python

         >>> # See the descendants of a term node, GO:0006306
         >>> descendant_set = my_graph.id_index['GO:0006306'].descendants
         >>> [node.name for node in descendant_set]
         >>> # Access all graph leaf nodes
         >>> leaf_nodes  = my_graph.leaves
         >>> [node.name for node in leaf_nodes]

.. _git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git/
.. _docopt: https://github.com/docopt/docopt
.. _JSONPickle: https://github.com/jsonpickle/jsonpickle
.. _obo: http://www.geneontology.org/page/download-ontology
.. _gaf: http://current.geneontology.org/products/pages/downloads.html
.. _Hinderer: https://doi.org/10.1371/journal.pone.0220728
