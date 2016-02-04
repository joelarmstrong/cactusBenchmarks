import os
import sys
import re
from jobTree.scriptTree.target import Target
import ConfigParser
from bioio import getTempDirectory
from bioio import system, popenCatch
from bioio import nameValue
from glob import glob
from getMisalignmentWigs import getWigsFromXML

class TestSet(Target):
    """Represents a single test region.

    Using the run() method will compute the alignment for the test
    set, followed by several metrics (coverage, precision, recall,
    etc.) and (if desired) an assembly hub.
    """
    def __init__(self, label, path, configPath, outputDir, opts):
        Target.__init__(self)
        self.label = label
        self.path = path
        self.parseConfig(configPath)
        self.workDir = getTempDirectory()
        self.outputDir = outputDir
        self.wigDir = getTempDirectory()
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        self.hal = os.path.join(outputDir, "out.hal")
        self.opts = opts

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
        """Make an assembly hub for the test set, and place it in
        outputDir/hub."""
        cmd = "hal2assemblyHub.py --hub %s --longLabel %s --shortLabel %s %s --jobTree %s/jobTree %s" % (self.label, self.label, self.label, self.hal, getTempDirectory(), os.path.join(self.outputDir, "hub"))
        if self.getOption("Evaluation", "misalignmentWigTrack") is not None:
            cmd += " --wigDirs %s --nowigLiftover" % ",".join(glob(os.path.join(self.wigDir, '*')))
        system(cmd)

    def getCoverage(self):
        """Report all-by-all coverage to outputDir/coverage."""
        system("halStats --allCoverage %s > %s" % (self.hal, os.path.join(self.outputDir, "coverage")))

    def getMafComparatorXML(self):
        """Find the precision and recall relative to the true alignment by
        running mafComparator.

        Assumes that the test set config has specified a true MAF
        containing only sequence names (not UCSC-styled "genome.chr"
        names).

        Also parses the "wiggle" parts of the XML into proper .wig
        files, if the misalignmentWigTrack option is enabled in the
        test set's config.
        """
        truth = self.getOption('Evaluation', 'truth')

        # Extract the maf for our alignment
        test = os.path.join(getTempDirectory(), 'test.maf')
        system("hal2maf --onlySequenceNames --global --noAncestors %s %s" % \
               (self.hal, test))

        xmlPath = os.path.join(self.outputDir, "mafComparator.xml")
        comparatorCmd = "mafComparator  --samples 20000000 --maf1 %s --maf2 %s --out %s" % (truth, test, xmlPath)
        if self.getOption("Evaluation", "misalignmentWigTrack") is not None:
            # Add the options to generate the requested wiggle track
            comparatorCmd += " " + nameValue("wigglePairs", self.getOption("Evaluation", "misalignmentWigTrack"))
            comparatorCmd += " --wiggleBinLength 1"
        system(comparatorCmd)

        if self.getOption("Evaluation", "misalignmentWigTrack") is not None:
            # Extract the wiggle files
            genome = getGenomeForSequence(self.hal, self.getOption("Evaluation", "misalignmentWigTrack").split(":")[0])
            system("mkdir -p %s %s" % (os.path.join(self.wigDir, "underalignment", genome), os.path.join(self.wigDir, "overalignment", genome)))
            underalignmentPath = os.path.join(self.wigDir, "underalignment", genome, genome + ".wig")
            overalignmentPath = os.path.join(self.wigDir, "overalignment", genome, genome + ".wig")
            getWigsFromXML(xmlPath, underalignmentPath, overalignmentPath)

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

    def run(self):
        """Do everything that needs to be done to the test set: alignment,
        evaluation, and visualization."""
        self.align(self.opts.progressiveCactusDir, self.opts.cactusConfigFile)
        self.getCoverage()
        if self.getOption("Evaluation", "truth") is not None:
            self.getMafComparatorXML()
        if self.getOption("Evaluation", "dotplot") is not None:
            self.makeDotplot()
        if self.getOption("Evaluation", "coalescenceRefGenome") is not None:
            self.getCoalescences()
        self.makeHub()

def getGenomeForSequence(halFile, sequenceName):
    """Find the genome that has a given sequence, assuming that sequence
    names are unique in the alignment.
    """
    genomes = popenCatch("halStats --genomes %s" % halFile).split()
    sequenceToGenome = {}
    for genome in genomes:
        sequences = popenCatch("halStats --sequences %s %s" % (genome, halFile)).split()
        for sequence in sequences:
            sequenceToGenome[sequence] = genome
    return sequenceToGenome[sequenceName]
