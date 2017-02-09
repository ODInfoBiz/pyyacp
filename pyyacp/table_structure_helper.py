from pyyacp import simple_type_detection

DESCRIPTION_CONFIDENCE = 10

import structlog
log = structlog.get_logger()


def guess_description_lines(sample):


    first_lines = True
    conf = 0
    description_lines = 0
    for i, row in enumerate(sample):
        if len(row) == 1 and len(row[0]) > 0:
            if not first_lines:
                # a description line candidate not in the first line, possibly no description line
                description_lines = 0
                break
        elif len(row) > 1 and all([len(c) == 0 for c in row[1:]]):
            if not first_lines:
                # a description line candidate not in the first line, possibly no description line
                description_lines = 0
                break
        else:
            if first_lines:
                description_lines=i
                #description_lines = i
                first_lines = False
            if conf > DESCRIPTION_CONFIDENCE:
                return sample[0:description_lines]
        conf += 1
    return sample[0:description_lines]


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

def _detect_header_lines(pending, max_headers=2):

    h_rows = 0
    prev_types = []

    for i, row in enumerate(pending):
        # if we observe more than 3 headers, we assume that our detection failed and the first row is the header
        if i > max_headers:
            h_rows = 1
            break

        log.debug("HEADER? ", row=row)
        row_types = [ simple_type_detection.detectType(rowValue) for rowValue in row]

        # if first row contains numeric we assume that there is no header
        if i == 0 and ('FLOAT' in row_types or 'NUM' in row_types or 'NUM+' in row_types):
            h_rows = 0
            break

        if i > 0 and prev_types[i - 1] != set(row_types) and len(row_types) != 0 and len(prev_types[i - 1]) != 0:
            # change of types -> good indicator
            cur_notstrings = not all([x == 'str' or x == 'empty' for x in row_types])
            prev_allstrings = all([x == 'str' or x == 'empty' for x in prev_types[i - 1]])
            if cur_notstrings and prev_allstrings:
                # TODO
                # row type chane
                h_rows = i
                break

        prev_types.append(set(row_types))

    if h_rows < len(pending):
        return pending[:h_rows]
    else:
        # if only strings, assume first line is header
        if len(prev_types) > 0 and all([x == 'str' or x == 'empty' for x in prev_types[0]]):
            return pending[:1]
        return None


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