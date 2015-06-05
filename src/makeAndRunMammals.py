#!/usr/bin/env python
"""Hacky pseudo-shell-script to update and make the specified
branch of progressiveCactus and/or its submodules, then build it, then
run the simulated mammal alignment and test it against the truth
maf.
"""
import os
import sys
from argparse import ArgumentParser
import subprocess


def runMammals(opts):
    os.chdir("submodules/cactusTestData/evolver/mammals/loci1/")
    with open("mammals1.txt", 'w') as seqFile:
        seqFile.write("""((simHuman_chr6:0.144018,(simMouse_chr6:0.084509,simRat_chr6:0.091589):0.271974):0.020593,(simCow_chr6:0.18908,simDog_chr6:0.16303):0.032898);

simCow_chr6 simCow.chr6
simDog_chr6 simDog.chr6
simHuman_chr6 simHuman.chr6
simMouse_chr6 simMouse.chr6
simRat_chr6 simRat.chr6
        """)
    cmdline = "../../../../../bin/runProgressiveCactus.sh mammals1.txt work mammals1.hal"
    if opts.cactusConfigFile is not None:
        cmdline += " --config %s" % opts.cactusConfigFile
    if opts.stats:
        cmdline += " --stats "
    system(cmdline)
    os.chdir(opts.progressiveCactusDir)

def scoreMammals(opts):
    """Run mafComparator on the mammal1 result and the truth maf and put
    the resulting xml in the output dir.
    """
    os.chdir("submodules/cactusTestData/evolver/mammals/loci1/")
    system("%s/submodules/hal/bin/hal2maf --noAncestors --onlySequenceNames --global mammals1.hal mammals1.maf" % opts.progressiveCactusDir)
    system("%s/submodules/mafTools/bin/mafComparator --maf1 mammals1.maf --maf2 all.burnin.maf --out %s/mammals1.xml" % (opts.progressiveCactusDir, opts.outputDir))
    if opts.cactusConfigFile is not None:
        system("cp %s %s/config.xml" % (opts.cactusConfigFile, opts.outputDir))
    system("cp work/cactus.log %s" % (opts.outputDir))
    system("cp mammals1.hal %s" % (opts.outputDir))
    if opts.stats:
        system("PYTHONPATH=%s/submodules/:$PYTHONPATH %s/submodules/jobTree/bin/jobTreeStats work/jobTree > %s/stats" % (opts.progressiveCactusDir, opts.progressiveCactusDir, opts.outputDir))
    system("ls")
    os.chdir(opts.progressiveCactusDir)

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('progressiveCactusDir',
                        help="Location of progressiveCactus")
    parser.add_argument('--progressiveCactusBranch',
                        help="branch of progressiveCactus to switch to",
                        default="master")
    parser.add_argument('--cactusBranch', help="branch of cactus to switch to",
                        default=None)
    parser.add_argument('--cactusConfigFile',
                        help="config xml to use instead of default",
                        default=None)
    parser.add_argument('--outputDir',
                        help="dir to place output mafComparator xml in",
                        default="/output")
    parser.add_argument('--stats',
                        help="output stats file with jobTree stats",
                        default=False, action="store_true")
    opts = parser.parse_args()
    opts.progressiveCactusDir = os.path.abspath(opts.progressiveCactusDir)
    opts.outputDir = os.path.abspath(opts.outputDir)
    system("mkdir -p %s" % opts.outputDir)
    if opts.cactusConfigFile is not None:
        # make a backup of the cactus config xml since it could be
        # modified on the host
        opts.cactusConfigFile = os.path.abspath(opts.cactusConfigFile)
        system("cp %s %s" % (opts.cactusConfigFile, "/tmp/"))
        opts.cactusConfigFile = os.path.join(
            "/tmp",
            os.path.basename(opts.cactusConfigFile))
    else:
        opts.cactusConfigFile = os.path.join(opts.progressiveCactusDir,
                                             "submodules/cactus/cactus_progressive_config.xml")
    makeUcscClean = False
    os.chdir(opts.progressiveCactusDir)
    initializeProgressiveCactus(opts)
    initializeSubmodules(opts)
    if makeUcscClean:
        system("make ucscClean")
    system("make ucsc")
    runMammals(opts)
    scoreMammals(opts)

if __name__ == '__main__':
    main()
