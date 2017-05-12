import random
from math import factorial, log10
import itertools
import math
from math import factorial, log10

def benford_law():
    return [math.log10(1 + 1 / float(i)) * 100.0 for i in xrange(1, 10)]

def pearson(x, y):
    nx = len(x)
    ny = len(y)
    if nx != ny: return 0
    if nx == 0: return 0
    n = float(nx)
    meanx = sum(x) / n
    meany = sum(y) / n
    sdx = math.sqrt(sum([(a - meanx) * (a - meanx) for a in x]) / (n - 1))
    sdy = math.sqrt(sum([(a - meany) * (a - meany) for a in y]) / (n - 1))
    normx = [(a - meanx) / sdx for a in x]
    normy = [(a - meany) / sdy for a in y]
    return sum([normx[i] * normy[i] for i in range(nx)]) / (n - 1)

def getChiSquared(test,expected):
	chi_sq=0
	for t,e in zip(test,expected):
		print('testing :',t)
		print('expected: ',e)
		chi_sq=chi_sq+ ((t-e)*(t-e))/e
	return chi_sq

def passFailChi(chi):
	# degrees of freedom always 8 and assuming 95% confidence
	# from: https://en.wikipedia.org/wiki/Chi-squared_distribution
	# 95% conf: 15.51

	# Null hypothesis H_0: The first digits in the index minute price changes follow the Benford's law
	# Hypothesis H_1: The first digits in the index minute price changes do not follow the Benford's law}
	if (chi<15.51):
		return True
	else:
		return False


def leemis_m(counts, expected):
    '''Based on the Wikipedia article fo Leemis' m.
    I need to have someone check this equation to make sure I got it
    right'''
    deviations = []
    for i in range(len(counts)):
        deviations.append(counts[i] - expected[i])
    m = math.sqrt(sum(counts)) * max(deviations)
    return m


def cho_gaines_distance(counts, expected):
    '''Based on the Wikipedia article for Cho-Gaines' Distance, d.
    I need to have someone check this to make sure it's good.'''
    Sigma = 0
    for i in range(len(counts)):
        Sigma += (counts[i] - expected[i]) ** 2

    distance = math.sqrt(sum(counts) * Sigma)
    return distance


def leemis_critical(m, alpha=.05):
    '''alpha can take on one of the values of .01, .05, .10 for the
    signficance you wish you test. This method can only be run
    after first calculating Leemis' m by running the lemmis_m method'''
    assert alpha == .05 or alpha == .01 or alpha == .10, "This " \
                                                         "module currently supports alpha critical-values of .01, .05, or .10"

    if alpha == .05:
        CV = 0.967
    elif alpha == .01:
        CV = 1.212
    else:  # alpha = .10
        CV = 0.851

    if m > CV:
        print "We can reject the null hypothesis that the data follows " \
              "Benford's law with an m of {} against a crtical value of {}, " \
              "alpha {} using Leemis' m".format(m, CV, alpha)

    else:
        print "We cannot reject the null hypothesis that the data follows " \
              "Benford's law with an m of {} against a crtical value of {}, " \
              "alpha {} using Leemis' m".format(m, CV, alpha)


def cho_gaines_critical(distance, alpha=.05):
    assert alpha == .05 or alpha == .01 or alpha == .10, "This " \
                                                         "module currently supports alpha critical-values of .01, .05, or .10"

    if alpha == .05:
        CV = 1.330
    elif alpha == .01:
        CV = 1.569
    else:  # alpha = .10
        CV = 1.212

    if distance > CV:
        print "We can reject the null hypothesis that the data follows " \
              "Benford's law with an d of {} against a crtical value of {}, " \
              "alpha {} using Cho-Gaines' d".format(distance, CV, alpha)

    else:
        print "We cannot reject the null hypothesis that the data follows " \
              "Benford's law with an d of {} against a crtical value of {}, " \
              "alpha {} using Cho-Gaines' d".format(distance, CV, alpha)


def get_leading_number(cell):
    numbers = "123456789"
    l = map(int, filter(lambda x: x in numbers, cell))
    return l[0] if len(l)>0 else 0

def getExpectedBenfordCount(size):
	return map(lambda x:x*0.01*size, benford_law())


from faker import Factory
fake = Factory.create()
#r=[unicode(fake.random_digit()*0.5) for i in range (1,100000)]
r=[unicode(random.randint(0, 10000)) for a in range(1000)]





#r=[unicode(factorial(i)) for i in range(0,100)]
#print r
print r

#get leadign numpers
x=sorted(map(get_leading_number,r))
import numpy as np
d=np.array([x.count(k) for k in range(1,10)])

#b=[math.log10(1 + 1 / float(i)) * 100.0 for i in xrange(1, 10)]
#d = np.array(getExpectedBenfordCount(100))


print d
d_prob= d/float(sum(d))*100
print d_prob

##
y= getExpectedBenfordCount(len(x))
print 'expected'
print y
y_prob= benford_law()
print y_prob


def chisq_stat(O, E):
    return sum([(o - e) ** 2 / e for (o, e) in zip(O, E)])


chi=getChiSquared(d,y)
print 'CHI', chi, passFailChi(chi)
print 'CHI', chisq_stat(d,y)

m=leemis_m(d_prob,y_prob )
print 'LEEMIS',m, leemis_critical(m)
dist=cho_gaines_distance(d_prob,y_prob)
print "CHO", dist, cho_gaines_critical(dist)
