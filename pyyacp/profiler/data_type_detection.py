from pyyacp.profiler import  ColumnProfiler


INT='int'
FLOAT='float'
DATETIME='datetime'
DATE='date'
TIME='time'
UNICODE='unicode'

import re
types=[
    (FLOAT,re.compile('^\[?[+/-]*\]?\d+\.\d*$')),
    (INT,re.compile('^\[?[+/-]*\]?\d+$')),
    (DATETIME, re.compile('^\d{4}-\d{2}-\d{2}([C ]+\d{2}:\d{2}:\d{2})$')),
    (DATE, re.compile('^\d{4}-\d{2}-\d{2}$')), #1111-11-11
    (TIME, re.compile('^\d{2}:\d{2}(:\d{2})?$')) #1111-11-11
]

class DataTypeDetection(ColumnProfiler):

    def __init__(self):
        super(DataTypeDetection, self).__init__('dtype','data_type')
        self.values=[]

    def profile_column(self, column, meta):
        data_type = UNICODE
        if 'patterns' in meta:
            data_type = self._analyse_ColumnPattern(meta)

        return data_type

    def _analyse_ColumnPattern(self, meta):
        pattern=meta['patterns']
        gtypes = set([])
        for p in pattern:
            for ptype in types:
                m=ptype[1].match(p[0])
                if m:
                    gtypes.add(ptype[0])
        if len(gtypes) != 1:
            return UNICODE
        d= gtypes.pop()
        if d == INT or d==FLOAT:
            #print meta['stats_min_value']
            if meta['stats_min_value'][0]==u'0':
                #print "LEADING ZERO"
                return UNICODE
        return d