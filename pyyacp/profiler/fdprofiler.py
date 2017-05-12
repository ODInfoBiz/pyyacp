import time
from collections import defaultdict
from itertools import chain, combinations

from pyyacp.profiler import Profiler
from pyyacp.timer import Timer

__author__ = 'nina'

class FDProfiler(Profiler):

    def __init__(self):
        super(FDProfiler, self).__init__('tane','table_tane')


    def _profile(self, datatable):
        with Timer(key="FDAnalyserAnalyser") as t:
            fd = TANEAlgorithm()
            stats= fd.process(datatable)
            datatable.meta[self.key]=stats


class TANEAlgorithm(object):
    '''
        Implementation of a TANE algorithm (http://hpi.de/fileadmin/user_upload/fachgebiete/naumann/folien/SS13/DPDC/DPDC_07_FDs.pdf)
        for finding functional dependencies.

        When computing the dependencies, they are described as a tuple of strings (a,b), which means a -> b.
        On the right side, we always have only one column, while on the left side there could be more columns.
        We separate them with '_'. We do it like this, because arrays cannot be keys in a dictionary.
            ('2_6', '7') : 2,6 -> 7  --- columns 2 and 6 infer column 7
            ('3', '4') : 3 -> 4 --- column 3 infers column 4
            ('', '1') : [] -> 1 --- everything infers column 1 = column 1 has always the same value independently of other columns

        When all the dependencies are computed, we transform them to arrays.

        At the end, functional dependency is represented as an array of length >= 1.
            [2,6,7] : 2,6 -> 7  --- columns 2 and 6 infers column 7
            [3,4] : 3 -> 4 --- column 3 infers column 4
            [1] : [] -> 1 --- everything infers column 1 = column 1 has always the same value independently of other columns
    '''

    def process(self, data_table):
        return self.analyse_cols(data_table.columns())

    def analyse_cols(self, columns):
        self.cols=columns
        self.checks = 0
        t0 = time.clock()

        self.relation_column_dict = {}
        self.R = self.getRelations(self.cols) # a set of relations
        self.L = defaultdict(list)
        self.cplus = {'':self.R}
        self.dependencies = []

        self.L[1] = set([x for x in self.R.split('_')])
        l = 1

        while self.L[l] != set([]):
            self.compute_dependencies(l)
            self.prune(l)
            self.L[l+1] = self.generate_next_level(l)
            l += 1


        stats = {}
        stats['dependencies'] = self.dependencies
        t1 = time.clock()
        stats['fd_processing_time'] = t1 - t0
        stats['fd_checks'] = self.checks

        stats['suggested_keys'] = self.suggestKeys()
        stats = self.transformToLists(stats)

        return stats



    def getRelations(self, cols):
        relations = []
        for i in range(len(cols)):
            relations.append(str(i))
        return '_'.join(relations)


    def compute_dependencies(self, l):
        level = self.L[l]
        for X in level:
            cplus = []

            for a in X.split('_'):
                temp = list(X.split('_'))
                temp.remove(a)
                cplus.append(set( self.getCplus('_'.join(temp)).split('_')))

            self.cplus[X] = '_'.join(sorted(set.intersection(*cplus)))

        for X in level:
            for a in [x for x in X.split('_') if x in self.cplus[X]]:
                temp = list(X.split('_'))
                temp.remove(a)
                dependency = ('_'.join(temp), a)
                if self.checkDependency(dependency):
                    self.dependencies.append(dependency)
                    self.cplus[X] = self.cplus[X].replace(a,'')
                    for r in self.R:
                        if not r in X:
                            self.cplus[X] = self.cplus[X].replace(r,'')


    def prune(self, l):
        level = self.L[l]
        tempLevel = set(level)
        for X in level:
            if self.cplus[X] == '':
                tempLevel.remove(X)

        self.L[l] = set(tempLevel)
        pass


    def generate_next_level(self, i):

        l = set([])

        prefix_blocks = self.prefix_blocks(i)
        for K in prefix_blocks.values():

            if len(K) > 1:
                for c in combinations(K,2):
                    l.add('_'.join(sorted(set(c[0].split('_')+c[1].split('_')))))
        return l


    def prefix_blocks(self, level):
        pb = defaultdict(list)

        for e in self.L[level]:
            prefix = '_'.join(e.split('_')[0:len(e.split('_'))-1])
            pb[prefix].append(e)

        return pb


    def getCplus(self, X):
        if X in self.cplus:
            return self.cplus[X]
        else:
            cplus = set([])
            for a in self.R:
                if X:
                    for b in X:
                        Xtemp = list(X)
                        if a in Xtemp:
                            Xtemp.remove(a)
                        if b in Xtemp:
                            Xtemp.remove(b)
                        dependency = (Xtemp, b)
                        if dependency not in self.dependencies:
                            cplus.add(a)
            return ''.join(sorted(cplus))


    def checkDependency(self, dependency):
        self.checks += 1

        left = dependency[0]
        if len(dependency[0]) > 0:
            left = dependency[0].split('_')

        right = dependency[1]
        rightColumn = self.cols[int(right)]

        leftColumns = [self.cols[int(l)] for l in left]

        values = {}

        for i in range(len(rightColumn)):
            #x is a column
            if tuple([x[i] for x in leftColumns]) in values:
                if values[tuple([x[i] for x in leftColumns])] != rightColumn[i]:
                    return False
            else:
                values[tuple([x[i] for x in leftColumns])] = rightColumn[i]

        return True


    def suggestKeys(self):
        '''
            We search for column or combination of columns that defines all the other columns.
            This are key candidates for the table.
        '''

        suggested_keys = []
        dependencies_dict = defaultdict(list)

        # store original dependencies
        for dependency in self.dependencies:
            left = dependency[0]
            right = dependency[1]
            dependencies_dict[left].append(right)


        for dependency in dependencies_dict:
            # check subsets of left hand side of dependency and store what they define
            for sub in map(lambda x: '_'.join(sorted(x)), subsets(dependency)):
                if sub in dependencies_dict:
                    dependencies_dict[dependency] += [a for a in dependencies_dict[sub]]
                    dependencies_dict[dependency] = list(set(dependencies_dict[dependency]))

        dependencies_dict = {k: v for k, v in dependencies_dict.items() if k != ''}

        for d in dependencies_dict:
            temp = self.R.split('_')
            for c in d.split('_'):
                temp.remove(c)
            if set(dependencies_dict[d]) == set(temp):
                suggested_keys.append(d)
        return suggested_keys

    def transformToLists(self, stats):
        '''
            Transform dependencies in '_' form to arrays.
        '''
        suggested_keys = stats['suggested_keys']
        suggested_list = []
        for key in suggested_keys:
            suggested_list.append(map(lambda x: int(x),key.split('_')))

        stats['suggested_keys'] = suggested_list

        FDs = stats['dependencies']
        FD_lists = []
        for fd in FDs:
            if fd[0] != '':
                FD_lists.append(map(lambda x:int(x), fd[0].split('_') + [fd[1]]))
            else:
                FD_lists.append(map(lambda x:int(x), [fd[1]]))

        stats['dependencies'] = FD_lists
        return stats

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def subsets(s):
    return map(set, powerset(s.split('_')))
