from ConfigParser import ConfigParser
from bioio import getTempDirectory
from bioio import system
from bioio import nameValue
import os
import sys

class TestSet:
    """Represents a single test region.

    Using the run() method will compute the alignment for the test
    set, followed by several metrics (coverage, precision, recall,
    etc.) and (if desired) an assembly hub.
    """
    def __init__(self, label, path, configPath, outputDir):
        self.label = label
        self.path = path
        self.parseConfig(configPath)
        self.workDir = getTempDirectory()
        self.outputDir = outputDir
        if not os.path.exists(self.outputDir):
            os.mkdir(self.outputDir)
        self.hal = os.path.join(outputDir, "out.hal")

    def parseConfig(self, configPath):
        """Parses the configuration file."""
        self.config = ConfigParser()
        self.config.read(configPath)
        if not self.config.has_option("Alignment", "seqFile"):
            raise RuntimeError("Test set config at %s does not point to an "
                               "input seqFile." % configPath)
        self.seqFile = self.config.get("Alignment", "seqFile")

    def align(self, progressiveCactusDir, configFile):
        """Run the actual alignment."""
        os.chdir(self.path)

        configFile = nameValue("config", configFile)
        system("%s/bin/runProgressiveCactus.sh --stats %s %s %s %s" % (
            progressiveCactusDir, configFile, self.seqFile, self.workDir,
            self.hal))

    def makeHub(self):
        system("hal2assemblyHub.py --hub %s --longLabel %s --shortLabel %s %s --jobTree %s/jobTree %s" % (self.label, self.label, self.label, self.hal, getTempDirectory(), os.path.join(self.outputDir, "hub")))

    def getCoverage(self):
        system("halStats --allCoverage %s > %s" % (self.hal, os.path.join(self.outputDir, "coverage")))

    def getPrecisionRecall(self):
        """Find the precision and recall relative to the true alignment.

        Assumes that the test set config has specified a true MAF
        containing only sequence names (not UCSC-styled "genome.chr"
        names).
        """
        truth = self.config.get('Evaluation', 'truth')

        # Extract the maf for our alignment
        test = os.path.join(getTempDirectory(), 'test.maf')
        system("hal2maf --onlySequenceNames --global --noAncestors %s %s" % \
               (self.hal, test))
        system("mafComparator --maf1 %s --maf2 %s --out %s" % (truth, test, os.path.join(self.outputDir, "mafComparator.xml")))

    def run(self, opts):
        try:
            self.align(opts.progressiveCactusDir, opts.cactusConfigFile)
            self.makeHub()
            self.getCoverage()
            if self.config.has_option("Evaluation", "truth"):
                self.getPrecisionRecall()
        except Exception, e:
            sys.stderr.write("Could not complete test on region %s. "
                             "Error: %s\n" % (self.path, repr(e)))
