# -*- coding: utf-8 -*-
from __future__ import absolute_import

import unittest
import sys
from random import randint, shuffle
from pyyacp.column_format_detector import  aggregate,  aggregate_group_of_same_symbols
from pyyacp.testing.value_pattern_types_list import random_number, random_date, random_time, random_iso8601, \
    random_lowercase_string, random_word, random_words


def for_examples(parameters):

  def tuplify(x):
    if not isinstance(x, tuple):
      return (x,)
    return x

  def decorator(method, parameters=parameters):
    for parameter in (tuplify(x) for x in parameters):

      def method_for_parameter(self, method=method, parameter=parameter):
        method(self, *parameter)
      args_for_parameter = ",".join(repr(v) for v in parameter)
      name_for_parameter = method.__name__ + "(" + args_for_parameter + ")"
      frame = sys._getframe(1)  # pylint: disable-msg=W0212
      frame.f_locals[name_for_parameter] = method_for_parameter
    return None
  return decorator

##basic straight forward aggregation
test_cols_aggregated=[
    (random_number(10,digits=1, fix_len=True), '1'),
    (random_number(10,digits=2, fix_len=True), '11'),
    (random_number(10,digits=3, fix_len=True), '111'),
    (random_number(10,digits=5, fix_len=True), '11111'),
    ( random_number(2,digits=1, fix_len=True)+random_number(2,digits=2, fix_len=True), '01'),
    (random_date(5), '1111-11-11'),
    (random_time(5), '11:11:11'),
    (random_iso8601(5), '1111-11-11C11:11:11'),
    (random_lowercase_string(10, length=5),'ccccc'),
    (random_lowercase_string(5, length=5)+random_lowercase_string(5, length=3),'aaccc'),
    (random_word(10,length=5),'Ccccc'),
    (random_word(5,length=5)+random_word(5,length=3),'Caacc'),
    (random_words(10,length=[5,3]),'Ccccc Ccc'),
    (random_words(5,length=[5,3])+random_words(5,length=[3,5]),'Caacc Caacc'),

]

#This cases are not that straight forward
test_cols_aggregated_complex=[
    ( [u'-1']+random_number(5,digits=1, fix_len=True), '[-]1'), # sometimes numbers contain a minus
    ( [u'-1',u'+1']+random_number(5,digits=1, fix_len=True), '[+/-]1')
]


class TestFormatEncoder(unittest.TestCase):
    def setUp(self):
        self.f = aggregate

    @for_examples(test_cols_aggregated)
    def test_basic(self, x, y):
        res=self.f(values=x)
        self.assertEqual(res[0][0], y)
        self.assertEqual(res[0][1], len(x))

    @for_examples(test_cols_aggregated_complex)
    def test_complex(self, x, y):
        res = self.f(values=x)
        self.assertEqual(res[0][0], y)
        self.assertEqual(res[0][1], len(x))

if __name__ == '__main__':
    unittest.main()