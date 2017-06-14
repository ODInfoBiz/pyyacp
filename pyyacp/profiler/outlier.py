#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import random
import string
import math
import numpy as np
import timeit
from collections import Counter

from collections import defaultdict

from pyyacp.profiler import ColumnProfiler, ColumnByCellProfiler
from pyyacp.profiler import is_not_empty
from outliers import smirnov_grubbs as grubbs

import structlog
log =structlog.get_logger()


def get_outlier_indices(data):
    num_data = []
    for d in data:
        try:
            num_data.append(float(d))
        except Exception as e:
            pass
    if len(num_data) < len(data):
        log.warn('Could only convert ' + str(len(num_data)) + ' of ' + str(len(data)) + ' values in column')
    return grubbs.min_test_indices(num_data, alpha=0.05)

class OutlierProfiler(ColumnProfiler,ColumnByCellProfiler):

    def __init__(self):
        super(OutlierProfiler, self).__init__('cdp', 'c_dist')
        self.dv = defaultdict(int)

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
        if data_type=='int':
            num_values = map(int, values)
        elif data_type=='float':
            num_values = map(float, values)

    def _compile_stats(self):
        return {'dist':dict(self.dv)}
