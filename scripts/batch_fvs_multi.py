#!/usr/bin/env python
"""FVS Batch 

Looks in a directory, finds `plots` (presumably created by build_keys.py) 
finds all subdirectories (presumably plots)
and runs all the key files withing the plot dir (output to `work` directory)
and compiles their results to a csv (`final` directory)

Usage:
    batch_fvs.py [BATCHDIR] [--cpus=1]
    batch_fvs.py (-h | --help)
    batch_fvs.py --version

Options:
    -h --help     Show this screen.
    --version     Show version.
"""
from docopt import docopt
import os
import sys
from run_fvs import apply_fvs_to_plotdir
import itertools


def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]


def grouper(n, iterable):
    it = iter(iterable)
    while True:
       chunk = tuple(itertools.islice(it, n))
       if not chunk:
           return
       yield chunk


if __name__ == "__main__":
    args = docopt(__doc__, version='FVS Batch 1.0')

    batchdir = args['BATCHDIR']
    cpus = args['--cpus']
    if not cpus:
        cpus = 1
    else:
        cpus = int(cpus)
    if cpus > 1:
        from multiprocessing import Pool
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

    if cpus == 1:
        for datadir in datadirs:
            plotdir = os.path.join(plotsdir, datadir) 
            print plotdir
            apply_fvs_to_plotdir(plotdir)
    elif cpus > 1:
        # print selected_datadirs
        def hoot(stuff):
            print "I got...", stuff
            apply_fvs_to_plotdir(stuff)

        # for selected_datadirs in list(grouper(cpus, datadirs)):
        pool = Pool(processes=cpus)
        # pool.map(apply_fvs_to_plotdir, datadirs, cpus)
        pool.map(hoot, datadirs, cpus)
    else:
        raise Exception("--cpus must be >= 1")


    print "DONE!"