#!/usr/bin/env python
"""run_fvs.py

After running build_keys ....

run_fvs.py plots/varWC_rx1...../  <--- this is a plot directory containing .key files to be run

Usage:
  run_fvs.py INPUT
  run_fvs.py (-h | --help)
  run_fvs.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt
import os
import glob
from shutil import copytree
from subprocess import Popen, PIPE


def apply_fvs_to_plotdir(plotdir):
    """
    from plots/varWC_rx1_cond31566, 
        write working dir to ../../work/varWC_rx1_cond31566
    """
    assert os.path.exists(plotdir)
    path = os.path.normpath(plotdir)
    dirname = path.split(os.sep)[-1]
    work_base = os.path.abspath(os.path.join(plotdir, "..", "..", "work"))
    if not os.path.exists(work_base):
        os.makedirs(work_base)

    # TODO overwrite, bail or make multiple work dirs? Going for the later now...
    work = os.path.join(work_base, dirname)
    original_work = work
    version = 2
    while os.path.exists(work):
        work = original_work + "_%d" % version
        version += 1

    copytree(plotdir, work)
    keys = glob.glob(os.path.join(work, '*.key'))
    for key in keys:
        exectute_fvs(key)


def exectute_fvs(key):
    basename = os.path.basename(key)
    prefix, ext = os.path.splitext(basename)
    variant = "wc"
    
    if os.name == 'posix':
        fvsbin_dir = '/usr/local/bin'
        extension = 'c'  # dunno why but fvs has recently added c to end, e.g. FVSpnc
    elif os.name == 'nt':
        fvsbin_dir = 'C:\\FVSbin'
        extension = ".exe"
    fvsbin = os.path.join(fvsbin_dir, 'FVS%s' % variant + extension)

    cmd = [fvsbin, '--keywordfile=%s' % basename]
    print ' '.join(cmd)

    os.chdir(os.path.dirname(key))
    proc = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
    (fvsout, fvserr) = proc.communicate() 

    print fvsout
    print fvserr

    # if [ $? -ne 0 ]; then
    #     echo "FVS failed. Try: '''cd $TEMPDIR && cat $PREFIX.input.rsp | /usr/bin/wine $EXE''' " > $PREFIX.error.log
    #     cat $PREFIX.error.log
    #     exit 1
    # fi
    # if [ -f $PREFIX.err ]; then
    #     echo "\n !!!!!!!!!!! \n FVS found a $PREFIX.err file" >> $PREFIX.error.log
    #     # just warn, don't exit
    #     # exit 1
    # fi
    # if [ ! -f $PREFIX.out ] || [ ! -f $PREFIX.trl ]; then
    #     throw "FVS failed to produce necessary output files" >> $PREFIX.error.log
    #     cat $PREFIX.error.log
    #     exit 1
    # fi

    print "TODO: WE CREATE FINAL DIR"
    print "TODO: WE EXTRACT csv FROM THE .out FILE"


if __name__ == "__main__":
    args = docopt(__doc__, version='2.0')

    indata = args['INPUT']
    apply_fvs_to_plotdir(indata)

    # TODO run_fvs.py plots/varWC_rx1...../blah.key  <--- run just this single keyfile  
    # where to put working dir? 
