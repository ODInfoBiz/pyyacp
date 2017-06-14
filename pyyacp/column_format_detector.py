#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


import functools
import string
import itertools
from difflib import SequenceMatcher as SM
from itertools import groupby

from collections import defaultdict
from pyyacp.suffix_tree import STree
from pyyacp.timer import Timer, timer

#>>>>>>>>>> TRANSLATE >>>>>>>>>>>>>>>>>

UPPER='C'
UPPER_PLACEHOLDER='A'
LOWER='c'
LOWER_PLACEHOLDER='a'
DIGIT='1'
DIGIT_PLACEHOLDER='0'
SPECIAL='$'
BRACKET='ß'


ALL=[UPPER,LOWER,DIGIT,SPECIAL,BRACKET,'+','-',' ']

in_out={
    string.digits: DIGIT,
    string.ascii_lowercase: LOWER,
    string.ascii_uppercase: UPPER
}
in_out2={
    string.digits: DIGIT,
    string.ascii_lowercase: LOWER,
    string.ascii_uppercase: UPPER,
    'äöü': LOWER,
    'ÄÖÜ': UPPER,
    ' ':' ',
    '!"#$%&*<=>?@|': SPECIAL,
    '()[]{}' : BRACKET
}



def make_trans_table(in_out):
    input=''
    output=''
    for i, o in in_out.items():
        input+=i
        output+=o*len(i)
    return string.maketrans(input, output)

def make_trans_table_unicode(in_out):
    translate_table={}
    for i, o in in_out.items():
        for char in i:
            translate_table[ord(char)]=unicode(o)

    return translate_table

#### MASTER TRANS TABLE
all_table_unicode=make_trans_table_unicode(in_out2)

def translate(input, trans_table=all_table_unicode):
    ''' use the unicode mapping'''
    if type(input) != unicode:
        input = input.decode('utf-8')
    return input.translate(trans_table)


@timer(key='translate_all')
def translate_all(inputs, filter_empty=True, sort=True):
    p = [translate(i) for i in inputs  if not filter_empty or len(i.strip())>0]
    if sort:
        p = sorted(p, key=functools.cmp_to_key(pattern_comparator))
    return p

### pattern to sorted unique list of its symbols
def pattern_to_unique_symbols(pattern):
    ''' Builds for each set a sorted string with unique symbols'''
    return ''.join(sorted(list(set(pattern))))

def patterns_to_unique_symbols(patterns):
    ''' Builds for each set a sorted string with unique symbols'''
    return [pattern_to_unique_symbols(pattern)  for pattern in patterns ]


### used to aggregate same symbol list
def aggregate_group_of_same_symbols(patterns=None, values=None):
    ''' This assumes that all patterns have the same set of symbols
        returns a single pattern for all input patterns
    '''
    if values is not None:
        patterns=translate_all(values)

    if patterns is None and values is None:
        raise ValueError("Either a list of patterns or values has to be supplied")

    symbols,p = None, None

    for i, pattern in enumerate(patterns):
        if symbols is None:
            symbols = set(pattern)
        else:
            if set(pattern) != symbols:
                raise ValueError("The list of patterns contains not all the same symbols: {} vs {}".format(symbols,set(pattern)))

        if p is None:  # nothing aggregated yet
            p = pattern
        else:
            a = p[::-1]
            b = pattern[::-1]
            match = SM(None, a, b).find_longest_match(0, len(a), 0, len(b))
            m = max([len(p), len(b)])
            if DIGIT in p:
                p = DIGIT_PLACEHOLDER * (m - match.size) + DIGIT * match.size
            if UPPER in p:
                p = UPPER_PLACEHOLDER * (m - match.size) + UPPER * match.size
            if LOWER in p:
                p = LOWER_PLACEHOLDER * (m - match.size) + LOWER * match.size
    for k in [DIGIT_PLACEHOLDER,LOWER_PLACEHOLDER,UPPER_PLACEHOLDER]:
        if k in p and p.count(k)>4:
            p = p.replace(k*p.count(k),str(p.count(k))+k)
    return p

def aggregate_group_of_pattern_tuples(p_tuples):
    #use one loop
    cnt, ps = 0, []
    for p in p_tuples:
        cnt += p[1]
        ps.append(p[0])
    agg_pattern=aggregate_group_of_same_symbols(ps)        

    return (agg_pattern , cnt )

