import string

from faker import Factory
fake = Factory.create('it_IT')


## digits

def random_time(size, pattern="%H:%M:%S"):
    return [unicode(fake.time(pattern=pattern))for i in range(0,size)]

def random_iso8601(size):
    return [unicode(fake.iso8601(tzinfo=None))for i in range(0,size)]


def random_date(size, pattern="%Y-%m-%d"):
    return [unicode(fake.date(pattern=pattern))for i in range(0,size)]

def random_number(size, digits=None, fix_len=False):
    return [ unicode(fake.random_number(digits=digits, fix_len=fix_len)) for i in range(0,size)]

def random_lowercase_string(size, length=10):
    return [ unicode(''.join(fake.random_sample(elements=(string.ascii_lowercase), length=length))) for i in range(0,size)]

def random_word(size, length=10):

    return [unicode(''.join(fake.random_sample(elements=(string.ascii_uppercase), length=1)))+unicode(''.join(fake.random_sample(elements=(string.ascii_lowercase), length=length-1))) for i in
            range(0, size)]

def random_isbn13(size, separator='-'):
    return [ unicode(fake.isbn13(separator=separator)) for i in range(0,size) ]
#def random_isbn10(size, separator='-'):
#    return [ unicode(fake.isbn10(separator=separator)) for i in range(0,size)]

def random_isbn10(size, separator='-'):
    return make_pattern(size, fake.isbn10, separator=separator)

def make_pattern(size, f,**fargs):
    return [unicode(f(**fargs)) for i in range(0, size)]



def random_words(size,length=[5,3]):
    res=[]
    for i in range(0,size):
        ws=[]
        for c in length:
            ws.append(unicode(''.join(fake.random_sample(elements=(string.ascii_uppercase), length=1))) + unicode(''.join(fake.random_sample(elements=(string.ascii_lowercase), length=c - 1))))
        res.append(" ".join(ws))
    return res
int_columns=[
    random_number(10,digits=1, fix_len=True),
    random_number(10,digits=2, fix_len=True),
    random_number(10,digits=3), random_word(10, length=10),random_isbn10(10)
]



if __name__ == '__main__':
    print int_columns
    def translate(i):
        return