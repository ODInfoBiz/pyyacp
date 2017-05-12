# -*- coding: utf-8 -*-
import re, string, timeit


input= "test_123-TEST"

digit_table = string.maketrans(string.digits,"1"*len(string.digits))
ascii_lower_table = string.maketrans(string.ascii_lowercase,"a"*len(string.ascii_lowercase))
ascii_upper_table = string.maketrans(string.ascii_uppercase,"A"*len(string.ascii_uppercase))

in_out={
    string.digits:'1',
    string.ascii_lowercase:'a',
    string.ascii_uppercase:'A'
}
in_out2={
    string.digits:'1',
    string.ascii_lowercase:'a',
    string.ascii_uppercase:'A',
    'ä':'a'
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
        for char in i.decode('utf-8'):
            translate_table[ord(char)]=unicode(o)

    return translate_table

all_table = make_trans_table(in_out)
all_table_unicode=make_trans_table_unicode(in_out2)

def translate_digits(s):
    return s.translate(digit_table)
def translate_ascii_lower(s):
    return s.translate(ascii_lower_table)
def translate_ascii_upper(s):
    return s.translate(ascii_upper_table)

def translate(s):
    s=translate_digits(s)
    s=translate_ascii_lower(s)
    s=translate_ascii_upper(s)
    return s

def translate1(s):
    return s.translate(all_table)

def translate5(s):
    return s.translate(all_table_unicode)


def translate2(s):
    s=re.sub(r'\d', '1', s)
    s=re.sub(r'[A-Z]', 'A', s)
    s=re.sub(r'[a-z]', 'a', s)
    return s


num_dict = {'123456': "1",
                'test': "a",
                'TEST': "A",
                '_':'_',
                '-': '-'}
def translate4(s):

    string = ""
    for c in s:
        for k in num_dict.keys():
            if c in k:
                string += num_dict[k]
    return string



if __name__ == '__main__':

    print "input",input
    print "translate", translate(input)
    print "translate1", translate1(input)
    print "translate2", translate2(input)
    print "translate4", translate4(input)
    print "translate5", translate5('ä'.decode('utf-8'))



    #print "sets      :", timeit.Timer('f(s)', 'from __main__ import s,test_set as f').timeit(1000000)
    print "translate :", timeit.Timer('f(input)', 'from __main__ import input,translate as f').timeit(1000000)
    print "translate1   :", timeit.Timer('f(input)', 'from __main__ import input,translate1 as f').timeit(1000000)
    print "translate2   :", timeit.Timer('f(input)', 'from __main__ import input,translate2 as f').timeit(1000000)
    print "translate4   :", timeit.Timer('f(input)', 'from __main__ import input,translate4 as f').timeit(1000000)