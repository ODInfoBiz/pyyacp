#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from __future__ import absolute_import, division, print_function, unicode_literals
import pprint

from faststat.faststat import _sigfigs

__author__ = 'jumbrich'
import collections
import functools
import time
import faststat


class Timer(object):
    GLOBAL_VERBOSE=True
    measures={}

    def __init__(self, verbose=False, key=None, store=True):
        self.verbose = verbose
        self.key=key
        self.store=store

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        end = time.time()
        secs = end - self.start
        msecs = secs * 1000  # millisecs
        if self.verbose and Timer.GLOBAL_VERBOSE:
            print('(%s) elapsed time: %f ms' % (self.key,msecs))
        if self.key and self.store:
            if self.key not in self.__class__.measures:
                self.__class__.measures[self.key]=faststat.Stats()
            if msecs>=0:
                self.__class__.measures[self.key].add(msecs)

    @classmethod
    def printStats(cls):
        print("\n -------------------------")
        print("  Timing stats:" )
        pprint.pprint(cls.getStats())
        print("\n -------------------------")


    @classmethod
    def getStats(cls):
        stats={}
        for m in cls.measures:
            stats[m]={'avg':cls.measures[m].mean, 'calls':cls.measures[m].n, 'min':cls.measures[m].min, 'max':cls.measures[m].max, 'rep':cls.measures[m].__repr__}
        return stats

    @classmethod
    def to_csv(cls, filename=None):
        from cStringIO import StringIO
        import csv
        data = StringIO()
        csvw = csv.writer(data)
        csvw.writerow(['measure, calls', 'min','mean','max','q25','q5','q75'])

        q25, q50, q75=None, None, None
        for m in cls.measures:
            p = cls.measures[m].percentiles
            if cls.measures[m].n >= len(p):
                q25,q50,q75= _sigfigs(p.get(0.25, -1)),_sigfigs(p.get(0.5, -1)), _sigfigs(p.get(0.75, -1))

            csvw.writerow([m, cls.measures[m].n,
                           _sigfigs(cls.measures[m].min), _sigfigs(cls.measures[m].mean), _sigfigs(cls.measures[m].max),
                           q25,q50,q75
                           ])
        if filename:
            with open(filename,'w') as f:
                f.write(data)
        data.seek(0)
        return data.read()


def timer(key=None, verbose=False, *func_or_func_args):
    def wrapped_f(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with Timer(key=key, verbose=verbose) as t:
                out = f(*args, **kwargs)
            return out
        return wrapped
    if (len(func_or_func_args) == 1
            and isinstance(func_or_func_args[0], collections.Callable)):
        return wrapped_f(func_or_func_args[0])
    else:
        return wrapped_f
