#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import traceback

import sys

import  pyyacp.datatable as datatable
from pyyacp.profiler import  ColumnPatternProfiler, ColumnRegexProfiler, apply_profilers, ColumnByCellProfilerSet, \
    ColumnProfiler, ColumnProfilerSet

from pyyacp.profiler.column_stats_profiler import ColumnStatsProfiler
from pyyacp.profiler.data_type_detection import DataTypeDetection
from pyyacp.profiler.data_type_interpretation import DataTypeInterpretation
from pyyacp.profiler.distributions import CharacterDistributionProfiler, BenfordsLawDistribution
from pyyacp.profiler.fdprofiler import FDProfiler
from pyyacp.profiler.xsd11_type_detection import XSDTypeDetection
from pyyacp.table_structure_helper import AdvanceStructureDetector
from pyyacp.testing.csv_iterator import csvContent_iter

SAMPLES_PATH = "./sample_csvs"
from os import listdir
from os.path import isfile, join
onlyfiles = [join(SAMPLES_PATH, f) for f in listdir(SAMPLES_PATH) if isfile(join(SAMPLES_PATH, f))]

portalID='data_wu_ac_at'


profilers=[ColumnPatternProfiler(),DataTypeDetection(), ColumnStatsProfiler()]#FDProfiler(), ,ColumnStatsProfiler(), DataTypeDetection()]#,XSDTypeDetection()] #,ColumnRegexProfiler()]#,XSDTypeDetection()],,ColumnStatsProfiler()
cnt=0
for uri, csv_file in csvContent_iter(portalID):
    cnt+=1
    print "{}, {} -> {}".format(cnt,uri, csv_file)
    try:
        from pyyacp import YACParser

        yacp = YACParser(filename=csv_file,sample_size=1800, structure_detector = AdvanceStructureDetector())
        table=datatable.parseDataTables(yacp, url=uri)


        profilers=[ColumnByCellProfilerSet([ColumnPatternProfiler, ColumnStatsProfiler, CharacterDistributionProfiler, BenfordsLawDistribution]) , ColumnProfilerSet([DataTypeDetection,DataTypeInterpretation])]
        apply_profilers(table,profilers=profilers)

        to_html(table, dir='./html')

        #profilers = [ ColumnProfilerSet([ColumnPatternProfiler,ColumnStatsProfiler,DataTypeDetection])]
        #apply_profilers(table, profilers=profilers)

        print table.column_metadata
        print table.describe_colmeta()
        print table.describe_colmeta().info()

        for i,c in enumerate(table.columns()):
            print 'COL',i,set(c)
        print('*' * 80)


        #profiler_engine.profile(table,profilers=profilers)
        print('_' * 80)
        print 'Comments',table.comments
        print 'Headers',table.header_rows
        print '_' * 30,'DATA {}'.format(table.data.shape),'_'*30
        print table.data.head(5)
        print '_' * 30, 'META', '_' * 30
        for k in table.meta:
            print '[{}] {} '.format(k, table.meta[k])

        print table.describe_colmeta()


    except Exception as e:
        print(traceback.format_exc())
        print(sys.exc_info()[0])
        print e
    print 'next'
    if cnt>20:
        break



