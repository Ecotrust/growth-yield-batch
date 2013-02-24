from celery import Celery, current_task
import sys
import os
import time
import random
import subprocess


celery = Celery()
sys.path.append("/var/celery")
sys.path.append("/usr/local/apps/growth-yield-batch/scripts")
celery.config_from_object('celeryconfig')

from models import Task, db


@celery.task
def add(x, y):
    time.sleep(random.randint(0, 4))
    return x + y


@celery.task
def square(z):
    time.sleep(random.randint(0, 4))
    return z ** 2


@celery.task
def fvs(datadir):
    assert os.path.isdir(datadir)  # redundant assertion is redundant

    args = ['/usr/local/bin/fvs', datadir]
    print "Running %s" % ' '.join(args)
    proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    (out, err) = proc.communicate()
    print out  # how to stream this?

    if proc.returncode == 0:
        # TODO move output files to appropos location

        # Update task record
        request = current_task.request
        task_record = Task.query.filter_by(id=request.id).first()
        task_record.result = "/path/to/final_output_files"
        db.session.commit()
    else:
        raise Exception("fvs('%s') celery task failed" % datadir)

    return proc.returncode
