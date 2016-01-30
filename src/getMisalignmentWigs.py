#!/usr/bin/env python
"""Parse a mafComparator XML produced with the "wigglePairs" option to
generate WIG files. Assumes maf1 is the truth maf and maf2 is the test
maf.
"""
from argparse import ArgumentParser
import xml.etree.ElementTree as ET

def parseToWigString(comparatorWig, refChrom, binLength):
    """Parses a wiggle string from the XMLComparator format to the
    official UCSC WIG format."""
    data = "\n".join(comparatorWig.split(","))
    header = "fixedStep chrom=%s start=1 step=%s span=%s\n" % (refChrom, binLength, binLength)
    return header + data

def getWigsFromXML(xmlPath, underalignmentWig, overalignmentWig):
    """Creates two wiggle files showing misalignment from a mafComparator XML
    file."""
    xml = ET.parse(xmlPath)
    wigglePair = xml.find('./wigglePairs/wigglePair')
    if wigglePair is None:
        raise ValueError("Provided XML file doesn't have any wiggle data")
    underalignmentStr = parseToWigString(wigglePair.find('absentMaf1ToMaf2').text,
                                         wigglePair.get('reference'),
                                         wigglePair.get('binLength'))
    overalignmentStr = parseToWigString(wigglePair.find('absentMaf2ToMaf1').text,
                                        wigglePair.get('reference'),
                                        wigglePair.get('binLength'))
    with open(underalignmentWig, 'w') as underalignmentF:
        underalignmentF.write(underalignmentStr)
    with open(overalignmentWig, 'w') as overalignmentF:
        overalignmentF.write(overalignmentStr)

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('mafComparatorXML')
    parser.add_argument('underalignmentWig',
                        help='Wiggle that will show where an alignment has been missed')
    parser.add_argument('overalignmentWig',
                        help='Wiggle that will show where an incorrect alignment has been made')
    args = parser.parse_args()
    getWigsFromXML(args.mafComparatorXML, args.underalignmentWig, args.overalignmentWig)

if __name__ == '__main__':
    main()
