#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import traceback

import sys

from pyyacp.html.to_html import to_html
import  pyyacp.datatable as datatable
from pyyacp.profiler import  ColumnPatternProfiler, ColumnRegexProfiler, ColumnByCellProfilerSet, \
    ColumnProfiler, ColumnProfilerSet
from profiler.profiling import apply_profilers

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




def from_csv_iter(portalID='data_wu_ac_at'):
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

            to_html(table, cnt, dir='.')

        except Exception as e:
            print(traceback.format_exc())
            print(sys.exc_info()[0])
            print e
        print 'next'
        if cnt>10:
            break


def from_csv_catalog(catalog_base):
    from csvcatalog import CSVCatalog
    c = CSVCatalog(catalog_base)

    profilers = [ColumnPatternProfiler(), DataTypeDetection(),
                 ColumnStatsProfiler()]  # FDProfiler(), ,ColumnStatsProfiler(), DataTypeDetection()]#,XSDTypeDetection()] #,ColumnRegexProfiler()]#,XSDTypeDetection()],,ColumnStatsProfiler()

    cnt=0
    for uri_info in c.get_uris():
        print uri_info
        csv_file=uri_info['disk_location']
        if uri_info['exception'] is None:
            print "none"
        uri=uri_info['uri']
        cnt += 1
        print "{}, {} -> {}".format(cnt, uri, csv_file)
        try:
            from pyyacp import YACParser

            yacp = YACParser(filename=csv_file, sample_size=1800, structure_detector=AdvanceStructureDetector())
            table = datatable.parseDataTables(yacp, url=uri)

            profilers = [ColumnByCellProfilerSet(
                [ColumnPatternProfiler, ColumnStatsProfiler, CharacterDistributionProfiler, BenfordsLawDistribution]),
                         ColumnProfilerSet([DataTypeDetection, DataTypeInterpretation])]
            apply_profilers(table, profilers=profilers)

            to_html(table, cnt, dir='.')

        except Exception as e:
            print(traceback.format_exc())
            print(sys.exc_info()[0])
            print e
        print 'next'

if __name__ == '__main__':
    from_csv_catalog('/Users/jumbrich/Data/csv_catalog')
