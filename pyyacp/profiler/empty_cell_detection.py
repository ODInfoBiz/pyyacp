from pyyacp.column_format_detector import l2_aggregate, l1_aggregate, translate_all, l3_shared_groups


empty_symbols=[u'NA', u'NAN', u'nan', u'NULL',u'None',u'null']

def is_not_empty(value):
    return not is_empty(value)

def is_empty(value):
    v=value.strip()
    if len(v)==0:
        return True
    return v in empty_symbols

def detect_empty_cell( values ):
    l=[len(v.strip()) for v in values]
    patterns=translate_all(values)
    L2= l2_aggregate(grouped=l1_aggregate(patterns=patterns))
    s_p =l3_shared_groups(L2)
    print l
    print L2
    for k in L2:
        print k[0]
    print s_p


    results=[]
    if min(l)==0:
        results.append('')



if __name__ == '__main__':
    values=[' ',' Wien','Salzburg']
    values = ['-', ' 12', '-12', ' ']

    detect_empty_cell(values)

    print "1234"[4:]