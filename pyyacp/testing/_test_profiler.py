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

SAMPLES_PATH = "./sample_csvs"
from os import listdir
from os.path import isfile, join
onlyfiles = [join(SAMPLES_PATH, f) for f in listdir(SAMPLES_PATH) if isfile(join(SAMPLES_PATH, f))]

portalID='data_wu_ac_at'
import structlog
log = structlog.get_logger()
import anycsv
cnt=0
for uri, csv_file in csvContent_iter(portalID):
    cnt+=1
    if cnt<=2:
        continue
    log.info("{}, {} -> {}".format(cnt,uri, csv_file))
    try:
        from pyyacp import YACParser
        #filename=csv_file
        url=uri

        yacp = YACParser(filename=csv_file,sample_size=1800, structure_detector = AdvanceStructureDetector())
        table = datatable.parseDataTables(yacp, url=uri)

        apply_profilers(table)

        #to_html(table, dir='./html')

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


    except Exception as e:
        print(traceback.format_exc())
        print(sys.exc_info()[0])
        print e
    print 'next'
    if cnt>2:
        break



