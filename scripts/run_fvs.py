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
from extract import extract_data
from shutil import copytree, rmtree
from subprocess import Popen, PIPE


def apply_fvs_to_plotdir(plotdir):
    """
    from plots/varWC_rx1_cond31566, 
        write working dir to ../../work/varWC_rx1_cond31566
    """
    print plotdir
    assert os.path.exists(plotdir)
    path = os.path.normpath(plotdir)
    dirname = path.split(os.sep)[-1]

    final = os.path.abspath(os.path.join(plotdir, "..", "..", "final"))
    if not os.path.exists(final):
        os.makedirs(final)

    work_base = os.path.abspath(os.path.join(plotdir, "..", "..", "work"))
    if not os.path.exists(work_base):
        os.makedirs(work_base)
    work = os.path.join(work_base, dirname)
    if os.path.exists(work):
        rmtree(work)
    copytree(plotdir, work)

    keys = glob.glob(os.path.join(work, '*.key'))
    for key in keys:
        exectute_fvs(key)
        pass

    csv = os.path.join(final, dirname + ".csv")
    df = extract_data(work)
    df.to_csv(csv, index=False, header=True)
    print "CSV written to %s" % csv


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

    error_logfile = 'log.error.txt'
    logfile = 'log.output.txt'

    cmd = [fvsbin, '--keywordfile=%s' % basename]
    print ' '.join(cmd)

    os.chdir(os.path.dirname(key))
    proc = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
    (fvsout, fvserr) = proc.communicate() 

    print fvsout
    print fvserr

    with open(logfile, 'w') as log:
        log.write("[%s]" % key)
        log.write("\n")
        log.write(fvsout)
        log.write("\n")

    has_trl = False
    has_out = False
    if os.path.exists(key.replace(".key", ".trl")):
        has_trl = True
    if os.path.exists(key.replace(".key", ".trl")):
        has_out = True

    if fvserr or not has_trl or not has_out:
        with open(error_logfile, 'w') as log:
            log.write("[%s]" % key)
            log.write("\n")
            log.write(fvserr)
            if not has_trl:
                log.write("NO .TRL FILE!")
            if not has_out:
                log.write("NO .OUT FILE!")
            log.write("\n")

if __name__ == "__main__":
    args = docopt(__doc__, version='2.0')

    indata = args['INPUT']
    apply_fvs_to_plotdir(indata)

    # TODO run_fvs.py plots/varWC_rx1...../blah.key  <--- run just this single keyfile  
    # where to put working dir? 

