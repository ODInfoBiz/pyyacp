#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import  pyyacp.datatable as datatable
from pyyacp.table_structure_helper import AdvanceStructureDetector

SAMPLES_PATH = "sample_csvs"
from os import listdir
from os.path import isfile, join
onlyfiles = [join(SAMPLES_PATH, f) for f in listdir(SAMPLES_PATH) if isfile(join(SAMPLES_PATH, f))]



for csv_file in onlyfiles:
    if 'multi_head_milti_table.csv' not in csv_file:
        continue

    from pyyacp import YACParser

    yacp = YACParser(filename=csv_file,structure_detector = AdvanceStructureDetector(),sample_size=1800)
    print yacp


    tables=datatable.parseDataTables(yacp, url='http://example.org/test', max_tables=10)

    for table in tables:
        print table.data.shape
        print table.data.head(5)


        print 'Comments', table.comments
        print 'Headers', table.header_rows
