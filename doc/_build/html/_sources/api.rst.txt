========================
The GOcats API Reference
========================

Modules
~~~~~~~
The following modules are located in /ARK.GOcats/gocats.

.. automodule:: gocats
   :members:
   :private-members:

Directed Acyclic Graph (DAG)
----------------------------

.. automodule:: dag
   :members:
   :private-members:

Gene Ontology Directed Acylic Graph (GODAG)
-------------------------------------------

.. automodule:: godag
   :members:

Directed Acyclic Subgraph (SubDAG)
----------------------------------

.. automodule:: subdag
   :members:

Ontology Parser
---------------

.. automodule:: ontologyparser
   :members:

Decoy Gene Anotation File Creator (DecoyGAF)
--------------------------------------------

.. automodule:: decoygaf
   :members:

UniProt Subcellular Locations Parser
------------------------------------
.. automodule:: uniprotsubcellparser
   :members:

Tools
-----

.. automodule:: tools
   :members:

Test Scripts
~~~~~~~~~~~~
Test scripts can be found in multiple subdirectories. Their location depends on which aspect of the project they test. Check each subsection to see where each test is located.

Map2Slim Mapping Error Testing
------------------------------
The following scripts are located /ARK.GOcats/gocats/tests/Map2SlimMappingTest

These scripts are for enumerating the potential scoping and scaling errors that Map2Slim makes by evaluating all
relationship types in the same way. We are using Map2Slim's --idfile option to map custom GO terms, instead of mapping
to a whole GOslim. The goal is to produce an all-against-all mapping for all terms in Gene Ontology (or for individual
sub-ontologies of GO) so that all possilbe term-to-term mappings that Map2Slim can make are evaluated. However, because
Map2Slim does not natively allow this kind of evaluation, we were foced to perform two workarounds:

1. The first workaround is mapping GO terms to themselves. Map2Slim is designed to map *gene* annotations within a Gene
Annotation File (GAF) to a GO term in a GO slim or to a set of manually-defined GO terms. Therefore we created a "decoy"
GAF which replaced the "gene name" field with a string representing a GO term from the GO ontology file, and its row
contains a string of the same GO term in its "GO annotation" field. Map2Slim can read, process, and map the GO
annotation field in the same way it normally does. In this way, the resulting mapped gaf contains a GO term string
mapped to another GO term that has been mapped to the provided target GO term list.

This was accomplished in gotermcollect.py

2. The second workaround is that Map2Slim removes all mappings that are subsumed by other mappings. This means that if
one were to supply our "decoy GAF" with an --idfile listing of all terms in GO we would receive only mappings of GO
terms to themselves (all other mappings would be subsumed by one another). To overcome this we supplied a single GO term
in the --idfile option at a time for all terms in go, and then converged all resulting mappings together from the
resulting ~44,000 GAF output files (ignoring self-mappings and redundancy).

This was accomplished using gotermcollect.py, outputprocessing.py, m2s_runner.sh, run.sh, and a Perl script wihich submitted jobs to a TORUQUE cluster (submit_spartan_24.pl).

Has_Part mapping error analysis (hp_mapping_testing.py)
-------------------------------------------------------
The following script is located in /ARK.GOcats/gocats

Similar to Map2Slim error testing, this script enumerates the errors made by the misinterpretation of a problematic edge
type. In this case this involves enumerating all has_part paths in GO without reversing the semantic directionality of
the edge. GOcats perferms this reversal by defalut, creating a proper scoping/scaling interpretation of the relationship
with respect to term categorization. This test reverses the direcitonality back to its original, problematic state and
enumerates how many mappings are created as a result.

Speed Test
----------
This script is located in /ARK.GOcats/runscripts/Tests

Run Scripts
~~~~~~~~~~~
All project-level runscripts are located under /ARK.GOcats/runscripts

run.sh
------

run_map_supersets.sh
--------------------

FullSubgraphInclusion.sh
------------------------

GOcatsGenericHPAMapping.sh
--------------------------
