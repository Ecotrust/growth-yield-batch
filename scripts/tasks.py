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

    args = ['/usr/local/bin/fvs', datadir]  # TODO: instead of shelling out, pythonify the fvs script
    print "Running %s" % ' '.join(args)
    proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    print out  # how to stream this?
    print err

    if proc.returncode == 0:

        # Update task record
        request = current_task.request
        task_record = Task.query.filter_by(id=request.id).first()
        task_record.result = "/usr/local/data"
        db.session.commit()

        # TODO move output files to appropos location
        # TODO clean out tempfiles
    else:
        raise Exception("fvs('%s') celery task failed ######## OUT ### %s ####### ERR ### %s" % (datadir, out, err))

    return proc.returncode  # TODO tempdir if failed, output dir if good
