# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest

from pyyacp.table_structure_helper import AdvanceStructureDetector, SimpleStructureDetector

class TestDescriptionDetectionAdvanceStructureDetector(unittest.TestCase):

    def setUp(self):
        self.structure_detector = AdvanceStructureDetector()
        self.verbose=True


    def test_single_col_no_header(self):
        table=[ ['City'],
                ['Vienna'],
                ['Salzburg']
            ]
        self.assertListEqual([], self.structure_detector.guess_headers(table, verbose=self.verbose))

    def test_single_col_one_header(self):
        table=[ ['Name'],
                ['Tim Tom'],
                ['Max Min']
            ]
        self.assertListEqual([table[0]], self.structure_detector.guess_headers(table, verbose=self.verbose))

    def test_single_col_one_header1(self):
        table=[ ['Vor Nachname'],
                ['Tim Tom'],
                ['Max Min']
            ]
        self.assertListEqual([], self.structure_detector.guess_headers(table, verbose=self.verbose))

    def test_single_col_one_header2(self):
        table=[ ['Count'],
                ['10'],
                ['111']
            ]
        self.assertListEqual([table[0]], self.structure_detector.guess_headers(table, verbose=self.verbose))

    def test_multi_header(self):
        table=[ ['Einwohner'],
                ['Population'],
                ['1799'],
            ]
        self.assertListEqual(table[0:2], self.structure_detector.guess_headers(table, verbose=self.verbose))

    def test_col1_h1_mixed(self):
        table=[ ['Population','City','Country'],
                ['1799', 'Vienna', 'Austria'],
                ['1799', 'Salzburg', 'Austria'],
            ]
        self.assertListEqual(table[0:1], self.structure_detector.guess_headers(table, verbose=self.verbose))





class TestDescriptionDetectionSimpleStructureDetector(TestDescriptionDetectionAdvanceStructureDetector):
    def setUp(self):
        self.structure_detector = SimpleStructureDetector()
        self.verbose = True


if __name__ == '__main__':
    unittest.main()