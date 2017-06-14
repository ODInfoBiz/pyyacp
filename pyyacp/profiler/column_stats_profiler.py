#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import operator
from collections import defaultdict

import numpy as np

from pyyacp.profiler import ColumnProfiler, ColumnByCellProfiler
from pyyacp.timer import Timer, timer

__author__ = 'nina'

class ColumnStatsProfiler(ColumnProfiler,ColumnByCellProfiler):

    def __init__(self):
        super(ColumnStatsProfiler, self).__init__('csp', 'stats')
        self.vlen = []
        self.dv = defaultdict(int)

    @timer(key='csp_column')
    def profile_column(self, column, meta):
        return self._profile_column(column, meta)

    @timer(key='csp_result')
    def result(self):
        return self._compile_stats()

    def accept(self, cell):
        self.vlen.append(len(cell.strip()))
        self.dv[cell.strip()] += 1


    def _profile_column(self, values, meta):
        for v in values:
            self.vlen.append(len(v.strip()))
            self.dv[v.strip()]+=1
        return self._compile_stats()

    def _compile_stats(self):
        stats = {'num_rows': len(self.vlen)}

        a=np.array(self.vlen)
        an=a[a>0]

        if len(a[a==0])>0:
            self.dv.pop('')
        stats['min_value'] = min(self.dv) if len(self.dv)>0 else ''
        stats['max_value'] = max(self.dv) if len(self.dv)>0 else ''

        stats['min_len'] = min(an) if len(an)>0 else 0
        stats['max_len'] = max(an) if len(an)>0 else 0
        stats['mean_len'] = np.mean(an)
        stats['empty']= len(a[a==0])
        stats['distinct']=len(self.dv)
        stats['uniqueness']=len(self.dv)/float(len(a))

        sorted_values = sorted(self.dv.items(), key=operator.itemgetter(1), reverse=True)
        top_values = [(sorted_values[i][0], int(sorted_values[i][1])) for i in range(min(5, len(self.dv)))]


        stats['constancy']=max(self.dv.values())/float(len(a)) if len(self.dv)>0 and  len(a)>0 else 0
        stats['top_value'] = top_values[0] if len(top_values)>0 else None
        return stats