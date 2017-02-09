from collections import defaultdict, Counter

import operator

# from csvengine.profiling import outlier_detection


def profile(table):
    row_i = 0
    count = 0.
    data_columns = [[] for _ in range(table.columns)]
    col_compl = [[] for _ in range(table.columns)]
    row_compl = 0.
    data_compl = 0

    for row_i, row in enumerate(table):
        tmp_row_compl = 0.
        for c_i, c in enumerate(row):
            # build columns
            data_columns[c_i].append(c)

            col_compl[c_i].append(True if c else False)
            data_compl += 1 if c else 0
            tmp_row_compl += 1 if c else 0
            count += 1
        row_compl += tmp_row_compl/len(row) if len(row) > 0 else 0

    header = table.header_line if table.header_line else []
    columns = [Column(vals) for vals in data_columns]

    # TODO
    outliers = {}
    # for i, c in enumerate(columns):
    #     if c.label == ColumnLabel.NUMERIC:
    #         outliers[i] = outlier_detection.get_outlier_indices(c.values)

    data = {
        'rows': row_i+1,
        'columns': table.columns,
        'header': header,
        'types': [c.label for c in columns],
        'delimiter': table.delimiter,
        'encoding': table.encoding,
        'quotechar': table.quotechar,
        'outliers': outliers,
        'completeness': {
            'columns': [sum(col)/float(len(col)) for col in col_compl],
            'table': data_compl/count,
            'data': (data_compl + sum([True if h else False for h in header])) / (count + len(header)),
            'header': sum([True if h else False for h in header]) / float(len(header)) if len(header) > 0 else -1,
            'rows': row_compl/(row_i+1)
        },
        'distinct': [len(set(c.values)) for c in columns],
        'column_unique': [list(set(c.values))[:30] for c in columns],
        'column_counter': [Counter(c.values) for c in columns]
    }
    return data



class ColumnLabel:
    NUMERIC = 'NUMERIC'
    ENTITY = 'ENTITY'
    TEXT = 'TEXT'
    ID = 'ID'
    EMPTY = 'EMPTY'

def isfloat(value):
  try:
    float(value)
    return True
  except:
    return False

def get_label(v):
    if v.isnumeric() or isfloat(v):
        return ColumnLabel.NUMERIC
    if isfloat(v):
        return ColumnLabel.NUMERIC
    if not v:
        return ColumnLabel.EMPTY
    return ColumnLabel.TEXT


class Column:
    def __init__(self, values):
        self.values = values
        self._classify()

    def _classify(self):
        self.char_dist = defaultdict(int)
        labels = defaultdict(int)
        lengths = defaultdict(int)
        tokens = defaultdict(int)

        for value in self.values:
            for c in value:
                self.char_dist[c] += 1

            labels[get_label(value)] += 1
            lengths[len(value)] += 1
            tok = len(value.split(' '))
            length = '4+' if tok >= 4 else str(tok)
            tokens[length] += 1

        # do not consider empty cells
        if ColumnLabel.EMPTY in labels:
            del labels[ColumnLabel.EMPTY]

        if len(labels) == 1 and ColumnLabel.NUMERIC in labels:
            self.label = ColumnLabel.NUMERIC
        elif len(lengths) == 1:
            self.label = ColumnLabel.ID
        elif '4+' in tokens and tokens['4+'] >= len(self.values) * 0.3:
            self.label = ColumnLabel.TEXT
        else:
            self.label = ColumnLabel.ENTITY

        #self.length = max(tokens.iteritems(), key=operator.itemgetter(1))[0]