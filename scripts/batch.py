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
  --purge       Clear out a previous batch run; cancel all current jobs, wipe task records.
  --fix         Clear out a previous batch run and rerun only those that had failed.
"""
from docopt import docopt
import os
import sys
from tasks import fvs
from models import Task, db
from celery.result import AsyncResult

def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]

if __name__ == "__main__":
    args = docopt(__doc__, version='FVS Batch 1.0')

    batchdir = os.path.abspath(args['BATCHDIR'])
    datadirs = get_immediate_subdirectories(batchdir)
    if len(datadirs) == 0:
        print "ERROR:: Batch directory '%s' doesn't contain any subdirectories" % batchdir
        sys.exit(1)

    db.create_all()  # create tables if they don't exist

    # if --purge, cancel everything in the queue
    if args['--purge']:
        from celery import current_app as c
        c.control.purge()

        started = Task.query.filter_by(batchdir=batchdir).all()
        print "Revoking tasks... "
        for task_record in started:
            # stop the worker
            c.control.revoke(task_record.id, terminate=True, signal="SIGTERM")
            # delete the task record
            db.session.delete(task_record)
            db.session.commit()

    # if --fix, rerun tasks that have failed
    if args['--fix']:
        started = Task.query.filter_by(batchdir=batchdir).all()
        for task_record in started:
            task = fvs.AsyncResult(task_record.id)
            if task.status == "FAILURE":
                print "Revoking failed task ", task_record.id
                # delete the task record
                db.session.delete(task_record)
                db.session.commit()

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

        # check database to see if we started a currently running job for this datadir
        started = Task.query.filter_by(batchdir=batchdir, datadir=datadir).first()

        if started:
            task = fvs.AsyncResult(started.id)
            #print "Already started\tfvs('%s')\t%s\t%s" % (fulldatadir, task.id, task.status)
        else:  
            task = fvs.apply_async(args=(fulldatadir,))

            # Add a task record to the db
            task_record = Task(task.id, batchdir, datadir)
            db.session.add(task_record)
            db.session.commit()

            #print "Sent task to queue\tfvs('%s')\t%s\t%s" % (fulldatadir, task.id, task.status)

    print "Added %d plots to the queue" % n
