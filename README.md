# cactusBenchmarks

cactusBenchmarks is an infrastructure for reproducibly running
different versions and configurations of
[progressiveCactus](https://github.com/glennhickey/progressiveCactus)
on a variety of test sets.

## Installation

First, download the test regions (which are too large to store in git):

```
./testRegions/download_test_regions.sh
```

## Running with Docker

Use `bin/run.sh`:

```
./bin/run.sh [OPTIONS] testLabel
```

You can run any number of tests simultaneously, with different
versions and config files, without the runs interfering with one
another.

## Running without Docker

Ensure you're in the progressiveCactus environment, and that mafComparator and the dotplot scripts are in your PATH. Use `bin/runBenchmarks.py`:

```
./bin/runBenchmarks.py [OPTIONS] progressiveCactusDir testRegionsDir testLabel
```

You should only run one instance of runBenchmarks.py at a time per
progressive cactus directory.

## Options

### --tests TESTS
list of tests to run (comma-separated)
### --progressiveCactusBranch PROGRESSIVECACTUSBRANCH
branch of progressiveCactus to switch to
### --cactusBranch CACTUSBRANCH
branch of cactus to switch to
### --cactusConfigFile CACTUSCONFIGFILE
config xml to use instead of default. When using Docker, this is
copied into the container, so it may be safely modified after the
container starts running.
### --outputDir OUTPUTDIR
dir to place test results in
### --stats
output stats file with jobTree stats
