#!/bin/sh
# USAGE: run.sh <ontology_file> <input_directory> <output_directory>

ONTOLOGY_FILE="$1"
INPUT_DIRECTORY="$2"
OUTPUT_DIRECTORY="$3"

if [ ! -d "${INPUT_DIRECTORY}" ]; then
	mkdir ${INPUT_DIRECTORY}
fi

if [ ! -d "${OUTPUT_DIRECTORY}" ]; then
	mkdir ${OUTPUT_DIRECTORY}
fi 

echo "Creating input files of GO terms to be mapped by Map2Slim."
python3 gotermcollect.py ${ONTOLOGY_FILE} ${INPUT_DIRECTORY}

DECOY_GAF="${INPUT_DIRECTORY}/GO-GO_GAF.goa" # Created by gotermcollect.py

echo "Mapping GO terms with Map2Slim."
for subdir in ${INPUT_DIRECTORY}/*; do
	if [ -d "${subdir}" ]; then # Skip for non-directory, input files in the INPUT_DIRECTORY
		echo "Calling m2s_runner.sh for ${subdir}"
		./submit_spartan_24.pl ./m2s_runner.sh ${subdir} ${OUTPUT_DIRECTORY} ${ONTOLOGY_FILE} ${DECOY_GAF}
	fi
done
echo "Spartan submissions completed."
