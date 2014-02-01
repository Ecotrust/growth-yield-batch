#!/usr/bin/env python
"""FVS Batch 

Looks in a directory, finds `plots` (presumably created by build_keys.py) 
finds all subdirectories (presumably plots)
and runs all the key files withing the plot dir (output to `work` directory)
and compiles their results to a csv (`final` directory)

Usage:
    batch_fvs.py [options] [BATCHDIR] 
    batch_fvs.py (-h | --help)
    batch_fvs.py --version

Options:
    -h --help        Show this screen.
    --version        Show version.
    --cores=<cpus>   Number of CPU Cores [default: 1]
    --failures-only  Start a new batch to rerun previously failed plots
"""
from docopt import docopt
import os
import sys
from run_fvs import apply_fvs_to_plotdir
import glob


def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]


if __name__ == "__main__":
    args = docopt(__doc__, version='FVS Batch 1.0')

    batchdir = args['BATCHDIR']
    cores = int(args['--cores'])
    failures_only = bool(args['--failures-only'])
    if not batchdir:
        batchdir = os.path.curdir
    batchdir = os.path.abspath(batchdir)
    plotsdir = os.path.join(batchdir, 'plots')
    if not os.path.exists(plotsdir):
        print "ERROR:: No plots directory found in %s; Run build_keys first" % batchdir
        sys.exit

    datadirs = get_immediate_subdirectories(plotsdir)
    if len(datadirs) == 0:
        print "ERROR:: Plots directory '%s' doesn't contain any subdirectories" % batchdir
        sys.exit(1)

    plotdirs = [os.path.join(plotsdir, x) for x in datadirs]

    if failures_only:
        errs = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(os.path.join("final", "*.err"))]
        print "removing %s error files" % len(errs)
        map(os.remove, [os.path.join(batchdir, "final", "%s.err" % x) for x in errs])

        print "calculating diff of all plots vs successes..."
        # Assume that the csv exists (may want to query the db instead?)
        good = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(os.path.join("final", "*.csv"))]
        plotdirs = [os.path.join(plotsdir, x) for x in datadirs if x not in good]
        print "\t", len(plotdirs)

    if cores == 1:
        # Single core
        # equivalent to:
        # for plotdir in plotdirs:
        #     apply_fvs_to_plotdir(plotdir)
        map(apply_fvs_to_plotdir, plotdirs)
    elif cores > 1:
        # Multicore
        from multiprocessing import Pool
        pool = Pool(cores)
        pool.map(apply_fvs_to_plotdir, plotdirs)
        pool.close()
        pool.join()
    else:
        raise Exception("cores must be >= 1")

    print "DONE!"
