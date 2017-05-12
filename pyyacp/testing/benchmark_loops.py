import functools
from time import sleep

from faker import Factory
fake = Factory.create()
from pyyacp.column_format_detector import pattern_comparator, translate




def filter1(value):
    return len(value)!=0

## digits
def lower(value):
    return value.lower()


def count(value):
    sleep(0.001)
    return value


def random_number(size, digits=None, fix_len=False):
    return [ unicode(fake.random_number(digits=digits, fix_len=fix_len)) for i in range(0,size)]


int_columns=[
    random_number(10,digits=1, fix_len=True),
    random_number(10,digits=2, fix_len=True),
    random_number(10,digits=2)
]

inputs=[unicode(fake.name()) for i in range(0,1000)]

print inputs
def translate1(inputs):

    inputs = [i for i in inputs if filter1(i)]
    inputs = [lower(i) for i in inputs]
    inputs = [count(i) for i in inputs]

    p = [translate(i) for i in inputs if len(i.strip()) > 0]
    p = sorted(p, key=functools.cmp_to_key(pattern_comparator))
    return p

def translate2(inputs):
    p=[]
    for i in inputs:
        if filter1(i):
            i=lower(i)
            i=count(i)
            p.append(translate(i))
    p = sorted(p, key=functools.cmp_to_key(pattern_comparator))

    return p

def translate4(inputs):
    p=[]
    pa=p.append
    for i in inputs:
        if filter1(i):
            i=lower(i)
            i=count(i)
            pa(translate(i))
    p = sorted(p, key=functools.cmp_to_key(pattern_comparator))

    return p

def translate3(inputs):
    p=map(lower,filter(lambda x: filter1(x), inputs))
    p = map(count, p)
    p=map(translate, p)
    p = sorted(p, key=functools.cmp_to_key(pattern_comparator))

    return p

if __name__ == '__main__':
    import timeit

    repeat=1
    numer=1
    print "list_comp :", timeit.Timer('f(inputs)', 'from __main__ import inputs, translate1 as f').repeat(repeat=repeat, number=numer)
    print "loop :", timeit.Timer('f(inputs)', 'from __main__ import inputs, translate2 as f').repeat(repeat=repeat, number=numer)
    print "loop2 :", timeit.Timer('f(inputs)', 'from __main__ import inputs, translate4 as f').repeat(repeat=repeat, number=numer)
    print "map_filter :", timeit.Timer('f(inputs)', 'from __main__ import inputs, translate3 as f').repeat(repeat=repeat, number=numer)

