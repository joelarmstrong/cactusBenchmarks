#!/usr/bin/env python
"""
Runs a set of benchmarks/integration tests for progressiveCactus.
"""
import sys
import os
from bioio import system
from argparse import ArgumentParser
from testSet import TestSet

def initializeProgressiveCactus(opts):
    """Points progressiveCactus to the correct commit and compiles."""
    os.chdir(opts.progressiveCactusDir)
    system("git fetch")
    system("git checkout %s" % (opts.progressiveCactusBranch))
    system("git pull")
    system("git submodule sync")
    system("git submodule update --init --recursive")
    system("make ucscClean")
    if opts.cactusBranch is not None:
        os.chdir("submodules/cactus")
        system("git fetch")
        system("git checkout %s" % (opts.cactusBranch))
        os.chdir(opts.progressiveCactusDir)
    system("make ucsc")

def setupTestSets(dir, outputDir, tests=None):
    """Initializes the TestSet classes.

    By default, a test is created for each directory in the
    supplied dir. If the tests parameter is not None, it's assumed
    to be a comma-separated list of test directories (in "dir") to use
    instead.
    """
    testPaths = None # for proper scoping
    if tests is None:
        testPaths = [os.path.join(dir, d) for d in os.listdir(dir)]
        testPaths = filter(os.path.isdir, testPaths)
    else:
        testPaths = [os.path.join(dir, d) for d in tests.split(",")]
        if not all([os.path.isdir(d) for d in testPaths]):
            raise RuntimeError("Test paths not found: %s" % [not os.path.isdir(d) for d in testPaths])

    tests = []
    for path in testPaths:
        test = TestSet(path, path, os.path.join(path, "config"),
                       os.path.join(outputDir, os.path.basename(os.path.normpath(path))))
        tests.append(test)
    return tests

def parseArgs(args):
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('progressiveCactusDir',
                        help="Location of progressiveCactus",
                        type=os.path.abspath)
    parser.add_argument('testRegionsDir',
                        help="directory containing test regions",
                        type=os.path.abspath)
    parser.add_argument('label',
                        help="A label for this run")
    parser.add_argument('--tests',
                        help="list of tests to run (comma-separated)",
                        default=None)
    parser.add_argument('--progressiveCactusBranch',
                        help="branch of progressiveCactus to switch to",
                        default="master")
    parser.add_argument('--cactusBranch', help="branch of cactus to switch to",
                        default=None)
    parser.add_argument('--cactusConfigFile',
                        help="config xml to use instead of default",
                        default=None)
    parser.add_argument('--outputDir',
                        help="dir to place test results in",
                        default="output",
                        type=os.path.abspath)
    parser.add_argument('--stats',
                        help="output stats file with jobTree stats",
                        default=False, action="store_true")
    return parser.parse_args(args[1:])

def main(args):
    opts = parseArgs(args)

    # setup progressiveCactus to point to the right commit, and run
    # make
    initializeProgressiveCactus(opts)

    tests = setupTestSets(opts.testRegionsDir, opts.outputDir, opts.tests)

    # ensure our output dir exists, and redirect our stderr there for
    # logging purposes.
    if not os.path.isdir(opts.outputDir):
        os.mkdir(opts.outputDir)
    sys.stderr = open(os.path.join(opts.outputDir, "log"), 'w')

    for test in tests:
        test.run(opts)

    # Put git commit in the output dir
    os.chdir(opts.progressiveCactusDir)
    system("git rev-parse HEAD > %s/progressiveCactus_version" % opts.outputDir)
    os.chdir(os.path.join(opts.progressiveCactusDir, "submodules/cactus"))
    system("git rev-parse HEAD > %s/cactus_version" % opts.outputDir)

    # Put config in the output dir
    if opts.cactusConfigFile is not None:
        system("cp %s %s/config.xml" % (opts.cactusConfigFile, opts.outputDir))
    else:
        # we used the default config
        system("cp %s %s/config.xml" % (os.path.join(opts.progressiveCactusDir,
                                                     "submodules/cactus/cactus_progressive_config.xml"),
                                        opts.outputDir))

if __name__ == '__main__':
    main(sys.argv)
