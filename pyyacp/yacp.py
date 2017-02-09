'''
Created on Jan 29, 2016

@author: jumbrich
'''

# python 3 compatible
from pyyacp.table_structure_helper import guess_description_lines, guess_headers, detect_empty_columns

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import anycsv
import unicodecsv
import structlog
log = structlog.get_logger()


class YACParserException(Exception):
    pass

class YACParser(object):
    def __init__(self, filename=None, url=None, content=None, sample_size=20, skip_guess_encoding=False):

        self.table = anycsv.reader(filename=filename, url=url, content=content, skip_guess_encoding=skip_guess_encoding, sniff_lines=sample_size)

        keys = ['encoding', 'url', 'filename', 'delimiter', 'quotechar']
        self.meta = {}
        for k,v in self.table.__dict__.items():
            if k in keys:
                if v:
                    self.meta[k] = v
                    #setattr(self, k, v)
        self.meta['dialect'] = self.table.dialect
        print self.meta



        self.sample = []
        for i, row in enumerate(self.table):
            #if len(row) != self.columns:
            #    raise ValueError("Row length of "+str(len(row))+" does not match column length of "+str(self.columns))
            if i >= sample_size:
                break
            self.sample.append(row)

        self.descriptionLines  = guess_description_lines(self.sample)
        self.description = len(self.descriptionLines)
        if self.description:
            self.sample = self.sample[self.description:]

        self.emptyColumns = detect_empty_columns(self.sample)

        self.columns = len(self.sample[self.description])

        self.header_line = guess_headers(self.sample, self.emptyColumns)


        if self.header_line:
            self.table.seek_line(self.description + len(self.header_line))
        else:
            self.table.seek_line(self.description)

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
        csvstream = StringIO.StringIO()
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


