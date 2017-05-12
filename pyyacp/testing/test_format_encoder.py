# -*- coding: utf-8 -*-
import codecs
import unittest
import string
import sys

from pyyacp.column_format_detector import translate


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


test_cases=[ (c,'1') for c in string.digits]
test_cases.extend([ (c,'a') for c in string.ascii_lowercase])
test_cases.extend([ (c,'A') for c in string.ascii_uppercase])

encoding=[('ä','a'),('ö','a'),('ü','a'),
          ('Ä', 'A'), ('Ö', 'A'), ('Ü', 'A')]

special=[('?','?')]

mix=[('Wien 1110', 'Aaaa 1111')]

class TestFormatEncoder(unittest.TestCase):

    @for_examples(test_cases)
    def test_basic(self, x, y):
        self.assertEqual(translate(x), y)

    @for_examples(encoding)
    def test_encoding(self, x, y):
        self.assertEqual(translate(x), y)

    @for_examples(special)
    def test_special(self, x, y):
        self.assertEqual(translate(x), y)

    @for_examples(mix)
    def test_mix(self, x, y):
        self.assertEqual(translate(x), y)


if __name__ == '__main__':
    unittest.main()