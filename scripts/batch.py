#!/usr/bin/env python
"""FVS Batch 

Looks in a directory, 
finds all subdirectories (which are presumed to be a data dir for the fvs script),
and fires off a celery task for each

Usage:
  batch.py BATCHDIR [--purge] [--fix] 
  batch.py (-h | --help)
  batch.py --version

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

    batchdir = os.path.abspath(args['BATCHDIR'])
    datadirs = get_immediate_subdirectories(batchdir)
    if len(datadirs) == 0:
        print "ERROR:: Batch directory '%s' doesn't contain any subdirectories" % batchdir
        sys.exit(1)

    print "Sending all tasks to the queue... patience..."
    i = 0
    j = 1000
    n = len(datadirs)
    for datadir in datadirs:
        # output every jth iteration
        i += 1
        if i % j == 0:
            print "  sent %s of %s" % (i, n)

        fulldatadir = os.path.join(batchdir, datadir)
        task = fvs.apply_async(args=(fulldatadir,))

    print "Added %d plots to the queue" % n
