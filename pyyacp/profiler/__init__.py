import functools

from pyyacp import column_format_detector
import regroup

from pyyacp.column_format_detector import aggregate_patterns, translate, pattern_comparator
from pyyacp.profiler.empty_cell_detection import is_not_empty
from pyyacp.timer import Timer, timer
import structlog
log = structlog.get_logger()


@timer(key="profile_table")
def apply_profilers(table, profilers=None):
    for profiler in profilers:
        log.info("Running profiler: [{}] {}".format(profiler.__class__, type(profiler)))
        if isinstance(profiler, ColumnProfilerSet):
            for i, col in enumerate(table.columns()):
                profiler.profile_column(col, table.column_metadata[i])
        else:
            profiler.profile_table(table)

class ColumnProfilerSet(object):
    """
    This class provides a wrapper for profilers which take a column as input
    """
    def __init__(self, profilers=[]):
        self.profiler_factories=profilers

    def _init(self):
        self.profilers=[p() for p in self.profiler_factories]

    def profile_column(self, column, meta):
        self._init()
        with Timer(key='cloop', verbose=True):
            for p in self.profilers:
                result = p.profile_column(column, meta)
                self._add_results(meta, result, p)

    def _add_results(self, meta, results, p):
        if isinstance(results, dict):
            for k, v in results.items():
                meta["{}_{}".format(p.key, k)] = v
        else:
            meta["{}".format(p.key)] = results


class ColumnByCellProfilerSet(ColumnProfilerSet):

    def __init__(self, profilers=[]):
        super(ColumnByCellProfilerSet, self).__init__(profilers=profilers)

    def profile_column_by_cell(self, column, meta):
        self._init()
        pa=[p.accept for p in self.profilers]

        for cell in column:
            for p in pa:
                p(cell)
        for p in self.profilers:
            result = p.result()
            self._add_results(meta, result, p)

    def profile_column(self, column, meta):
        self.profile_column_by_cell(column, meta)



class Profiler(object):
    def __init__(self, id, key):
        self.id=id
        self.key=key

class ColumnProfiler(Profiler):
    def __init__(self, id, key):
        super(ColumnProfiler, self).__init__(id,key)

    def profile_column(self, column, meta):
        pass

class ColumnByCellProfiler(Profiler):
    def __init__(self, id, key):
        super(ColumnByCellProfiler, self).__init__(id,key)

    def result(self):
        pass

    def accept(self, cell):
        pass


class ColumnPatternProfiler(ColumnProfiler,ColumnByCellProfiler):

    def __init__(self, num_patterns=3):
        super(ColumnPatternProfiler, self).__init__('cpp','patterns')
        self.num_patterns=num_patterns
        self.patterns=[]
        self.pa = self.patterns.append

    @timer(key="cpp_column")
    def profile_column(self, column, meta):
        return column_format_detector.aggregate(filter(is_not_empty,column), size=self.num_patterns)

    @timer(key="cpp_result")
    def result(self):
        p = sorted(self.patterns, key=functools.cmp_to_key(pattern_comparator))
        #empty
        #reset in case there is another column
        self.patterns = []
        self.pa = self.patterns.append
        return aggregate_patterns(p, size=self.num_patterns)

    def accept(self, cell):
        if is_not_empty(cell):
            self.pa(translate(cell))


class ColumnRegexProfiler(Profiler):
    def __init__(self):
        super(ColumnRegexProfiler, self).__init__('crp','col_regex')
        self.values=[]

    def profile_column(self, column, meta):
        return column_format_detector.aggregate(column, size=self.num_patterns)

    def result(self):
        res=self.profile_column(self.values, None)
        self.values=[]
        return res

    def accept(self, cell):
        self.values.append(cell)

    def _profile(self, table):
        for i, col in enumerate(table.columns()):
            try:
                regex = regroup.DAWG.from_iter(col).serialize()
                table.column_metadata[i][self.key]=regex
            except Exception as e:
                table.column_metadata[i][self.key]="exc:{}".format(str(e.__class__))