def unique_order(seq):
    return ''.join([ x[0] for x in groupby(seq)])

def l1_aggregate(patterns, ind=0, verbose=False):
    '''
    :param patterns: list of pattern version of values
    :param ind:
    :param verbose:
    :return:
        return a list of pattern groups (pattern, count)
    '''
    l1_grouped = [(k, sum(1 for i in g)) for k, g in itertools.groupby(patterns)]
    if verbose:
        print("{} L{}: {} groups, {}".format(' '*(ind+1),1,len(l1_grouped),l1_grouped))
    return l1_grouped


def l2_aggregate(patterns=None, grouped=None, ind=0, verbose=False):
    '''
    :param patterns:
    :param grouped:
    :param ind:
    :param verbose:
    :return: a list of aggregated group information ( unique_order_pattern, len, [l1 groups (pattern, cnt) ]
    '''
    if grouped is None and patterns:
        grouped = l1_aggregate(patterns)

    l2_grouped_agg = []
    for k, g in itertools.groupby(grouped, lambda x: unique_order(x[0])):
        g=[ i for i in g] #we need to get this since groupby gives an iterator which can be exhausted
        l2_grouped_agg.append((k,len(g),g))

    if verbose:
        print("{} L{}: {} groups, {}".format(' '*(ind+2),2,len(l2_grouped_agg),l2_grouped_agg))
    return l2_grouped_agg

@timer(key='l3_shared_groups')
def l3_shared_groups(L2, ind=0, verbose=False):

    g_l2_keys=[ g[0] for g in L2 ]


    st = STree(g_l2_keys)
    lcs=st.lcs()
    if lcs is not None and len(lcs)>0:
        #we have the longest common shared subsequence, lets return it
        return {lcs:g_l2_keys}

    #import numpy as np
    #import sklearn.cluster
    #import distance

    #words = "YOUR WORDS HERE".split(" ")  # Replace this line
    #words = np.asarray(words)  # So that indexing with a list will work
    #def dist(a,b):
    #    match = SM(None, a, b).find_longest_match(0, len(a), 0, len(b))
    #    return match.size

    #lev_similarity = -1 * np.array([[dist(w1, w2) for w1 in words] for w2 in words])

    #affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5)
    #affprop.fit(lev_similarity)
    #for cluster_id in np.unique(affprop.labels_):
    #    exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
    #    cluster = np.unique(words[np.nonzero(affprop.labels_ == cluster_id)])
    #    cluster_str = ", ".join(cluster)
    #    print(" - *%s:* %s" % (exemplar, cluster_str))

    ## Ok this is trickier, we have no common pattern, that means
    #1 we can try to find differnt groups, or
    #2 find the largest group

    #For now, lets leave the code here as it is
    g_l2_keys = sorted(g_l2_keys, key=functools.cmp_to_key(pattern_comparator_length), reverse=True)

    ##first, find shared pattern groups
    s_p={} # shared pattern group
    for gk in g_l2_keys:
        if len(s_p) == 0: # empty s_p , add it
            s_p[gk]=[gk]
        else:
            m=False
            for sp in sorted(s_p.keys(), key=len, reverse=True):
                match = SM(None, sp, gk).find_longest_match(0, len(sp), 0, len(gk))
                if match.size != 0:
                    m=True
                    match_pat = sp[match.a: match.a+match.size]
                    if match_pat == sp:
                        s_p[sp].append(gk)
                    else:
                        l = s_p.pop(sp)
                        l.append(gk)
                        s_p[match_pat]=l
            if not m:
               s_p[gk]=[gk] 
    ## check that there is only a  1-1 mapping, the above code groups for each matching string, meaning
    ## there are patterns which can belong to shared matches
    added=[]
    #sort first by length of shared pattern -> we want to the longest
    for k in sorted(s_p, key=functools.cmp_to_key(pattern_comparator_length), reverse=True):
        v1 = [vv for vv in s_p[k] if vv not in added]
        s_p[k] = v1
        added.extend(v1)

    if verbose:
        print("{} Shared pattern groups:{}".format(' '*(3+ind),s_p))
    
    return s_p


def l3_get_patterns_in_L2(L2,v):
    return [g for g in L2 if g[0] in v]

