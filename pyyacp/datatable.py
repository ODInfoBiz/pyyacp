#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import itertools
from StringIO import StringIO

import pandas as pd
import unicodecsv

from pyyacp.table_structure_helper import guess_description_lines, _detect_header_lines, _most_common_oneliner, \
    SimpleStructureDetector, AdvanceStructureDetector
from pyyacp.timer import Timer, timer

from pyyacp import YACParserException
import structlog
log = structlog.get_logger()


@timer(key="parse_datatable")
def parseDataTables(yacpParser, url=None, batches=80, max_tables=1, raiseError=True, structure_detector=AdvanceStructureDetector()):
    yacpParser.seek_line(0)
    tables = []
    cur_dt = None
    groups = []

    def grouper(n, iterable):
        it = iter(iterable)
        while True:
            chunk = tuple(itertools.islice(it, n))
            if not chunk:
                return
            yield chunk

    rows = 0
    rows_to_add=[]
    skipped=0
    for g_rows in grouper(batches, yacpParser):
        rows += len(g_rows)

        # analys the shape of the rows
        r_len = map(len, g_rows)
        max_len = max(r_len)
        est_colNo = _most_common_oneliner(r_len)
        grouped_L = [ ( k, sum(1 for i in g) ) for k, g in itertools.groupby(r_len)]

        groups += grouped_L

        if len(grouped_L) == 1:
            # perfect, one table in this batch
            if cur_dt is None:
                # we have no table, this is hte first
                comments = structure_detector.guess_description_lines(list(g_rows))
                header = structure_detector.guess_headers(list(g_rows))
                cur_dt = DataTable(yacpParser.meta, est_colNo, comments=comments, headers=header, url=url, id=len(tables))

                pos = len(comments) + len(header)
                rows_to_add.extend(g_rows[pos:])
            elif max_len == cur_dt.no_cols:
                rows_to_add.extend(g_rows)
            else:
                # not the same length, maybe different table , should not happen
                log.warning("NOT IMPLEMENTED", filename=yacpParser.url,
                            msg="not the same length, maybe different table")
        else:
            # lets go over the groups
            # (2,30) -> belongs to old table
            # (0,1)  -> empty line
            # (1,1)  -> comment line -> flag create_new
            # (4,20) -> belongs to new table -> create new table, start parsing at (1,1)

            cur_line = 0
            create_new = False
            for i, group in enumerate(grouped_L):

                if group[0] == 0:   # empty line, skip
                    skipped+=1
                    pass
                elif group[0] == 1 and group[1]<3:
                    # there is a group with one element, that should be the comment lines
                    # also this means a new table
                    if i == len(grouped_L) - 1 and [sum(x) for x in zip(*grouped_L)][1] < batches:
                        # print "SUFFIX COMMENT LINES"
                        log.warning("SUFFIX COMMENT LINES")
                    else:
                        # we have more groups to come, so lets start a new table from this line
                        if not create_new:
                            parse_start = cur_line
                        create_new = True
                else:
                    # a group with more than one column
                    start = None
                    if cur_dt is None or create_new:
                        start = cur_line
                        if create_new:
                            start = parse_start
                    elif group[0] == cur_dt.no_cols:
                        #cur_dt.addRows(g_rows[cur_line:group[1]])
                        rows_to_add.extend(g_rows[cur_line:cur_line+group[1]])
                    else:
                        # seems like a new table
                        if group[1] != 1 or (
                                        i == len(grouped_L) - 1 and
                                        [sum(x) for x in zip(*grouped_L)][1] == batches):
                            # more than one row
                            # OR at the end of the group and still a full batch
                            start = cur_line
                        else:
                            #print ("NOT TREATED", group[0])
                            # if only one row and (at the end of the file or in the middle of a group)
                            pass

                    if start is not None:
                        if cur_dt:
                            with Timer(key="adding {} rows".format(len(rows_to_add)), verbose=True):
                                cur_dt.addRows(rows_to_add)
                                rows_to_add=[]
                            tables.append(cur_dt)

                        _rows=g_rows[start:]
                        comments = structure_detector.guess_description_lines(_rows)
                        header = structure_detector.guess_headers(_rows)

                        cur_dt = DataTable(yacpParser.meta, group[0], comments=comments, headers=header, url=url, id=len(tables))

                        pos = len(comments) + len(header) + start
                        end = cur_line + group[1]

                        rows_to_add.extend(g_rows[pos:end])
                        create_new = False

                cur_line += group[1]

    cur_dt.addRows(rows_to_add)
    rows_to_add = []
    tables.append(cur_dt)

    prev_group = None
    agg_groups = []
    for group in groups:
        if prev_group is not None:
            if prev_group[0] == group[0]:
                # merge
                prev_group = ( prev_group[0], prev_group[1] + group[1])
            else:
                agg_groups.append(prev_group)
                prev_group = group
        else:
            prev_group = group

    agg_groups.append(prev_group)
    log.info("TABLE SHAPE", groups=agg_groups, filename=url)

    if len(tables) > max_tables:
        if raiseError:
            raise YACParserException("Too many tables (#" + str(len(tables)) + ") shapes:" + str(agg_groups))

    log.info("Parsed table", skipped=skipped, tables=len(tables))

    if max_tables==1:
        return tables[0]
    else:
        return tables


