The GOcats Tutorial
===================

Currently, `GOcats` can be used to:
   * Create subgraphs of the Gene Ontology (GO) which each represent a user-specified concept.
   * Map specific, or fine-grained, GO terms in a Gene Annotation File (GAF) to an arbitrary number of concept
     categories.
   * Explore the Gene Ontology graph within a Python interpreter.

In this document, each use case will be explained in-depth.

Using GOcats to create subgraphs representing user-specified concepts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before starting, it is important to decide what concepts you as the user wish to extract from the Gene Ontology. You may
have an investigation that is focused on concepts like "DNA repair" or "autophagy," or you may simply be interested in
enumerating many arbitrary categories and seeing how ontology terms are shared between concepts. As an example to use in
this tutorial, let's consider a goal of extracting subgraphs that represent some typical subcellular locations of a
eukaryotic cell.

Creating a keyword file
-----------------------

The phrase "keyword file" might be slightly misleading because GOcats does not only handle keywords, but also **short phrases**
that may be used to define a concept. Therefore, both may be used in combination in the keyword CSV file.

The CSV file is formatted as so:

   * Each row represents a separate concept.
   * Column 1 is the name of the concept (this is for reference and will not be used to parse GO).
   * Column 2 is a list of keywords or short phrases used to describe the concept in question.
      * Each item in column 2 is separated by a semicolon (;) with no whitespace around the semicolon.

Here is an example of what the file contents should look like (**do not include the header row in the actual file**):
   +--------------+------------------------------------------+
   |    Concept   |             Keywords/phrases             |
   +==============+==========================================+
   | mitochondria | mitochondria;mitochondrial;mitochondrion |
   +--------------+------------------------------------------+
   |   Nucleus    | nucleus;nuclei;nuclear                   |
   +--------------+------------------------------------------+
   |   lysosome   | lysosome;lysosomal;lysosomes             |
   +--------------+------------------------------------------+
   |   vesicle    | vesicle;vesicles                         |
   +--------------+------------------------------------------+
   |     ER       | endoplasmic;sarcoplasmic;reticulum       |
   +--------------+------------------------------------------+
   |    golgi     | golgi; golgi apparatus                   |
   +--------------+------------------------------------------+
   | extracellular| extracellular;secreted                   |
   +--------------+------------------------------------------+
   |   cytosol    | cytosol;cytosolic                        |
   +--------------+------------------------------------------+
   |  cytoplasm   | cytoplasm;cytoplasmic                    |
   +--------------+------------------------------------------+
   | cell membrane| plasma;plasma membrane                   |
   +--------------+------------------------------------------+
   | cytoskeleton | cytoskeleton;cytoskeletal                |
   +--------------+------------------------------------------+

We'll imagine this file is located in the home directory and is called "cell_locations.csv."

Downloading the Gene Ontology .obo file
---------------------------------------

The go.obo file is available here: http://www.geneontology.org/page/download-ontology. Be sure to download the .obo-
formatted version. All releases of GO in this format as of Jan 2015 have been verified to be compatible with GOcats.
We'll assume this database file is located in the home directory and is called "go.obo."

Extracting subgraphs and creating concept mappings
--------------------------------------------------

This is where GOcats does the heavy lifting. We'll assume the GOcats repository was already cloned into the home
directory (refer to :doc:`guide` for instructions on how to install GOcats). We can now use Python to run the
:func:`gocats.create_subgraphs` function. We can also specify that we only want to parse the "celluar_component"
sub-ontology of GO (the "supergraph namespace"), since we are only interested in concepts of this type. Although it is
redundant, we can also play it safe and limit subgraph creation to only consider terms listed in "cellular_component" as
well (the "subgraph namespace").

   .. code:: bash

      python3 ARK.GOcats/gocats/gocats.py create_subgraphs ~/go.obo ~/cell_locations.csv ~/cell_locations_output --supergraph_namespace=cellular_component --subgraph_namespace=cellular_component

The results will be output to ~/cell_locations_output.

Let's look at the output files
------------------------------

In the output directory (i.e. ~/cell_locations_output) we can see several files. The following table describes what
can be found in each:

   +--------------------------------+---------------------------------------------------------------------------------------------------+
   |          File Name             |                                       Description                                                 |
   +================================+===================================================================================================+
   | GC_content_mapping.json        | JSON version of Python dictionary (keys: concept root nodes, values: list of subgraph term nodes).|
   +--------------+-----------------+---------------------------------------------------------------------------------------------------+
   | GC_content_mapping.json_pickle | Same as above, but a JSONPickle version of the dictionary.                                        |
   +--------------+-----------------+---------------------------------------------------------------------------------------------------+
   | GC_id_mapping.json             | JSON version of Python dictionary (keys: subgraph term nodes, values: list of concept roots).     |
   +--------------+-----------------+---------------------------------------------------------------------------------------------------+
   | GC_id_mapping.json_pickle      | Same as above, but a JSONPickle version of the dictionary.                                        |
   +--------------+-----------------+---------------------------------------------------------------------------------------------------+
   | id_translation.json_pickle     | A JSONPickle version of a Python dictionary mapping GO IDs to the name of the term.               |
   +--------------+-----------------+---------------------------------------------------------------------------------------------------+
   | NetworkTable.csv               | A csv version of id_translation for visualizing in Cytoscape (best results with --map_supersets)  |
   +--------------+-----------------+---------------------------------------------------------------------------------------------------+
   | subgraph_report.txt            | A summary of the subgraphs extracted for mapping. See below for more details.                     |
   +--------------+-----------------+---------------------------------------------------------------------------------------------------+

We can look in subgraph_report.txt to get an overview of what our subgraphs contain, how they were constructed, and how
they compare to the overall GO graph.