def l3_aggregate(L2, len_patterns, ind=0, verbose=False, run=1, max_presub_runs=2):
    """
    :param L2: the pattern set of level 2 (
    :param ind:
    :param verbose:
    :param run:
    :param max_presub_runs:
    :return:
    """

    if verbose:
        print("{} L3 L2:{}".format(' '*(3+ind), L2))

    s_p = l3_shared_groups(L2, ind=ind, verbose=verbose)
    if len(s_p) != 1:
        if len(L2) > 5:  # len(L2)/float(len(patterns)) >0.01 or
            # we do not have any hope to aggregate the L2 patterns in a meaningful way
            # lets do some quick heuristics if there is any chance

            unique = defaultdict(int)
            un = set([])
            l = []
            for p in L2:
                cc = p[0].count('c')
                Cc = p[0].count('C')
                wc = p[0].count(' ')
                un |= set(p[0])
                if wc > 0 and wc < 3 and (cc + Cc) > wc:
                    unique['E'] += 1
                elif wc >= 3 and (cc + Cc) > wc:
                    unique['T'] += 1
            if unique['E'] / float(len(L2)) > 0.95:
                return [('E', len_patterns)]
            elif (unique['E'] + unique['T']) / float(len(L2)) > 0.95:
                return [('T', len_patterns)]
            else:
                return [(u"{{{}}}".format(''.join(un)), len_patterns)]



    results=[]
    for k, v in s_p.items():
        if verbose:
            print("{} aggregating {},{}".format(' '*(ind+4),k.encode('utf8'), v))
        
        ## check, if the pattern group has only one element with size 1, not much to aggregate
        t=True
        if len(v)==1:
            for g in l3_get_patterns_in_L2(L2, v): #'1', 1, [('1', 5)])
                if len(g[2])==1 and g[2][0][1]==1:
                    results.append(g[2][0])
                    t=False    
        if not t:
            continue
        
        ## ok, we have several patterns, lets aggregate their common pattern and also pre and suffixes
        op_b , op_a=set([]),set([]) # sets for 
        p_to_agg=[]
        p_prefix=[]
        p_suffix=[]
        for g in l3_get_patterns_in_L2(L2, v):
            #find longest match between the key and this pattern
            m = SM(None, k, g[0]).find_longest_match(0, len(k), 0, len(g[0]))
            o, l = g[0][:m.b], g[0][m.b+m.size:] #split in prefix and suffix

            s_pre = o if len(o)>0 else ''
            s_suf = l if len(l)>0 else ''
            op_b.add(o)
            op_a.add(l)
            
            for p in g[2]:
                sub_p=''
                ks = [ aa for aa in k ]
                ps = [ aa for aa in s_pre ]
                kc=ks.pop(0) if len(ks)>0 else None
                pc=ps.pop(0) if len(ps)>0 else None
                pre_i, suf_i=len(p[0]),0
                i=0
                for i,c in enumerate(p[0]):
                    while pc and c != pc:
                        pc=ps.pop(0) if len(ps)>0 else None
                    if not pc or c!=pc: 
                        #no prefix
                        while kc and c !=kc:
                            kc=ks.pop(0) if len(ks)>0 else None
                        if c == kc:
                            pre_i=min(i,pre_i)
                            sub_p+=c
                        else:
                            #ok no prefix and not a key pattern -> should be suffix
                            break

                #i=len(sub_p) if i < len(sub_p) else i
                suf_i= pre_i+len(sub_p)
                ss_pre=p[0][0:pre_i]
                ss_suf=p[0][suf_i:]

                if len(ss_pre)>0:
                    p_prefix.append(ss_pre)
                if len(ss_suf)>0:
                    p_suffix.append(ss_suf)
                p_to_agg.append((sub_p,p[1]))
        p_groups=[ [] for a in range(0, len(k) ) ]
        cnt=0
        for p in p_to_agg:
            cnt+=p[1]
            for i,x in enumerate(itertools.groupby(p[0])):
                p_groups[i].append(''.join([a for a in x[1] ]))
        agg_pattern=''.join([aggregate_group_of_same_symbols(patterns) for patterns in p_groups ])
        
        if verbose:
            print ("{}-{}- K:'{}'".format(" "*(ind+4),ind,k))
            print ("{}-{}- PP {}".format(" "*(ind+5),ind, p_prefix))
            print ("{}-{}- PS {}".format(" "*(ind+5),ind,p_suffix))


        if run<max_presub_runs:
            agg_p_prefix=aggregate_patterns(p_prefix, size=2, ind=ind+3, verbose=verbose, run=run+1)
            agg_p_suffix=aggregate_patterns(p_suffix, size=2, ind=ind+3, verbose=verbose, run=run+1)
            s_op_b = u"[{}]".format("/".join([aa[0] for aa in agg_p_prefix if aa[0] is not None]))
            s_op_a = u"[{}]".format('/'.join([aa[0] for aa in agg_p_suffix if aa[0] is not None]))

            if verbose:
                print ("{}-{}- agg_p_prefix {}".format(" "*(ind+5),ind,agg_p_prefix))
                print ("{}-{}- agg_p_suffix {}".format(" "*(ind+5),ind,agg_p_suffix))


        else:
            s_op_b=u"[{}]".format(collapse(op_b))#u"[{}]".format('/'.join(set(op_b)))
            #if verbose:
            #    print "{} {}- s_op_b {} {}".format(" "*(ind+5),ind,s_op_b,op_b).encode('utf8')

            #if verbose:
            #    print "{} {}- s_op_b {} {}".format(" "*(ind+5),ind,s_op_b,agg_p_prefix)
            s_op_a = u"[{}]".format(collapse(op_a))#u"[{}]".format('/'.join(set(op_a)))
            # if verbose:
            #    print "{} {}- s_op_a {} {}".format(" "*(ind+5),ind,s_op_a,op_a)

            # if verbose:
            #    print "{} {}- s_op_a {} {}".format(" "*(ind+5),ind,s_op_a,agg_p_suffix)

        if (len(s_op_b) == 4 and '{' in s_op_b) or len(s_op_b)==2:
            s_op_b = ''
        if (len(s_op_a) == 4 and '{' in s_op_b) or len(s_op_a)==2:
            s_op_a = ''
            
        #if verbose:
        #    print "{}-{}- Result K:'{}' pre:{} pat:{} suf:{}".format(" "*(ind+4),ind,k, s_op_b, agg_pattern, s_op_a)
        results.append((''.join([s_op_b, agg_pattern, s_op_a]),cnt))
    return results


