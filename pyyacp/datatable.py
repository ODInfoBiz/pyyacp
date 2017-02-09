import itertools
import pandas as pd

from pyyacp.table_structure_helper import guess_description_lines, _detect_header_lines

import structlog

from pyyacp.yacp import YACParserException

log = structlog.get_logger()

def parseDataTables(yacpParser, url=None, batches=80,max_tables=3):
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

    def _most_common_oneliner(L):
        return max(itertools.groupby(sorted(L)),
                   key= lambda (x, v): (len(list(v)) , -L.index(x))
                   )[0] if len(L)>0 else None


    #def readTables(cls, rowIter, batches=80, meta={}, filename=None, max_tables=3):

    rows = 0
    #gc.disable()
    for g_rows in grouper(batches, yacpParser):
        rows += len(g_rows)

        # analys the shape of the rows
        r_len = [len(row) for row in g_rows]
        max_len = max(r_len)
        est_colNo = _most_common_oneliner(r_len)
        grouped_L = [(k, sum(1 for i in g)) for k, g in itertools.groupby(r_len)]

        # print grouped_L
        groups += grouped_L

        # determine how "many" tables we have
        if len(grouped_L) == 1:
            # perfect, one table in this batch

            if cur_dt is None:
                # we have no table, this is hte first
                comments = guess_description_lines(g_rows)
                print len(g_rows[len(comments):])
                header = _detect_header_lines(g_rows[len(comments):])
                cur_dt = DataTable(yacpParser.meta, est_colNo, comments=comments, headers=header)

                pos = len(comments) + len(header)
                cur_dt.addRows(g_rows[pos:])

            elif max_len == cur_dt.noCols:
                cur_dt.addRows(g_rows)

            else:
                # not the same length, maybe different table , should not happen
                log.warning("NOT IMPLEMENTED", filename=yacpParser.url,
                            msg="not the same length, maybe different table")

                # print 'ROWS: ', len(cur_dt.rows)
                # print 'CURRENT SIZE: ', get_size.getsize(cur_dt)/1000000., 'MB'
        else:
            # lets go over the groups
            # (2,30) -> belongs to old table
            # (0,1)  -> empty line
            # (1,1)  -> comment line -> flag create_new
            # (4,20) -> belongs to new table -> create new table, start parsing at (1,1)

            cur_line = 0
            create_new = False
            for i, group in enumerate(grouped_L):
                # print group, cur_line, create_new

                if group[0] == 0:
                    # empty line, skip
                    pass
                elif group[0] == 1:
                    # there is a group with one element, that should be the comment lines
                    # also this means a new table
                    if i == len(grouped_L) - 1 and [sum(x) for x in zip(*grouped_L)][1] < batches:
                        # print "SUFFIX COMMENT LINES"
                        log.warning("SUFFIX COMMENT LINES")
                    else:
                        # we have more groups to come, so lets start a new table from this line
                        parse_start = cur_line
                        create_new = True
                else:
                    # a group with more than one column
                    start = None
                    if cur_dt is None or create_new:

                        start = cur_line
                        if create_new:
                            start = parse_start

                            # we have no table, this is hte first
                            # start parsing a new table from cur_lines



                    elif group[0] == cur_dt.noCols:
                        for row in g_rows[cur_line:group[1]]:
                            cur_dt.addRow(row)

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
                        # print "Creating new table"
                        if cur_dt:
                            tables.append(cur_dt)

                        comments = guess_description_lines(g_rows[start:])
                        header = _detect_header_lines(g_rows[start + len(comments):])
                        cur_dt = DataTable(yacpParser.meta, group[0], comments=comments, headers=header)

                        pos = len(comments) + len(header) + start
                        end = cur_line + group[1]
                        for row in g_rows[pos:end]:
                            cur_dt.addRow(row)
                        create_new = False

                cur_line += group[1]

    tables.append(cur_dt)

    prev_group = None
    agg_groups = []
    for group in groups:
        if prev_group is not None:
            if prev_group[0] == group[0]:
                # merge
                prev_group = (prev_group[0], prev_group[1] + group[1])
            else:
                agg_groups.append(prev_group)
                prev_group = group
        else:
            prev_group = group

    agg_groups.append(prev_group)
    log.info("TABLE SHAPE", groups=agg_groups, filename=url)

    if len(tables) > max_tables:
        raise YACParserException("Too many tables (#" + str(len(tables)) + ") shapes:" + str(agg_groups))
    return tables


class DataTable(object):

    def __init__(self, meta, cols, comments=None, headers=None):
        self.meta = meta
        self.noCols = cols
        self.noRows = 0

        self.comments = comments if comments else []
        self.header_rows = headers if headers else []
        self.id = None
        self.columnIDs=['col{}'.format(i) for i in range(1, self.noCols+1)]
        self.data=pd.DataFrame(columns=self.columnIDs)
        self.header_cols=list(map(list, zip(*self.header_rows)))
        #TODO, lets see what we do with the header


    def addRows(self, rows):
        df = pd.DataFrame(list(rows), columns=self.columnIDs)
        self.data=pd.concat([self.data,df])

    def rows(self):
        return [row for row in self.rowIter()]

    def rowIter(self):
        for row in self.data.itertuples():
            yield list(row[1:])

    def columns(self):
        return [collist for collist in self.columnIter()]

    def columnIter(self):
        for colName in self.columnIDs:
            yield self.data[colName].tolist()

