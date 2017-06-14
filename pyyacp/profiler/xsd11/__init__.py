#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#http://www.w3.org/TR/2009/WD-xmlschema11-2-20091203/type-hierarchy-200901.longdesc.html
#https://www.w3.org/TR/xmlschema11-2/#built-in-datatypes


class Type(object):


    def detectType(self, value):
        raise NotImplementedError('Must provide implementation in subclass.')

    def type(self):
        return self.__class__.__name__

    def _isType(self, value):
        raise NotImplementedError('Must provide implementation in subclass.')

    def convert(self, value):
        return value

class SingleSubType(Type):

    def __init__(self, subType=None):
        self._subType = subType

    def detectType(self, value):
        results=[]
        if self._isType(value):
            results.append(self.type())
            value= self.convert(value)
            if self._subType is not None:
                res=self._subType.detectType(value)
                if res:
                    #print ("RES",res)
                    if isinstance(res,list):
                        results+=res
                    else:
                        results.append(res)

            return results
        else:
            return None


class MultiSubType(Type):

    def __init__(self, subTypes=None):
        self._subTypes = subTypes

    def detectType(self, value):
        results=[]
        if self._isType(value):
            results.append(self.type())
            value= self.convert(value)
            if self._subTypes is not None:
                for subtype in self._subTypes:
                    res = subtype.detectType(value)
                    if res:
                        if isinstance(res, list):
                            results += res
                        else:
                            results.append(res)

            return results
        else:
            return None