def pattern_comparator(pattern1, pattern2):
    '''
    :param pattern1:
    :param pattern2:
    :return: numbers before ascii
    '''

    if pattern1==pattern2:
        sim = 0
    else:
        p1u = unique_order(pattern1)
        p2u = unique_order(pattern2)
        if p1u>p2u:
            sim = 1
        elif p1u==p2u:
            if pattern1>pattern2:
                sim= 1
            else:
                sim= -1
        else:
            sim = -1
    #print pattern1, pattern2,sim
    return sim

def pattern_comparator_length(pattern1, pattern2):
    '''
    :param pattern1:
    :param pattern2:
    :return: numbers before ascii
    '''
    d = len(pattern1)-len(pattern2)
    if d!=0:
        return d
    if pattern1==pattern2:
        sim= 0
    else:
        p1u = unique_order(pattern1)
        p2u = unique_order(pattern2)
        if p1u>p2u:
            sim = 1
        elif p1u==p2u:
            if pattern1>pattern2:
                sim= 1
            else:
                sim= -1
        else:
            sim = -1
    #print pattern1, pattern2,sim
    return sim

def aggregate_patterns(patterns, size=1, verbose=False, ind=0, run=1):

    ''' This method tries to aggregate all patterns into one.
    Basic assumption is that all patterns share a common sub-pattern.
    If that is not the case, the methods return groups of patterns which could be aggregated.

    The heuristic works as follows.
    1) Build groups of patterns and their frequency e.g. ( 'Aaaaa',1), ('Aaaa',1)
    2) We can sort the groups by considering the symbols, e.g. only ascii before digits

    '''
    if len(patterns)==0:
        return [ (None , 0) ]

    L1 = l1_aggregate(patterns, ind=ind, verbose=verbose)
    #L1: [('1', 6)]
    if len(L1)==1:
        return L1

    L2 = l2_aggregate(grouped=L1, ind=ind, verbose=verbose)
    # L2: [('1', 6, ['1', '1', '1', '1', '1', '1'])]
    if len(L2)==1:
        if len(L2[0][0])==1:
            #one L2 pattern with only one symbol
            return [ aggregate_group_of_pattern_tuples(L2[0][2]) ]
        else:
            #one L2 pattern but with several symbols
            #aggregate each symbol and concat the groups
            p_groups=[ [] for a in range(0, len(L2[0][0]) ) ]
            cnt=0
            for p in L2[0][2]:
                cnt+=p[1]
                for i,x in enumerate(itertools.groupby(p[0])):
                    p_groups[i].append(''.join([a for a in x[1] ]))

            agg_pattern=''.join([aggregate_group_of_same_symbols(patterns) for patterns in p_groups ])
            if verbose:
                print ('{} > {}\n{} < {}'.format(' '*(ind+2),p_groups,' '*(ind+2),agg_pattern ))
            return [ ( agg_pattern,cnt ) ]
    else:
        L3 = l3_aggregate(L2, len(patterns), ind=ind, verbose=verbose, run=run)
        if len(L3)<=size:
            return L3
        elif len(L3)==0:
            return []
        else:
            # Nothing in common
            # we could return the unique of all patterns
            c = sum([x[1] for x in L3])

            sym = ''.join( [x for x in set(''.join(x[0] for x in L3)) if x in ALL])
            return [(collapse([x[0] for x in L3]), c)]

