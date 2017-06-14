#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import traceback

import sys

import  pyyacp.datatable as datatable
from pyyacp.profiler import  ColumnPatternProfiler, ColumnRegexProfiler
from pyyacp.profiler import profiler_engine
from pyyacp.profiler.column_stats_profiler import ColumnStatsProfiler
from pyyacp.profiler.data_type_detection import DataTypeDetection
from pyyacp.profiler.fdprofiler import FDProfiler
from pyyacp.profiler.xsd11_type_detection import XSDTypeDetection
from pyyacp.relateness import relateness
from pyyacp.table_structure_helper import AdvanceStructureDetector
from pyyacp.testing.csv_iterator import csvContent_iter
from utils.timing import Timer

portalID='data_wu_ac_at'


profilers=[FDProfiler(), ColumnPatternProfiler(),ColumnStatsProfiler(), DataTypeDetection()]#,XSDTypeDetection()] #,ColumnRegexProfiler()]#,XSDTypeDetection()],,ColumnStatsProfiler()
cnt=0
t=[]
for uri, csv_file in csvContent_iter(portalID):
    cnt+=1
    print "{}, {} -> {}".format(cnt,uri, csv_file)
    try:
        from pyyacp import YACParser

        yacp = YACParser(filename=csv_file,sample_size=1800, structure_detector = AdvanceStructureDetector())
        table=datatable.parseDataTables(yacp, url=uri)
        table.apply_profiler(profilers=profilers)

        print ">>>>>TABLE{}".format(cnt)


        print('_' * 80)
        print 'Headers',table.header_rows
        print '_' * 30,'DATA {}'.format(table.data.shape),'_'*30
        print '_' * 30, 'META', '_' * 30
        for k in table.meta:
            print '[{}] {} '.format(k, table.meta[k])
        print table.colum_profiles()

        t.append(table)
    except Exception as e:
        print(traceback.format_exc())
        print(sys.exc_info()[0])
        print e
    if cnt>10:
        break

cnt=0
with Timer(key="relatness", verbose=True):
    for i, t1 in enumerate(t):
        for t2 in t[i+1:]:
            res= relateness(t1,t2)
            cnt+=1
            if len(res)!=0:
                print 'T1 Headers', t1.header_rows
                print 'T2 Headers', t2.header_rows
                print res
print cnt
