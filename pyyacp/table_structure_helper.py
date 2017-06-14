#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import itertools

from pyyacp import column_format_detector
from pyyacp.profiler import simple_type_detection

DESCRIPTION_CONFIDENCE = 10

import structlog
log = structlog.get_logger()

class SimpleStructureDetector(object):
    # i would include emtpy lines for now
    def guess_description_lines(self,sample):
        return guess_description_lines(sample)
    # allow multple header lines if existing
    def guess_headers(self,sample, verbose=False):
        descriptionLines = self.guess_description_lines(sample)
        description = len(descriptionLines)
        if description:
            sample = sample[description:]
        emptyColumns = detect_empty_columns(sample)
        return guess_headers(sample, emptyColumns)

    def guess_columns(self,sample):
        descriptionLines = self.guess_description_lines(sample)
        description = len(descriptionLines)
        return len(sample[description])


ascii=set(['a','A','b','B'])
digits=set(['1','0'])
class AdvanceStructureDetector(object):

    # i would include emtpy lines for now
    def guess_description_lines(self, sample):
        r_len = [len(row) for row in sample]
        grouped_L = [(k, sum(1 for i in g)) for k, g in itertools.groupby(r_len)]
        est_colNo = _most_common_oneliner(r_len)
        c_lines=0
        cur_line = 0

        for i, group in enumerate(grouped_L):
            if group[0] < est_colNo:
                # We consider this as a comment line
                c_lines += group[1]
            else:
                # same length as the data rows, we should check if there are empty columns
                #if there are more than 50% empty columns, consider this a header line
                for lineno in range(cur_line, group[1] + cur_line):
                    empty_cells = 0.0
                    for a, cell in enumerate(reversed(sample[lineno])):
                        if len(cell.strip()) == 0 and empty_cells == a:
                            empty_cells += 1
                    r= empty_cells / len(sample[lineno]) if len(sample[lineno])>0 else 0
                    if  r > 0.5:
                        c_lines += 1
                    else:
                        break

            cur_line += group[1]
        return sample[0:c_lines]


    def _guess_header_by_group(self, groups, verbose=False):
        if verbose:
            print(" _guess_header_by_group({})".format(groups))
        if len(groups)==1:
            ##asume no header
            return -1
        elif len(groups)==2:
            #two groups, very likely a header
            return groups[0][1]
        else:
            h = None
            header = -1
            for i, pat in enumerate(groups):
                if h is not None:
                    if verbose:
                        print("  cell_pattern-{}: {}".format(i, pat))
                    h_sym = set(h)
                    p_sym = set(pat)
                    delta_sym = h_sym.symmetric_difference(p_sym)
                    new_sym = p_sym - h_sym

                    # Do we have a header?
                    # 1)
                    if verbose:
                        print("   ascii in h:{},digits in new:{}".format(h_sym.issubset(ascii),
                                                                         len(new_sym) > 0 and new_sym.issubset(
                                                                             digits)))
                    digits_added = h_sym.issubset(ascii) and len(new_sym) > 0 and new_sym.issubset(digits)
                    # 2) new symbols
                    new_symbols = len(new_sym) > 0 and not new_sym.issubset(h_sym)
                    if verbose:
                        print("   new symbols added:{} subset:{}".format(new_symbols,new_sym.issubset(h_sym)))
                    is_header = (digits_added or new_symbols)
                    if verbose:
                        print("   header?: {} h:{} vs p{}, delta:{}, new:{}".format(is_header, h_sym, p_sym, delta_sym,
                                                                                 new_sym))
                    if is_header:
                        if verbose:
                            print("   >>>>we think we have a header: {}".format(h))
                        header = i - 1
                    elif header != -1:
                        break
                h = pat
            return header

    # allow multple header lines if existing
    def guess_headers(self, sample, verbose=False):
        descriptionLines = self.guess_description_lines(sample)
        #skip description lines
        sample = sample[len(descriptionLines):]
        #check how many row/col groups we still have
        r_len = [len(row) for row in sample]
        grouped_L = [(k, sum(1 for i in g)) for k, g in itertools.groupby(r_len)]
        est_colNo = _most_common_oneliner(r_len)

        if len(grouped_L)>0 and grouped_L[0][0] == est_colNo:
            ##lets assume that the first group is the one we use for the header detection
            ##also make sure that the length is the estimated col length

            ##convert the rows into columns
            cols = map(list, zip(*sample))
            guessed_col_header = []
            for col in cols:
                if verbose:
                    print ("Column:{}".format(col))
                pattern = column_format_detector.translate_all(col,sort=False)
                L1 = column_format_detector.l1_aggregate(pattern)
                symbols = column_format_detector.l2_aggregate(grouped=L1)
                d=[ (k[0],sum([cc[1] for cc in k[2]])) for k in symbols]
                p_guess_headers = self._guess_header_by_group(d,verbose=verbose)
                if verbose:
                    print (p_guess_headers)
                    print ('symbols:{}'.format(symbols))
                guessed_col_header.append(p_guess_headers)

            def mode(array):
                most = max(list(map(array.count, array)))
                return list(set(filter(lambda x: array.count(x) == most, array)))

            #print(guessed_col_header)
            mc = _most_common_oneliner(guessed_col_header)
            max_h = max(guessed_col_header) if len(guessed_col_header)>0 else 0
            #print sample
            if verbose:
                print ("most_common:{}, max:{}, modes:{}, {}".format(mc, max_h, mode(guessed_col_header), guessed_col_header))
            if mc >= 0:
                return sample[0: mc]
            return []

        else:
            if len(grouped_L)>0:
                raise ValueError("Header detectiong failed, no potential header group ( likely cause, too many empty cells -> description line)")
            else:
                raise ValueError(
                    "Header detectiong failed, row length does not match (est:{}, is:{}".format(est_colNo,grouped_L[0][0]))



    def guess_columns(self, sample):
        r_len = [len(row) for row in sample]
        return _most_common_oneliner(r_len)

def _most_common_oneliner(L):
    return max(itertools.groupby(sorted(L)),
               key=lambda (x, v): (len(list(v)), -L.index(x))
               )[0] if len(L) > 0 else None


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
        row_types = [simple_type_detection.detectType(rowValue) for rowValue in row]

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
        columns = [ [] for _ in sample[1]]
        for row in sample:
            for j, c in enumerate(row):
                columns[j].append(c)
        for i, col in enumerate(columns):
            if all(['EMPTY' in simple_type_detection.detectType(c) for c in col]):
                empty_col.append(i)
    return empty_col