#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from collections import defaultdict

from pyyacp.profiler import Profiler
from pyyacp.profiler.xsd11.types import anySimpleType
from pyyacp.timer import Timer


class XSDTypeDetection(Profiler):

    def __init__(self):
        super(XSDTypeDetection, self).__init__('xsd','col_xsd')
        self.a = anySimpleType()


    def parseTypes(self, type, d, i=0):
        d1 = d.setdefault(type.type(), {'c': 0})
        #print "{}{} {}".format(' '*i,i,type.type())
        if hasattr(type,'_subTypes'):
            d1['st']={}
            st=type._subTypes
            for s in st:
                self.parseTypes(s, d1['st'],i=i+2)

        if hasattr(type, '_subType'):
            st = type._subType
            if st is not None:
                d1['st'] = {}
                self.parseTypes(st, d1['st'], i=i + 2)

    def _profile(self, table):
        for i, col in enumerate(table.columns()):
            patterns = self._analyse_Column(col)
            table.column_metadata[i][self.key] = patterns

    def _analyse_Column(self,col):
        c = {}
        self.parseTypes(self.a, c)

        counts = defaultdict(int)
        for value in col:
            xsdtype = self.a.detectType(value)
            #self.update_Counts(xsdtype, counts)
            for d in xsdtype:
                counts[d] += 1

        def update(c,counts):
            for k,v in c.items():
                if k in counts:
                    v['c']=counts[k]
                    if 'st' in v:
                        update(v['st'], counts)
        update(c,counts)
        def cleanup(c):
            for k,v in c.items():
                #print k,v
                if v['c']==0:
                #    print "del",k
                    del c[k]
                elif 'st' in v:
                    cleanup(v['st'])
                    if len(v['st'])==0:
                        del v['st']
        cleanup(c)
        return c


    def update_Counts(self, types, counts):
        if isinstance(types, dict):
            for k,v in types.items():
                if v is True:
                    counts=counts.setdefault(k,{'c':0})
                    counts['c'] += 1
                if isinstance(v,dict):
                    counts = counts.setdefault(k, {'c': 0, 'v': {}})
                    counts['c']+=1
                    self.update_Counts(v, counts['v'])
        if isinstance(types,list):
            for k in types:
                if isinstance(k,dict):
                    self.update_Counts(k, counts)
                else:
                    counts = counts.setdefault(k, {'c': 0})
                    counts['c'] += 1



if __name__ == '__main__':
    a = anySimpleType()
    c=XSDTypeDetection()
    import pprint
    pprint.pprint(c._analyse_Column(["5723","5723",'12312312312312']))
