from pyyacp.profiler import ColumnProfiler
from pyyacp.profiler.data_type_detection import DATETIME, INT, UNICODE

import re
SENT=re.compile('^(C[c])+( [Cc]+)*[\.!?]?$')
ENT=re.compile('^(C[c])+( [Cc]+){2,3}$')

class DataTypeInterpretation(ColumnProfiler):

    def __init__(self):
        super(DataTypeInterpretation, self).__init__('dclass','data_class')
        self.values=[]

    def profile_column(self, column, meta):
        data_class = 'UNDEF'
        if 'patterns' in meta and 'stats_max_len' in meta:
            return  self._analyse_ColumnPattern(column,meta)

        return data_class

    def _analyse_ColumnPattern(self, column,meta):
        patterns= meta['patterns']
        data_type=meta['data_type']
        #print meta
        min, mean, max = meta['stats_max_len'], meta['stats_mean_len'], meta['stats_min_len']
        fixed_len = min==max
        unique= meta['stats_distinct'] + meta['stats_empty'] == meta['stats_num_rows']

        if data_type==DATETIME:
            return data_type.upper()

        if meta['stats_empty'] == meta['stats_num_rows']:
            return "EMPTY"

        s=''
        if data_type == INT:
            s+='NUM'
        elif data_type == UNICODE:
            if len(patterns)==1:
                if SENT.match(patterns[0][0]):
                    s+='SENTENCE'
                elif ENT.match(patterns[0][0]):
                    s += 'ENTITY'
                else:
                    s += 'UNI'
            else:
                s += 'UNI'
        else:
            s = 'UNDEF'

        if fixed_len:
            s+='_ID'
        else:
            s+='_VAR'

        if unique:
            s+='_UNIQ'

        if meta['stats_distinct'] == 1:
            s+="_SING"
        elif (meta['stats_num_rows'] > 10 and (meta['stats_distinct']/float(meta['stats_num_rows']))<0.1) \
                or (meta['stats_num_rows'] < 10 and meta['stats_distinct']<=2):
            s+='_CAT'
        return s
