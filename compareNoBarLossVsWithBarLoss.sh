#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

function lift {
    HAL=$1
    SRC_GENOME=$2
    DEST_GENOME=$3
    DEST_FILE=$4
    halStats --bedSequences "$SRC_GENOME" "$HAL" | halLiftover "$HAL" \
        "$SRC_GENOME" stdin "$DEST_GENOME" "$DEST_FILE"
}

for noBar in true false; do
    for branch in development phylogeny; do
        outputDir=output-"$branch"
        if [[ $noBar == true ]]; then
            outputDir="$outputDir-noBar"
        fi
        lift "$outputDir/output/mammals1.hal" simMouse_chr6 simRat_chr6 "$branch-$noBar-lifted.bed"
    done
    bedtools subtract -a "development-$noBar-lifted.bed" -b "phylogeny-$noBar-lifted.bed" > "$noBar-loss.bed"
done
