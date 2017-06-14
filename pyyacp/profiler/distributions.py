#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import math
import numpy as np

from collections import defaultdict

from pyyacp.profiler import ColumnProfiler, ColumnByCellProfiler
from pyyacp.profiler import is_not_empty
from pyyacp.profiler.data_type_detection import FLOAT, UNICODE
from pyyacp.profiler.data_type_detection import INT
from pyyacp.timer import timer


class CharacterDistributionProfiler(ColumnProfiler,ColumnByCellProfiler):

    def __init__(self):
        super(CharacterDistributionProfiler, self).__init__('cdp', 'c_dist')
        self.dv = defaultdict(int)

    @timer(key='cdp_column')
    def profile_column(self, column, meta):
        return self._profile_column(column, meta)

    def result(self):
        return self._compile_stats()

    def accept(self, cell):
        if is_not_empty(cell):
            for c in cell:
                self.dv[c] += 1

        #self.values.append(cell)

    def _profile_column(self, values, meta):
        data_type = meta['data_type']
        if data_type == UNICODE:
            for v in filter(is_not_empty,values):
                for c in v:
                    self.dv[c] += 1
        return self._compile_stats()

    def _compile_stats(self):
        if len(self.dv)>0:
            return {'dist':dict(self.dv)}
        else:
            return {'dist': None}

def benford_law():
    return [math.log10(1 + 1 / float(i)) * 100.0 for i in xrange(1, 10)]

def get_leading_number(cell):
    numbers = "123456789"
    l = map(int, filter(lambda x: x in numbers, cell))
    return l[0] if len(l)>0 else 0

def chisq_stat(O, E):
    return sum([(o - e) ** 2 / e for (o, e) in zip(O, E)])

def passChi(chi):
	# degrees of freedom always 8 and assuming 95% confidence
	# from: https://en.wikipedia.org/wiki/Chi-squared_distribution
	# 95% conf: 15.51

	# Null hypothesis H_0: The first digits in the index minute price changes follow the Benford's law
	# Hypothesis H_1: The first digits in the index minute price changes do not follow the Benford's law}
	if (chi<15.51):
		return True
	else:
		return False

def getExpectedBenfordCount(size):
	return map(lambda x:x*0.01*size, benford_law())

class BenfordsLawDistribution(ColumnProfiler, ColumnByCellProfiler):

    def __init__(self):
        super(BenfordsLawDistribution, self).__init__('cdb', 'benford')
        self.dv = {i:0 for i in range(1,10)}

    @timer(key='cdb_column')
    def profile_column(self, column, meta):
        return self._profile_column(column, meta)

    def result(self):
        return self._compile_stats()

    def accept(self, cell):
        digit=get_leading_number(cell)
        if digit != 0:
            self.dv[digit] +=1

    def _profile_column(self, values, meta):
        data_type = meta['data_type']
        if data_type == INT or data_type == FLOAT:
            x = map(get_leading_number, values)
            for k in range(1, 10):
                self.dv[k] = x.count(k)
        return self._compile_stats()

    def _compile_stats(self):
        if sum(self.dv.values())>0:
            d = np.array([ self.dv.get(k,0) for k in range(1, 10)])
            y = getExpectedBenfordCount(sum(d))

            chi= chisq_stat(d, y)

            dd={}
            total=sum(d)*1.0
            for k,v in self.dv.items():
                dd[k]=v/(total)

            return {'dist': dd, 'is':passChi(chi), 'chi':chi}
        else:
            return {'dist': None, 'is': False, 'chi': None}

#
#
#
# ### BENCHMARKING
#
# c = None
# def dist_counter(values):
#     global c
#     c=Counter("".join(values))
#     return c
#
# r = defaultdict(int)
# def dist_default(values):
#     global r
#     r = defaultdict(int)
#     for v in values:
#         for c in v:
#             r[c]+=1
#     return r
#
#
# from faker import Factory
# fake = Factory.create()
# inputs=[unicode(fake.name()) for i in range(0,1000)]
# print inputs
# print dist_default(inputs)
# print dist_counter(inputs)
# if __name__ == '__main__':
#
#
#     #print s
#
#     # print "sets      :", timeit.Timer('f(s)', 'from __main__ import s,test_set as f').timeit(1000000)
#     print "translate :", timeit.Timer('f(inputs)', 'from __main__ import inputs,dist_counter as f').timeit(1000)
#     print "translate :", timeit.Timer('f(inputs)', 'from __main__ import inputs,dist_default as f').timeit(1000)
#     #print "translate1   :", timeit.Timer('f(input)', 'from __main__ import input,translate1 as f').timeit(1000000)
#     #print "translate2   :", timeit.Timer('f(input)', 'from __main__ import input,translate2 as f').timeit(1000000)
#     #print "translate4   :", timei t.Timer('f(input)', 'from __main__ import input,translate4 as f').timeit(1000000)
#     print c
#     print r