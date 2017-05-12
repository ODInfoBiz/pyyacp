from pyyacp import datatable, YACParser
from pyyacp.profiler.fdprofiler import TANEAlgorithm, FDProfiler
from pyyacp.table_structure_helper import AdvanceStructureDetector
from pyyacp.testing.csv_iterator import csvContent_iter
from pyyacp.timer import Timer

if __name__ == '__main__':
    tane=TANEAlgorithm()


    cols={'A':[i for i in range(0,100)],
          'B':[i%2 for i in range(0,100)],
          'C':[i%3 for i in range(0,100)],
          'D': [i % 4 for i in range(0, 100)],
          'E': [i % 2 for i in range(0, 100)]
          }
    with Timer(verbose=True):
        print tane.analyse_cols(cols.values())

    portalID = 'data_wu_ac_at'

    profilers = [FDProfiler()]  # ,ColumnRegexProfiler()]#,XSDTypeDetection()]
    c = 0
    for uri, csv_file in csvContent_iter(portalID):
        c += 1
        print "{}, {} -> {}".format(c, uri, csv_file)
        try:
            from pyyacp.yacp import YACParser

            yacp = YACParser(filename=csv_file, sample_size=1800, structure_detector=AdvanceStructureDetector(),
                             verbose=True)

            table = datatable.parseDataTables(yacp, url=uri)
            print table.data.head(5)

            profiler_engine.profile(table, profilers=profilers)

            print 'Comments', table.comments
            print 'Headers', table.header_rows

            for i in range(0, table.no_cols):
                print "Column", i, table.header_rows[0][i]
                for p in profilers:
                    if p.key.startswith("col"):
                        if len(table.meta[p.key]) >= i:
                            print ' [{}] {} '.format(p.id, table.meta[p.key][i])
            for p in profilers:
                if p.key.startswith("table"):
                    print '[{}] {} '.format(p.id, table.meta[p.key])

            print table.meta