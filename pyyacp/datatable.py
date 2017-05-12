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
                rows_to_add.extend(g_rows[pos:])
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
                    pass
                elif group[0] == 1 or group[1]<3:
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
                        rows_to_add.extend(g_rows[cur_line:group[1]])
                    else:
                        # seems like a new table
                        if group[1] != 1 or (
                                        i == len(grouped_L) - 1 and
                                        [sum(x) for x in zip(*grouped_L)][1] == batches):
                            # more than one row
                            # OR at the end of the group and still a full batch
                            start = cur_line
                        else:
                            # if only one row and (at the end of the file or in the middle of a group)
                            pass

                    if start is not None:
                        if cur_dt:
                            with Timer(key="adding {} rows".format(len(rows_to_add)), verbose=True):
                                cur_dt.addRows(rows_to_add)
                                rows_to_add=[]
                            tables.append(cur_dt)

                        comments = structure_detector.guess_description_lines(g_rows[start:])
                        header = structure_detector.guess_headers(g_rows[start:])

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
    if max_tables==1:
        return tables[0]
    else:
        return tables


class DataTable(object):

    def __init__(self, meta, cols, url, id, comments=None, headers=None):
        self.meta = meta
        self.no_cols = cols
        self.no_rows = 0
        self.url=url
        self.id=id

        self.comments = comments if comments else []
        self.header_rows = headers if headers else []
        self.id = None
        if len(self.header_rows)==1:
            self.columnIDs=self.header_rows[0]
        elif len(self.header_rows) > 1:
            self.columnIDs = self.header_rows[0]
        else:
            self.columnIDs =['col{}'.format(i) for i in range(1, self.no_cols+1)]

        self.column_metadata={i:{}for i in range(0,len(self.columnIDs))}

        self.data=pd.DataFrame(columns=self.columnIDs)



    def basic(self):
        b={
            'rows':self.no_rows,
            'cols':self.no_cols,
            'uri':self.url

        }
        return b

    def addRows(self, rows):
        try:
            df = pd.DataFrame(list(rows), columns=self.columnIDs)
            self.data=pd.concat([self.data,df])
            self.no_rows=self.data.shape[1]
        except Exception as e:
            print self.data
            print self.columnIDs
            print len(list(rows))
            print list(rows)[0]
            print self.header_rows

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



    def describe_colmeta(self):

        d={}
        for i in range(0, self.no_cols):
            dd=d.setdefault('col{}'.format(i+1),{})
            for a,h in enumerate(self.header_rows):
                dd['header{}'.format(a)]=h[i]

            for k,v in self.column_metadata[i].items():
                dd[k]=v
        #     if 'data_type'  in self.column_metadata[i]:
        #         dd['data_type']=self.column_metadata[i]['data_type']
        #     if 'col_patterns' in self.column_metadata[i]:
        #         dd['col_patterns']=self.column_metadata[i]['col_patterns']
        #     if 'col_stats' in self.column_metadata[i]:
        #         v = self.column_metadata[i]['col_stats']
        #         dd['selectivity']=v['selectivity']['avg']
        #         dd['selectivity_min'] = v['selectivity']['min']
        #         dd['selectivity_max'] = v['selectivity']['max']
        #         dd['unique'] = v['uniques']
        #         dd['char_length_avg'] = v['char_length']['avg']
        #         dd['char_length_min'] = v['char_length']['min']
        #         dd['char_length_max'] = v['char_length']['max']
        #         dd['most_value'] = v['top_values'][0]
        #         dd['empty'] = v['empty']
        #
        # if 'table_tane' in self.meta:
        #     for i,k in enumerate(self.meta['table_tane']['suggested_keys']):
        #         for ci in range(0, self.no_cols):
        #             d['col{}'.format(ci + 1)]['pk{}'.format(i)]= ci in k


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
        w = unicodecsv.writer(csvstream, encoding="utf-8", delimiter=delimiter, lineterminator=newline)

        # write description lines at top
        if comments:
            for line in self.descriptionLines:
                w.writerow(line)
        if header:
            for header in self.header_rows:
                w.writerow(header)
        for row in self.rowIter():
            w.writerow(row)
        return csvstream.getvalue()


    def get_meta(self):

        meta={'table':{
            'rows': self.no_rows,
            'cols': self.no_cols,
            'uri': self.url,
            'comment_lines': len(self.comments),
            'header_lines': len(self.header_rows)
        }}
        for k,v in self.meta.items():

            meta['table'][k]=v

        d = {}
        meta['column']=d
        for i in range(0, self.no_cols):
            dd = d.setdefault('col{}'.format(i + 1), {})
            for a, h in enumerate(self.header_rows):
                dd['header{}'.format(a)] = h[i]

            for k, v in self.column_metadata[i].items():
                dd[k] = v

        return meta


