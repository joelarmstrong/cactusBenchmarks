#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

CACTUS_BENCHMARKS_DIR=$(readlink -f $(dirname $0)/..)
cd "$CACTUS_BENCHMARKS_DIR"/testRegions
wget -m -nH --cut-dirs=2 --no-parent -e robots=off -R index.html* http://hgwdev.cse.ucsc.edu/~jcarmstr/testRegions/
