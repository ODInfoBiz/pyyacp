# -*- coding: utf-8 -*-
import codecs
import unittest

from pyyacp import YACParser


def generate_csv(encoding):
    print "e",encoding
    data=u'ä,ö,ê\na,b,c'

    if encoding!='utf8':
        data=data.encode(encoding, errors='replace')
    print data
    return data


class TestEncodingDetection(unittest.TestCase):

    def test_utf8(self):
        encoding='utf8'
        yacp = YACParser(content=generate_csv(encoding), sample_size=1800)
        self.assertEquals(encoding,yacp.meta['encoding'])

    def test_ascii(self):
        encoding='us-ascii'
        yacp = YACParser(content=generate_csv(encoding), sample_size=1800)
        self.assertEquals(encoding, yacp.meta['encoding'])

    def test_latin(self):
        encoding='iso-8859-1'
        yacp = YACParser(content=generate_csv(encoding), sample_size=1800)
        self.assertEquals(encoding, yacp.meta['encoding'])

if __name__ == '__main__':
    unittest.main()