class DataTable(object):

    def __init__(self, meta, cols, url, id, comments=None, headers=None):
        self.meta = meta
        self.no_cols = cols
        self.no_rows = 0
        self.uri=url
        self.id=id

        self.comments = comments if comments else []
        self.header_rows = headers if headers else []
        self.id = None
        self.columnIDs = []
        if len(self.header_rows)==1:
            for i, v in enumerate(self.header_rows[0]):
                if len(v)>0:
                    self.columnIDs.append(v)
                else:
                    self.columnIDs.append('empty{}'.format(i))
        elif len(self.header_rows) > 1:

            for i in range(0, self.no_cols):
                added = False
                for h_row in self.header_rows:
                    if len(h_row[i])>0:
                        self.columnIDs.append(h_row[i])
                        added=True
                        break
                if not added:
                    self.columnIDs.append('empty{}'.format(i+1))
        else:
            self.columnIDs =['col{}'.format(i) for i in range(1, self.no_cols+1)]

        self.column_metadata={i:{}for i in range(0,len(self.columnIDs))}

        self.data=pd.DataFrame(columns=self.columnIDs)

    def table_structure(self):
        b={
            'uri': self.uri,
            'rows':self.no_rows,
            'columns':self.no_cols,
            'headers':self.header_rows,
            'comments': self.comments,
            'comment_lines': len(self.comments),
            'header_lines': len(self.header_rows)
        }
        return b

    def table_profile(self):

        meta = {k:v for k, v in self.meta.items()}
        if 'table_tane' in self.meta:
            meta['fd']=self.meta['table_tane']

        return meta

    def addRows(self, rows):
        try:
            df = pd.DataFrame(list(rows), columns=self.columnIDs)
            self.data=pd.concat([self.data,df])
            #print ('addRows {} {}'.format(len(rows), self.data.shape))
            self.no_rows=self.data.shape[0]
        except Exception as e:
            print(e)

    def rows(self):
        return [row for row in self.rowIter()]

    def rowIter(self):
        for row in self.data.itertuples():
            yield list(row[1:])


    def columnIter(self):
        for colName in self.columnIDs:
            yield self.data[colName].tolist()

    def columns(self):
        return [collist for collist in self.columnIter()]

    #def columns(self):
    #    return [ {'data':col,'meta':self.column_metadata[i]} for i, col in enumerate(self.columnIter())  ]



    def colum_profiles(self):

        d={}
        for i in range(0, self.no_cols):
            dd=d.setdefault('col{}'.format(i+1),{})
            for a,h in enumerate(self.header_rows):
                dd['header{}'.format(a)]=h[i]

            for k,v in self.column_metadata[i].items():
                dd[k]=v

        return pd.DataFrame(d)


    def generate(self, delimiter=',', newline='\n', header=True, comments=True):
        """
        :param delimiter: The delimiter symbol. The default is ",".
        :param newline: The line separator. The default is "\n".
        :param header: There will be a header in the output (if no header detected then col0,col1, ...)
        :param commentPrefix: The prefix for comments in the first rows. If false, any comments will be ignored.
        :return: A string representation of the CSV table
        """
        csvstream = StringIO()
        w = unicodecsv.writer(csvstream, encoding="utf-8", delimiter=str(delimiter), lineterminator=str(newline))
        c=0
        # write description lines at top
        if comments:
            for line in self.comments:
                w.writerow(line)
                c+=1
        if header:
            for header in self.header_rows:
                w.writerow(header)
                c += 1
        for row in self.rowIter():
            w.writerow(row)
            c += 1
        #print( 'WROTE',c,'LINES', len([row for row in self.rowIter()]), self.data.shape)
        return csvstream.getvalue()


    def print_summary(self, column_raw=True):
        print ('_' * 30, 'TABLE META', '_' * 30)
        for k,v in self.table_profile().items():
            print (k,v)
        print ('_' * 30, 'TABLE STRUCTURE', '_' * 30)
        for k,v in self.table_structure().items():
            print (k,v)
        print ('_' * 30, 'DATA {}'.format(self.data.shape), '_' * 30)
        print (self.data.head(5))
        print ('_' * 30, 'COLUMN PROFILE', '_' * 30)
        print (self.colum_profiles())

        if column_raw:
            for i,c in enumerate(self.columns()):
                print ('COL',i,set(c))
            print('*' * 80)



