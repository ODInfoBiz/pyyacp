'''
Created on Feb 1, 2016

@author: jumbrich
'''
from pyyacp.yacp import YACParser

if __name__ == '__main__':
    
    
    file = "/Users/jumbrich/Downloads/BAUSTELLENPKTOGD.csv"
    p = YACParser(filename=file)
    print p.__dict__['header_line']