#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
__author__ = 'nina'

import re
import dateutil.parser


def detectType(value):

    num = '^([0-9]*)$'
    numplus = '^([0-9!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c]*)$'
    plus = '^([!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c]*)$'
    alphanum = '^([^!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c]*)$'
    alpha = '^([^0-9!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c]*)$'
    alphaplus = '^([^0-9]*)$'
    float =  '^([0-9]*[.,][0-9]*)$'


    if len(value) == 0:
        return "EMPTY"
    elif re.match(float, value):
        return "FLOAT"
    elif re.match(plus, value):
        return "+"
    elif re.search(num, value):
        return "NUM"
    elif re.search(numplus, value):
        try:
            dateutil.parser.parse(value)
            return "TEMP"
        except:
            return "NUM+"
    elif re.search(alpha, value):
        return "ALPHA"
    elif re.search(alphaplus, value):
        return "ALPHA+"
    elif re.search(alphanum, value):
        return "ALPHANUM"
    else:
        try:
            dateutil.parser.parse(value)
            return "TEMP"
        except:
            return "ALPHANUM+"
