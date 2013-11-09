#!/usr/bin/env python
"""FVS Batch 

Looks in a directory, finds `plots` (presumably created by build_keys.py) 
finds all subdirectories (presumably plots)
and runs all the key files withing the plot dir (output to `work` directory)
and compiles their results to a csv (`final` directory)

Usage:
    batch_fvs.py [BATCHDIR]
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


def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]

if __name__ == "__main__":
    args = docopt(__doc__, version='FVS Batch 1.0')

    batchdir = args['BATCHDIR']
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

    for datadir in datadirs:
        plotdir = os.path.join(plotsdir, datadir) 
        apply_fvs_to_plotdir(plotdir)

    print "DONE!"