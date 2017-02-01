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
SAMPLE_CSVS = ["bevoelkerung.csv", "bezirkszahlen.csv", "hunde_wien.csv"]


def test_parser(path_to_file):
    p = YACParser(filename=path_to_file)
    assert p
    print(p.__dict__['header_line'])


def test_profiler(path_to_file):
    p = YACParser(filename=path_to_file, skip_guess_encoding=False)
    # print(profile(p))
    table_info = profile(p)
    assert table_info
    # for column in table_info['column_unique']:
    #     print '\n', column
    for column in table_info['column_counter']:
        print '\n', column.most_common(30)


if __name__ == '__main__':
    # show debug log info
    # logging.basicConfig(level=logging.DEBUG)
    file_path = SAMPLES_PATH + SAMPLE_CSVS[2]
    # test_parser(file_path)
    test_profiler(file_path)

