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
    assert os.path.isdir(datadir)

    args = ['/usr/local/bin/fvs', datadir]
    print "Running %s" % ' '.join(args)
    proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (fvsout, fvserr) = proc.communicate()
    print fvsout  # how to stream this?
    print fvserr
    if proc.returncode != 0:
        raise Exception("fvs('%s') celery task failed ######## OUT ### %s ####### ERR ### %s" % (datadir, fvsout, fvserr))

    uid = os.path.basename(datadir)
    tmpdir = os.path.join('/tmp/', uid)  # .replace("_", "/")
    assert os.path.isdir(tmpdir)

    # TODO more error checking
    # make sure we have 6 out files and 6 trl files? 
    # if not pass_tests():
    #     raise Exception("Tests failed")

    # parse data from fvs outputs
    outcsv = os.path.join('/usr/local/data/out/', uid + ".csv")
    import extract
    df = extract.extract_data(tmpdir)
    df.to_csv(outcsv)
    if not os.path.exists(outcsv):
        raise Exception("%s not created" % outcsv)

    # tar/bzip the files to their final home
    outbz = os.path.join('/usr/local/data/out/', uid + ".tar.bz")
    import compress
    compress.tar_bzip2_directory(tmpdir, outbz)
    if not os.path.exists(outbz):
        raise Exception("%s was not created" % outbz)

    # clean up temp data
    import shutil
    shutil.rmtree(tmpdir)

    # Update task record
    request = current_task.request
    task_record = Task.query.filter_by(id=request.id).first()
    task_record.result = os.path.join('/usr/local/data/out/%s.csv' % uid)
    db.session.commit()

    return proc.returncode
