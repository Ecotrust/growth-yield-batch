#!/usr/bin/env python
"""run_fvs.py

After running build_keys ....

run_fvs.py plots/varWC_rx1...../  <--- this is a plot directory containing .key files to be run

Usage:
  run_fvs.py PLOTDIRECTORY
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


class FVSError(Exception):
    pass

def apply_fvs_to_plotdir(plotdir):
    """
    from plots/varWC_rx1_cond31566, 
        write working dir to ../../work/varWC_rx1_cond31566
    """
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
        try:
            exectute_fvs(key)
        except FVSError as exc:
            err = os.path.join(final, dirname + ".err")
            with open(err, 'w') as fh:
                fh.write("key:" + key + "\n" + exc.message)
            print "  ERROR written to %s" % err
            return False

    csv = os.path.join(final, dirname + ".csv")
    df = extract_data(work)
    df.to_csv(csv, index=False, header=True)
    print "  CSV written to %s" % csv


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

    logfile = 'log.output.txt' # TODO this prolly gets overridden eh

    cmd = [fvsbin, '--keywordfile=%s' % basename]
    print ' '.join(cmd)

    os.chdir(os.path.dirname(key))
    proc = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
    (fvsout, fvserr) = proc.communicate() 

    with open(logfile, 'w') as log:
        log.write("[%s]" % key)
        log.write("\n")
        log.write(fvsout)
        log.write("\n")

    # Validate
    if not os.path.exists(key.replace(".key", ".out")):
        fvserr += "No OUT file\n"
    if not os.path.exists(key.replace(".key", ".trl")):
        fvserr += "No TRL file\n"
    if "STOP 20" in fvsout:
        fvserr += "STOP 20\n"

    if fvserr:
        raise FVSError(fvserr)

if __name__ == "__main__":
    args = docopt(__doc__, version='2.0')

    indata = args['INPUT']
    apply_fvs_to_plotdir(indata)

    # TODO run_fvs.py plots/varWC_rx1...../blah.key  <--- run just this single keyfile  
    # where to put working dir? 

