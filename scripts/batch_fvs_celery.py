#!/usr/bin/env python
"""FVS Batch 

Looks in a directory, 
finds all subdirectories (which are presumed to be a data dir for the fvs script),
and fires off a celery task for each

Usage:
  batch_fvs_celery.py [BATCHDIR]
  batch_fvs_celery.py (-h | --help)
  batch_fvs_celery.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt
import os
import sys
from tasks import fvs


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

    j = 100
    n = len(datadirs)
    for i, datadir in enumerate(datadirs):
        # output every jth iteration
        i += 1
        if i % j == 0:
            print "  sent %s of %s" % (i, n)

        fulldatadir = os.path.join(os.path.abspath(plotsdir), datadir)
        task = fvs.apply_async(args=(fulldatadir,))

    print "Added %d plots to the queue" % n
