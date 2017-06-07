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

Create a keyword file
---------------------

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
   |   nucleus    | nucleus;nuclei;nuclear                   |
   +--------------+------------------------------------------+
   |   lysosome   | lysosome;lysosomal;lysosomes             |
   +--------------+------------------------------------------+
   |   vesicle    | vesicle;vesicles                         |
   +--------------+------------------------------------------+
   |     er       | endoplasmic;sarcoplasmic;reticulum       |
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

Download the Gene Ontology .obo file
------------------------------------

The go.obo file is available here: http://www.geneontology.org/page/download-ontology. Be sure to download the
.obo-formatted version. All releases of GO in this format as of Jan 2015 have been verified to be compatible with
GOcats. We'll assume this database file is located in the home directory and is called "go.obo."

Extract subgraphs and create concept mappings
---------------------------------------------

This is where GOcats does the heavy lifting. We'll assume GOcats was already installed via pip or the repository was
already cloned into the home directory (refer to :doc:`guide` for instructions on how to install GOcats). We can now use
Python to run the :func:`gocats.gocats.create_subgraphs` function. We can also specify that we only want to parse the
"cellular_component" sub-ontology of GO (the "supergraph namespace"), since we are only interested in concepts of this
type. Although it is redundant, we can also play it safe and limit subgraph creation to only consider terms listed in
"cellular_component" as well (the "subgraph namespace"). Run the following if you hav installed via pip (if running from
the Git repository navigate to the GOcats directory or add this directory to your PYTHONPATH beforehand).

   .. code:: bash

      python3 -m gocats create_subgraphs ~/go.obo ~/cell_locations.csv ~/cell_locations_output --supergraph_namespace=cellular_component --subgraph_namespace=cellular_component

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

**subgraph_report.txt**

The first few lines give an overview of the subgraphs and supergraph (which is the full GO graph, unless a
supergraph_namespace filter was used). In our example case, the supergraph is the cellular_component ontology of GO.

In each divided section, the first line indicates the subgraph name (the one provided from column 1 in the keyword file)
. The following describes the meaning of the values in each section:

   - **Subgraph relationships**: the prevalence of relationship types in the subgraph.
   - **Seeded size**: how many GO terms were initially filtered from GO with the keyword list.
   - **Representative node**: the name of the GO term chosen as the root for that concept's subgraph.
   - **Nodes added**: the number of GO terms added when extending the seeded subgraph to descendants not captured by the
     initial search.
   - **Non-subgraph hits (orphans)**: GO terms that were captured by the keyword search, but do not belong to the
     subgraph.
   - **Total nodes**: the total number of GO terms in the subgraph.

Loading mapping files programmatically (optional)
-------------------------------------------------

While GOcats can use the mapping files described in the previous section to map terms in a GAF, it may also be useful to
load them into your own scripts for use. Since the mappings are saved in JSON and JSONPickle formats, it is relatively
simple to load them in programmatically:

.. code:: Python

   >>># Loading a JSON file
   >>>import json
   >>>with open('path_to_json_file', 'r') as json_file:
   >>>    json_str = json_file.read()
   >>>    json_obj = json.loads(json_str)
   >>>my_mapping = json_obj

   >>># Loading a JSONPickle file
   >>>import jsonpickle
   >>>with open('path_to_jsonpickle_file', 'r') as jsonpickle_file:
   >>>    jsonpickle_str = jsonpickle_file.read()
   >>>    jsonpickle_obj = jsonpickle.decode(jsonpickle_str, keys=True)
   >>>my_mapping = jsonpickle_obj

Using GOcats to map specific gene annotations in a GAF to custom categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With mapping files produced from the previous steps, it is possible to create a GAF with annotations mapped to the
categories, or concepts, that we define. Let's consider our current "cell_locations" example and imagine that we have
some gene set containing annotations in a GAF called "dataset_GAF.goa" in the home directory. To map these annotations,
use the :func:`gocats.gocats.categorize_dataset` option. Again, this should work from any location if you've installed
via pip, otherwise navigate to the GOcats directory or add this directory to your PYTHONPATH and run the following:

.. code:: bash

   # Note that you need to use the GC_id_mapping.json_pickle file for this step
   python3 -m gocats categorize_dataset ~/datasetGAF.goa ~/cell_locations_output/GC_id_mapping.json_pickle ~/mapped_dataset mapped_GAF.goa

Here, we named the output directory "~/mapped_dataset" and we named the mapped GAF "mapped_GAF.goa". The mapped gaf and
a list of unmapped genes will be stored in the output directory.

Exploring Gene Ontology graph in a Python interpreter or in your own Python project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you've installed GOcats via pip, importing should work as expected. Otherwise, navigate to the Git project directory,
open a Python 3.4+ interpreter, and import GOcats:

.. code:: Python

   >>> from gocats import gocats as gc

Next, create the graph object using :func:`gocats.gocats.build_graph_interpreter`. Since we have been looking at the
cellular_component sub-ontology in this example, we can specify that we only want to look at that part of the graph with
the supergraph_namespace option. Additionally we can filter the relationship types using the allowed_relationships
option (only is_a, has_part, and part_of exist in cellular_component, so this is just for demonstration):

.. code:: Python

   >>> # May filter to GO sub-ontology or to a set of relationships.
   >>> my_graph = gc.build_graph_interpreter("~/go.obo", supergraph_namespace=cellular_component, allowed_relationships=["is_a", "has_part", "part_of"])
   >>> full_graph = gc.build_graph_interpreter("~/go.obo")

The filtered graph (my_graph) and the full GO graph (full_graph) can now be explored.

The graph object contains an **id_index** which allows one to access node objects by GO IDs like so:

.. code:: Python

   >>>my_node = my_graph.id_index['GO:0004567']

It also contains a node_list and an edge_list.

Edges and nodes in the graph are objects themselves.

.. code:: Python

   >>>print(my_node.name)

Here is a list of some important graph, node, and edge data members and properties:

**Graph**
   - node_list: list of **node** objects in the graph.
   - edge_list: list of **edge** objects in the graph.
   - id_index: dictionary of node IDs that point to their respective **node** objects.
   - vocab_index: dictionary listing every word used in the gene ontology, pointing to **node** objects those words can be found in.
   - relationship_index: dictionary of relationships in the supergraph, pointing to their respective relationship objects.
   - root_nodes: a set of root nodes of the supergraph.
   - orphans: a set of nodes which have no parents.
   - leaves: a set of nodes which have no children.

**Node**
   - id
   - name
   - definition
   - namespace
   - edges: a set of **edges** that connect the node.
   - parent_node_set
   - child_node_set
   - descendants: a set of recursive graph children.
   - ancestors: a set of recursive graph parents.

**Edge**
   - node_pair_id: tuple of IDs of the **nodes** connected by the edge.
   - node_pair: a tuple of the **node objects** connected by the edge.
   - relationship_id: the ID of the relationship type (i.e. the name of the relationship).
   - relationship: the relationship object used to describe the edge
   - parent_id
   - parent_node
   - child_id
   - child_node
   - forward_node: see :doc:`api`
   - reverse_node: see :doc:`api`

Plotting subgraphs in Cytoscape for visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Coming soon!
