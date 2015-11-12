#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

SED_EXPR=$1
SUFFIX=$2

# The basenames of interesting config files.
BASES="master preserveNonUndoableChains removeNonUndoableChains onlyUndo onlyRemove nanoporeHacks"
# The branches each config file should use.
declare -A BRANCH=(["master"]="master"
                   ["preserveNonUndoableChains"]="onlineCactus"
                   ["removeNonUndoableChains"]="onlineCactus"
                   ["onlyUndo"]="onlineCactus"
                   ["onlyRemove"]="onlineCactus"
                   ["nanoporeHacks"]="nanoporeHacks")

for base in ${BASES}; do
    runLabel=${base}_${SUFFIX}
    echo "running $runLabel"
    sed "${SED_EXPR}" ${base}.xml > ${runLabel}.xml
    PYTHONPATH=bin:src:$PYTHONPATH ./bin/runBenchmarks.py --cactusConfigFile ${runLabel}.xml --progressiveCactusBranch ${BRANCH[$base]} --tests evolverMammals,evolverPrimates testRegions ${runLabel} --outputDir output-${runLabel} --batchSystem parasol --defaultMemory 9589934593 --bigMaxCpus 30 --maxThreads 30 --parasolCommand='/cluster/home/jcarmstr/bin/parasol -host=ku' --jobTree /hive/users/jcarmstr/tmp/jobT${runLabel} &
done
