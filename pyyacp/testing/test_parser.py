'''
Created on Feb 1, 2016

@author: jumbrich
@author: svakulenko
'''
import logging

import os
from pyyacp.yacp import YACParser


if __name__ == '__main__':
    # show debug log info
    logging.basicConfig(level=logging.DEBUG)
    # relative path to csv file
    # sample_csv = "https:__www.wien.gv.at_finanzen_ogd_hunde-wien.csv"
    sample_csv = "http:__ckan.data.graz.gv.at_dataset_027122b3-0f86-493a-ab77-da6bc424735f_resource_149a60b3-962d-4bff-b546-818a0d66d053_download_bezirkszahlen.csv"
    # get absolute path
    path_to_file = os.path.join(os.getcwd(), sample_csv)
    p = YACParser(filename=path_to_file)
    print p.__dict__['header_line']
