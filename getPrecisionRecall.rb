#!/usr/bin/env ruby
require 'nokogiri'
require 'pathname'

ARGV.each do |run|
  dir = Pathname.new(run)

  puts "=== #{dir} ==="

  # get precision and recall
  comparatorXmlPath = dir + "mafComparator.xml"
  unless comparatorXmlPath.exist?
    puts "no data"
    next
  end

  comparatorXml = Nokogiri::XML(comparatorXmlPath.open)
  aggregateResultNodes = comparatorXml.xpath('//alignmentComparisons/homologyTests/aggregateResults/all')
  precision = aggregateResultNodes[1]["average"].to_f
  recall = aggregateResultNodes[0]["average"].to_f
  fScore = (2 * precision * recall/(precision + recall)).round(3)
  puts "Precision: #{precision}"
  puts "Recall: #{recall}"
  puts "F-score: #{fScore}"
end
