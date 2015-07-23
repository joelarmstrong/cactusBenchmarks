import ConfigParser
from bioio import getTempDirectory
from bioio import system
from bioio import nameValue
import os
import sys
import re

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
            os.makedirs(self.outputDir)
        self.hal = os.path.join(outputDir, "out.hal")

    def parseConfig(self, configPath):
        """Parses the configuration file."""
        self.config = ConfigParser.ConfigParser()
        self.config.read(configPath)
        self.seqFile = self.getOption("Alignment", "seqFile", required=True)

    def getOption(self, section, option, default=None, required=False):
        """Gets an option from the test config, with an optional default.

        Throws an exception if required is True and the option or
        section aren't present, and returns None if no option is found
        and no default is provided."""
        try:
            return self.config.get(section, option)
        except ConfigParser.Error:
            if required:
                raise RuntimeError("Could not find required option %s in"
                                   " section %s of the config file for region "
                                   "%s" % (option, section, self.label))
            return default

    def align(self, progressiveCactusDir, configFile):
        """Run the actual alignment."""
        os.chdir(self.path)

        configFile = nameValue("config", configFile)
        root = nameValue("root", self.getOption("Alignment", "root"))
        system("%s/bin/runProgressiveCactus.sh --stats %s %s %s %s %s" % (
            progressiveCactusDir, configFile, root, self.seqFile, self.workDir,
            self.hal))

        # Copy the alignment log to the output directory
        system("cp %s %s" % (os.path.join(self.workDir, "cactus.log"),
                             self.outputDir))

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
        truth = self.getOption('Evaluation', 'truth')

        # Extract the maf for our alignment
        test = os.path.join(getTempDirectory(), 'test.maf')
        system("hal2maf --onlySequenceNames --global --noAncestors %s %s" % \
               (self.hal, test))
        system("mafComparator --maf1 %s --maf2 %s --out %s" % (truth, test, os.path.join(self.outputDir, "mafComparator.xml")))

    def makeDotplot(self):
        """Puts a dotplot in dotplot.pdf, given the dotplot option

        The dotplot option has the format:
        "genomeX.seqX:startX-endX,genomeY.seqY:startY-endY"
        """
        dotplotString = self.getOption("Evaluation", "dotplot")
        match = re.match(
            r'(.*?)\.([^:,]*),(.*?)\.([^:]*)',
            # r'(.*?)\.([^:,]*):?([0-9]*)?-?([0-9]*)?,(.*?)\.([^:]*):?([0-9]*)?-?([0-9]*)?',
            dotplotString)
        genomeX, seqX, genomeY, seqY = match.groups()
        tempFile = os.path.join(self.workDir, "tmp.dotplot")
        system("runDotplot.py %s %s %s %s %s > %s" % \
               (self.hal, genomeX, seqX, genomeY, seqY, tempFile))
        system("plotDotplot.R %s %s" % (tempFile, os.path.join(self.outputDir,
                                                               "dotplot.pdf")))

    def getCoalescences(self):
        """Runs the "correct-coalescences" evaluation on the test set.

        The reference genome is given by the coalescenceRefGenome
        option in the config file.
        """
        refGenome = self.getOption("Evaluation", "coalescenceRefGenome")
        system("scoreHalPhylogenies.py --jobTree %s/jobTree %s %s %s" % \
               (getTempDirectory(), self.hal, refGenome,
                os.path.join(self.outputDir, "coalescences.xml")))

    def run(self, opts):
        try:
            progressiveCactusDir = opts.progressiveCactusPreBuilt if opts.progressiveCactusPreBuilt else opts.progressiveCactusDir
            self.align(progressiveCactusDir, opts.cactusConfigFile)
            self.makeHub()
            self.getCoverage()
            if self.getOption("Evaluation", "truth") is not None:
                self.getPrecisionRecall()
            if self.getOption("Evaluation", "dotplot") is not None:
                self.makeDotplot()
            if self.getOption("Evaluation", "coalescenceRefGenome") is not None:
                self.getCoalescences()
        except Exception, e:
            sys.stderr.write("Could not complete test on region %s. "
                             "Error: %s\n" % (self.path, repr(e)))
