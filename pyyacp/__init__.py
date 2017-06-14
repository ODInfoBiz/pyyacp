#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO




import unicodecsv

import anycsv
from pyyacp.table_structure_helper import SimpleStructureDetector

import structlog
log = structlog.get_logger()


class YACParserException(Exception):
    pass




class YACParser(object):
    def __init__(self, filename=None, url=None, content=None, sample_size=20, skip_guess_encoding=False, structure_detector=SimpleStructureDetector(), max_file_size=-1):

        self.table = anycsv.reader(filename=filename, url=url, content=content, skip_guess_encoding=skip_guess_encoding, sniff_lines=sample_size,max_file_size=max_file_size)

        keys = ['encoding', 'url', 'filename', 'delimiter', 'quotechar','lineterminator','skipinitialspace','quoting','delimiter','doublequote']
        self.meta = {}
        for k,v in self.table.__dict__.items():
            if k in keys and v:
                self.meta[k] = v
        for k,v in self.table.dialect.items():
            if k in keys:
                self.meta[k] = v
        if 'url' in self.meta:
            self.meta['uri'] = self.meta.pop('url')

        #self.meta['dialect'] = self.table.dialect
        log.debug("Input file dialect", dialect=self.table.dialect, encoding=self.meta['encoding'])
        self.sample = []
        for i, row in enumerate(self.table):
            if i >= sample_size:
                break
            self.sample.append(row)

        # i would include emtpy lines for now
        self.descriptionLines = structure_detector.guess_description_lines(self.sample)

        if self.descriptionLines is None:
            raise ValueError("structure_detector should return a value, if no description lines exists, return empty")
        # allow multple header lines if existing, if none exist return 0
        self.header_lines = structure_detector.guess_headers(self.sample)
        if self.header_lines is None:
            raise ValueError("structure_detector should return a value, if no header lines exists, return empty")
        self.columns=structure_detector.guess_columns(self.sample)

        self.table.seek_line(0)#len(self.descriptionLines) + len(self.header_lines))

    def seek_line(self, lineNo):
        self.table.seek_line(lineNo)

    def next(self):
        return self.table.next()

    def __iter__(self):
        return self


    def getHeader(self):
        if self.header_line:
            return self.header_line
        else:
            return ['col'+unicode(i) for i in range(self.columns)]

    def reset(self):
        if self.header_line:
            self.table.seek_line(self.description + 1)
        else:
            self.table.seek_line(self.description)

    def generate(self, delimiter=',', newline='\n', header=True, comments=True):
        """
        :param delimiter: The delimiter symbol. The default is ",".
        :param newline: The line separator. The default is "\n".
        :param header: There will be a header in the output (if no header detected then col0,col1, ...)
        :param commentPrefix: The prefix for comments in the first rows. If false, any comments will be ignored.
        :return: A string representation of the CSV table
        """
        csvstream = StringIO()
        w = unicodecsv.writer(csvstream, encoding="utf-8", delimiter=delimiter, lineterminator=newline)

        # write description lines at top
        if comments:
            for line in self.descriptionLines:
                w.writerow(line)
        if header:
            w.writerow(self.getHeader())
        for row in self:
            w.writerow(row)
        return csvstream.getvalue()