from collections import defaultdict

from pyyacp.profiling import HeaderRowProfiler
from pyyacp.utils.timer import Timer
# nltk tools
from nltk.corpus import wordnet
from nltk.stem.snowball import SnowballStemmer

import re


class HeaderTokensProfiler(HeaderRowProfiler):
    def __init__(self, id='header_tokens'):
        super(HeaderTokensProfiler, self).__init__(id)
        self.key='header_tokens'
        self.tokens = defaultdict(int)

    def analyse_HRow(self, header_row):
        for header_cell in header_row.cells:
            header = header_cell.value

            if len(header.split(' ')) > 1:
                # multiple words
                self.tokens['MULTIPLE'] += 1
            elif len(header.split('_')) > 1:
                # underscore separated
                self.tokens['UNDERSCORE'] += 1
                pass
            elif len(re.sub("([a-z])([A-Z])","\g<1> \g<2>", header).split(' ')) > 1:
                # camelcase separated
                self.tokens['CAMELCASE'] += 1
                pass
            else:
                # single word
                self.tokens['SINGLE'] += 1

    def getResult(self):
        return dict(self.tokens)

class HeaderReadabilityProfiler(HeaderRowProfiler):

    def __init__(self, id='header_readability'):
        super(HeaderReadabilityProfiler, self).__init__(id)
        self.key='header_readability'
        self.languages = ['english', 'german']
        self.stemmer = {lan: SnowballStemmer(lan) for lan in self.languages}
        self.header = defaultdict(int)

    def analyse_HRow(self, header_row):
        with Timer(key="HeaderReadabilityProfiler") as t:
            for header_cell in header_row.cells:
                self.header['TOTAL'] += 1
                for lan in self.languages:
                    header = header_cell.value
                    # check if word (or stemmed word) is in wordnet knowledge base
                    stemmed_h = self.stemmer[lan].stem(header)
                    if wordnet.synsets(header) or wordnet.synsets(stemmed_h):
                        self.header['READABLE'] += 1
                        break
                        #self.header[header][lan] = True
                    #else:
                        #self.header[header][lan] = False

    def getResult(self):
        return dict(self.header)