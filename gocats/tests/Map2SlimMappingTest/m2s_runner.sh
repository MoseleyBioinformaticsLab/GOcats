#!/bin/sh

INPUT_SUBDIR="$1"
OUTPUT_DIR="$2"
ONTOLOGY_FILE="$3"
DECOY_GAF="$4"
OUTPUT_SUBDIR_NAME="${INPUT_SUBDIR##*/}" # The output subdirectory will have the same name as its input
OUTPUT_SUBDIR="$OUTPUT_DIR/$OUTPUT_SUBDIR_NAME"

OWLTOOLS_DIR=$HOME/owltools/OWLTools-Runner/bin # Change this to where your owltools is installed
echo "working on node: "
hostname

if [ ! -d "${OUTPUT_DIR}" ]; then
	mkdir ${OUTPUT_DIR}
fi

if [ ! -d "${OUTPUT_SUBDIR}" ]; then
	mkdir ${OUTPUT_SUBDIR}
fi

for file in ${INPUT_SUBDIR}/*; do
	OUTPUT_FILE_NAME="${file##*/}"
	if [ ! -e ${OUTPUT_SUBDIR}/${OUTPUT_FILE_NAME} ]; then
		echo "Working on mapping ${OUTPUT_FILE_NAME}"
		${OWLTOOLS_DIR}/owltools ${ONTOLOGY_FILE} --gaf ${DECOY_GAF} --map2slim --idfile ${file} --write-gaf ${OUTPUT_SUBDIR}/${OUTPUT_FILE_NAME} >> /dev/null # Dump the map2slim output.
		echo "Finished mapping ${OUTPUT_FILE_NAME}. Results stored in ${OUTPUT_SUBDIR}/${OUTPUT_FILE_NAME}"
	fi
done
