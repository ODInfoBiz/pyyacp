# -*- coding: utf-8 -*-
import codecs
import unittest

from pyyacp.table_structure_helper import AdvanceStructureDetector, SimpleStructureDetector
from pyyacp import YACParser


class TestDescriptionDetectionAdvanceStructureDetector(unittest.TestCase):

    #structure_detector = AdvanceStructureDetector()

    def setUp(self):
        self.structure_detector = AdvanceStructureDetector()




    def test_no_comment(self):
        table=u"""h1,h2,h3
                  c1,c2,c3"""
        yacp = YACParser(content=table, sample_size=1800,structure_detector=self.structure_detector)
        self.assertEquals(0,len(yacp.descriptionLines))


    def test_empty_comment(self):
        table=u"""
                  h1,h2,h3
                  c1,c2,c3"""
        yacp = YACParser(content=table, sample_size=1800,structure_detector=self.structure_detector)
        self.assertEquals(1,len(yacp.descriptionLines))


    def test_one_comment(self):
        table=u"""t
                  h1,h2,h3
                  c1,c2,c3
                  c21,c22,c23
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3"""
        yacp = YACParser(content=table, sample_size=1800,structure_detector=self.structure_detector)
        self.assertEquals(1,len(yacp.descriptionLines))

    def test_one_comment1(self):
        table=u"""t,
                  h1,h2,h3
                  c1,c2,c3
                  c21,c22,c23
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3"""
        yacp = YACParser(content=table, sample_size=1800,structure_detector=self.structure_detector)
        self.assertEquals(1,len(yacp.descriptionLines))

    def test_one_comment1(self):
        table=u"""t,,
                  h1,h2,h3
                  c1,c2,c3
                  c21,c22,c23
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3"""
        yacp = YACParser(content=table, sample_size=1800,structure_detector=self.structure_detector)
        self.assertEquals(1,len(yacp.descriptionLines))

    def test_mix_comment1(self):
        table=u"""
                  t,,

                  h1,h2,h3
                  c1,c2,c3
                  c21,c22,c23
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3
                  c1,c2,c3"""
        yacp = YACParser(content=table, sample_size=1800,structure_detector=self.structure_detector)
        self.assertEquals(3,len(yacp.descriptionLines))

class TestDescriptionDetectionSimpleStructureDetector(TestDescriptionDetectionAdvanceStructureDetector):
    def setUp(self):
        self.structure_detector = SimpleStructureDetector()

if __name__ == '__main__':
    unittest.main()