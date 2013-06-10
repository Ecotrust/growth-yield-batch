from celery import Celery
import sys
import os
import subprocess


celery = Celery()
sys.path.append("/var/celery")
sys.path.append("/usr/local/apps/growth-yield-batch/scripts")
celery.config_from_object('celeryconfig')


class FVSException(Exception):
    pass


OUTDIR = '/usr/local/data/out'


def write_err(uid, err):
    outerr = os.path.join(OUTDIR, uid + ".err")
    with open(outerr, 'w') as fh:
        fh.write(err)


@celery.task
def fvs(datadir):
    assert os.path.isdir(datadir)
    uid = os.path.basename(datadir)

    args = ['/usr/local/bin/fvs', datadir]
    print "Running %s" % ' '.join(args)
    proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (fvsout, fvserr) = proc.communicate()
    print fvsout  # how to stream this?
    print fvserr

    tmpdir = os.path.join('/tmp/', uid)  # .replace("_", "/")
    assert os.path.isdir(tmpdir)

    # tar/bzip the files to their final home
    outbz = os.path.join(OUTDIR, uid + ".tar.bz")
    import compress
    compress.tar_bzip2_directory(tmpdir, outbz)
    if not os.path.exists(outbz):
        err = "FVS file archive %s was not created" % (tmpdir, outbz)
        write_err(uid, err)
        raise FVSException(err)

    if proc.returncode != 0:
        err = "'fvs %s' command failed ######## OUT ### %s ####### ERR ### %s" % (datadir, fvsout, fvserr)
        write_err(uid, err)
        raise FVSException(err)

    # TODO more error checking
    # make sure we have 6 out files and 6 trl files?
    # if not pass_tests():
    #     raise FVSException("Tests failed")

    # parse data from fvs outputs
    outcsv = os.path.join(OUTDIR, uid + ".csv")
    import extract
    df = extract.extract_data(tmpdir)
    df.to_csv(outcsv, index=False, header=True)

    if not os.path.exists(outcsv):
        err = "FVS ran in %s but %s was not created" % (tmpdir, outcsv)
        write_err(uid, err)
        raise FVSException(err)

    # clean up temp data
    import shutil
    shutil.rmtree(tmpdir)

    return proc.returncode
