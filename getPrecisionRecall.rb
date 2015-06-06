#!/usr/bin/env ruby
require 'nokogiri'
require 'pathname'

PROGRESSIVE_CACTUS_DEVEL_DIR = Pathname.new("/home/joel/progressiveCactus-fresh")
PROGRESSIVE_CACTUS_PHYLO_DIR = Pathname.new("/home/joel/progressiveCactus-phylogeny")

dir = Pathname.new(ARGV[0])
raise "Path #{dir.realpath} is not a directory" unless dir.exist? && dir.directory?

# get config diff.
configXmlPath = dir + "../config.xml"
configXml = Nokogiri::XML(configXmlPath.open)
isPhylogenyBasedXml = configXml.at_xpath("*/caf").has_attribute?("phylogenyNumTrees")
baseConfig = (isPhylogenyBasedXml ? PROGRESSIVE_CACTUS_PHYLO_DIR : PROGRESSIVE_CACTUS_DEVEL_DIR) + "submodules/cactus/cactus_progressive_config.xml"
system("diff -w #{baseConfig.realpath} #{configXmlPath}")

# get precision and recall
comparatorXmlPath = dir + "mafComparator.xml"
comparatorXml = Nokogiri::XML(comparatorXmlPath.open)
aggregateResultNodes = comparatorXml.xpath('//alignmentComparisons/homologyTests/aggregateResults/all')
puts "Precision: #{aggregateResultNodes[0]["average"]}"
puts "Recall: #{aggregateResultNodes[1]["average"]}"