def collapse(patterns):
    if len(patterns)<3:
        sym = '/'.join(patterns)
        return sym
    else:
        s=set(''.join(patterns))
        sym = ''.join([x for x in s if x in ALL])
        return '{{{}}}'.format(sym)

@timer(key="aggregate")
def aggregate(values, size=1,verbose=False):
    patterns=translate_all(values)
    return aggregate_patterns(patterns, size=size, verbose=verbose, run=1)

if __name__ == '__main__':
    from faker import Factory

    fake = Factory.create()
    examples=[
        #['1','2','3','4','5','6',' '],
        #['-1', '+2', '-3', '4', '5', '6','-'],
        #['-1', '+2', '-3', '4', '5', '6'],
        #['Tim Tom', 'Ulf Uls', 'Max Maxi', 'Alf Also', 'C. A. Term', '123']
        #make_pattern(10, fake.isbn10, separator='-'),
        #make_pattern(10000, fake.uri)
        #['-1'] + random_number(5, digits=1, fix_len=True)
        #['-1', '+1'] + random_number(5, digits=1, fix_len=True)
        #[fake.sentence(nb_words=6, variable_nb_words=True) for i in range(0,10)]
        [u'43,462.33', u'30,166.00', u'35,618.00', u'38,356.90', u'77,764.00', u'106,421.00', u'385,895.25', u'503,625.00', u'34,122.08', u'127,974.00', u'148,184.64', u'44,832.91', u'30,702.85', u'365,172.00', u'92,107.78', u'33,589.13', u'5,448,814.11', u'496,835.21', u'34,170.00', u'449,064.18', u'1,250,000.00', u'462,084.00', u'110,777.00', u'33,470.37', u'46,992.13', u'36,000.00', u'32,696.00', u'28,995.06', u'68,691.00', u'25,645.77', u'113,913.43', u'106,228.20', u'34,055.72', u'27,809.00', u'137,004.08', u'31,531.00', u'38,171.08', u'97,616.70', u'-3,389,597.00']
    ]

    Timer.GLOBAL_VERBOSE=False
    for values in examples:
        print ("{}\n V: {}".format("=" * 80, values))
        #p=translate_all(values, filter_empty=False)
        #p = sorted(p, key=functools.cmp_to_key(pattern_comparator))
        #print " {}\n P: {}".format("-" * 80,p)
        #l1=l1_aggregate(p)
        #print "  {}\n   L1: {}".format("." * 80, l1)
        #l2 = l2_aggregate(patterns=p)
        #print "   {}\n   L2: {}".format("'" * 80, l2)
        #l3 = l3_aggregate(l2)
        #print "   {}\n   L3: {}".format("'" * 80, l3)
        a=aggregate(values,size=3,)
        print ("   {}\n  A: {}".format("'" * 80, a))

    Timer.printStats()
