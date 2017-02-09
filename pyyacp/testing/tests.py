'''
Created on Feb 1, 2016

@author: jumbrich
@author: svakulenko
'''
import os
import logging

from pyyacp.yacp import YACParser
from pyyacp.profiler import profile

SAMPLES_PATH = "sample_csvs/"
SAMPLE_CSVS = ["bevoelkerung.csv", "bezirkszahlen.csv", "hunde_wien.csv", "hunde_wien2.csv"]


def test_parser(path_to_file=SAMPLES_PATH+SAMPLE_CSVS[3]):
    # show debug log info
    logging.basicConfig(level=logging.DEBUG)
    p = YACParser(filename=path_to_file)
    assert p


def test_profiler(path_to_file=SAMPLES_PATH+SAMPLE_CSVS[3], show_counter=False):
    # show debug log info
    logging.basicConfig(level=logging.DEBUG)
    p = YACParser(filename=path_to_file, skip_guess_encoding=False)
    table_info = profile(p)
    assert table_info
   

def run_profiler(path_to_file=SAMPLES_PATH+SAMPLE_CSVS[3], show_counter=False):
    p = YACParser(filename=path_to_file, skip_guess_encoding=False)
    print 'Header:', p.__dict__['header_line']
    try:
        table_info = profile(p)
        assert table_info
        # show unique values for each of the columns
        for column in table_info['column_unique']:
            print '\n', column
        if show_counter:
            for column in table_info['column_counter']:
                print '\n', column.most_common(30)
    except Exception as e:
        print "Could not process:", path_to_file, e


def collect_columns(path_to_file):
    p = YACParser(filename=path_to_file, skip_guess_encoding=False)
    try:
        table_info = profile(p)
        assert table_info
        return table_info['column_unique']
    except Exception as e:
        print "Could not process:", path_to_file, e


def compare_columns(files=SAMPLE_CSVS, path=SAMPLES_PATH):
    tables = []
    print "Input files:", len(files)
    for sample in files:
        file_path = path + sample
        # test_parser(file_path)
        table_columns = collect_columns(file_path)
        if table_columns:
            tables.append(table_columns)
    # print tables
    print "Tables processed:", len(tables)
    print "Number of columns in each table:"
    print [len(columns) for columns in tables]


if __name__ == '__main__':
    compare_columns()