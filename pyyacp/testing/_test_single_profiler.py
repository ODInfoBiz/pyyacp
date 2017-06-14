#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import traceback

import sys

import  pyyacp.datatable as datatable
#from html.to_html import to_html
from pyyacp.profiler import  ColumnPatternProfiler, ColumnRegexProfiler, ColumnByCellProfilerSet, \
    ColumnProfiler, ColumnProfilerSet
from profiler.profiling import apply_profilers

from pyyacp.profiler.column_stats_profiler import ColumnStatsProfiler
from pyyacp.profiler.data_type_detection import DataTypeDetection
from pyyacp.profiler.data_type_interpretation import DataTypeInterpretation
from pyyacp.profiler.distributions import CharacterDistributionProfiler, BenfordsLawDistribution

from pyyacp.table_structure_helper import AdvanceStructureDetector
from pyyacp.testing.csv_iterator import csvContent_iter

from pyyacp import YACParser
#filename=csv_file
url='http://nsandi-corporate.com/wp-content/uploads/2015/02/transparency-25k-08-2013.csv'
url='http://www.win2day.at/download/lo_1992.csv'
url='http://data.wu.ac.at/data/unibib/diff/JREK/2015-07-07.csv'
url='http://www.win2day.at/download/etw_2006.csv'
url='http://www.win2day.at/download/jo_2004.csv'
url='http://www.win2day.at/download/jo_1992.csv'
#url='http://data.wu.ac.at/portal/dataset/fdb16224-5f6c-482b-932f-e5fe12f52991/resource/a545bb37-0563-4312-be3f-b36a793c0764/download/allcoursesandorgid14s.csv'

yacp = YACParser(url=url,sample_size=1800, structure_detector = AdvanceStructureDetector())
table = datatable.parseDataTables(yacp, url=url)

apply_profilers(table)

#to_html(table, dir='./html')

table.print_summary(column_raw=True)
print '_' * 30, 'TABLE META', '_' * 30
for k,v in table.table_profile().items():
    print (k,v)
print '_' * 30, 'TABLE STRUCTURE', '_' * 30
for k,v in table.table_structure().items():
    print (k,v)
print '_' * 30, 'DATA {}'.format(table.data.shape), '_' * 30
print table.data.head(5)
print '_' * 30, 'COLUMN PROFILE', '_' * 30
print table.colum_profiles()


for i,c in enumerate(table.columns()):
    print 'COL',i,set(c)
print('*' * 80)

