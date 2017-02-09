#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from pyyacp.datatable import parseDataTables

SAMPLES_PATH = "sample_csvs/"
SAMPLE_CSVS = ["bevoelkerung.csv", "bezirkszahlen.csv", "hunde_wien.csv", "hunde_wien2.csv"]




path_to_file=SAMPLES_PATH+SAMPLE_CSVS[3]

from pyyacp.yacp import YACParser
yacp = YACParser(filename=path_to_file,sample_size=1800)
print yacp


tables=parseDataTables(yacp, url="http://test")

for t in tables:
    print t.comments
    print t.header_rows
    print t.data.describe()
    print t.data['col7'].describe(), type(t.data['col7'].describe())
    print t.rowIter()