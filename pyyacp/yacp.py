'''
Created on Jan 29, 2016

@author: jumbrich
'''
from pyyacp import simple_type_detection

# python 3 compatible
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    
import unicodecsv as csv
import anycsv
import unicodecsv

class YACParserException(Exception):
    pass

class YACParser(object):
    def __init__(self, filename=None, url=None, content=None, sample_size=20, skip_guess_encoding=False):

        self.table = anycsv.reader(filename=filename, url=url, content=content, skip_guess_encoding=skip_guess_encoding)

        # copy dialect information to the returning result object
        keys = ['encoding', 'url', 'filename', 'delimiter', 'quotechar', 'columns']
        for k,v in self.table.__dict__.items():
            if k in keys:
                if v:
                    setattr(self, k, v)

        self.sample = []
        for i, row in enumerate(self.table):
            #if len(row) != self.columns:
            #    raise ValueError("Row length of "+str(len(row))+" does not match column length of "+str(self.columns))
            if i >= sample_size:
                break
            self.sample.append(row)


        self.description = guess_description_lines(self.sample)
        if self.description:
            self.sample = self.sample[self.description:]

        self.emptyColumns = detect_empty_columns(self.sample)

        self.columns = len(self.sample[self.description])

        self.descriptionLines = []
        for i in range(0, self.description):
            self.descriptionLines.append(self.sample.pop(0))

        self.header_line = guess_headers(self.sample, self.emptyColumns)


        if self.header_line:
            self.table.seek_line(self.description + 1)
        else:
            self.table.seek_line(self.description)

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
    
DESCRIPTION_CONFIDENCE = 10

def guess_description_lines(sample):

    first_lines = True
    conf = 0
    description_lines = 0
    for i, row in enumerate(sample):
        if len(row) == 1 and len(row[0]) > 0:
            if not first_lines:
                # a description line candidate not in the first line, possibly no description line
                return 0
        elif len(row) > 1 and all([len(c) == 0 for c in row[1:]]):
            if not first_lines:
                # a description line candidate not in the first line, possibly no description line
                return 0
        else:
            if first_lines:
                description_lines = i
                first_lines = False
            if conf > DESCRIPTION_CONFIDENCE:
                return description_lines
        conf += 1
    return description_lines


HEADER_CONFIDENCE = 1

def guess_headers(sample, empty_columns=None):
    # first store types of first x rows
    types = []
    for i, row in enumerate(sample):
        if i >= HEADER_CONFIDENCE:
            break
        row_types = []
        for c in row:
            t = simple_type_detection.detectType(c)
            row_types.append(t)
        types.append(row_types)

    # now analyse types
    first = types[0]
    if empty_columns:
        first = [i for j, i in enumerate(first) if j not in empty_columns]
    first_is_alpha = all(['ALPHA' in t for t in first])
    if first_is_alpha:
        return sample[0]
    return []

def detect_empty_columns(sample):
    empty_col = []
    if len(sample) > 0:
        columns = [[] for _ in sample[0]]
        for row in sample:
            for j, c in enumerate(row):
                columns[j].append(c)
        for i, col in enumerate(columns):
            if all(['EMPTY' in simple_type_detection.detectType(c) for c in col]):
                empty_col.append(i)
    return empty_col