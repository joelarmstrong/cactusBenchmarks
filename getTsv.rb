#!/usr/bin/env ruby
require 'pathname'
require 'nokogiri'

PROGRESSIVE_CACTUS_DEVEL_DIR = Pathname.new("/home/joel/progressiveCactus-fresh")
PROGRESSIVE_CACTUS_PHYLO_DIR = Pathname.new("/home/joel/progressiveCactus-phylogeny")

rows = {}

Dir.entries(ARGV[0]).each do |filename|
  begin
    path = Pathname.new(filename)
    next unless path.directory?
    branch = /output-([^-]*)/.match(filename)[1]
    configXmlPath = path + "output/config.xml"
    configXml = Nokogiri::XML(configXmlPath.open)
    isPhylogenyBasedXml = configXml.at_xpath("*/caf").has_attribute?("phylogenyNumTrees")
    baseConfig = (isPhylogenyBasedXml ? PROGRESSIVE_CACTUS_PHYLO_DIR : PROGRESSIVE_CACTUS_DEVEL_DIR) + "submodules/cactus/cactus_progressive_config.xml"
    diff = `diff -w #{baseConfig.realpath} #{configXmlPath} | grep -v -- check | grep '>'`.rstrip.gsub("\n", ", ").gsub(/\s+/, " ")
    prOutput = `./getPrecisionRecall.rb #{path}`
    p = /Precision: (.*)/.match(prOutput)[1].to_f
    r = /Recall: (.*)/.match(prOutput)[1].to_f
    rows[diff] ||= Hash.new(["", ""])
    rows[diff][branch] = [p, r]
  rescue
    warn "skipping #{filename} due to errors"
  end
end

branchOrdering = ["development", "phylogeny", "splitBeforeLastMelt", "barRescue", "makeConfidentSplitsFirst"]
puts "Config diff\t" + branchOrdering.map { |b| [b + "Precision", b + "Recall"] }.flatten.join("\t")

rows.each do |k,v|
  puts "#{k}\t" + ["development", "phylogeny", "splitBeforeLastMelt", "barRescue", "makeConfidentSplitsFirst"].map { |branch| "#{v[branch][0]}\t#{v[branch][1]}" }.join("\t")
end
