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
from shutil import copytree, rmtree
from subprocess import Popen, PIPE
try:
    from extract import extract_data
except ImportError:
    # pandas is probably not available
    extract_data = None


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
            fvsout, fvswarn = exectute_fvs(key)
            print
            print fvsout
            print
            print fvswarn
            print
        except FVSError as exc:
            err = os.path.join(final, dirname + ".err")
            with open(err, 'w') as fh:
                fh.write("key:\n" + key + "\n" + exc.message)
            print "  ERROR written to ./final/%s.err" % dirname
            return False

    print "  FVS run successfully. Results in ./work/%s" % dirname

    if extract_data:
        csv = os.path.join(final, dirname + ".csv")
        df = extract_data(work)
        df.to_csv(csv, index=False, header=True)
        print "  Parsed .out file. CSV written to ./final/%s.csv" % dirname
    else:
        print "  Unable to extract data from .out file. Install the pandas python library."


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

    # Validate outputs
    outfile = key.replace(".key", ".out")
    if not os.path.exists(outfile):
        fvserr += "No OUT file\n"
    if not os.path.exists(key.replace(".key", ".trl")):
        fvserr += "No TRL file\n"
    if "STOP" in fvsout:
        fvserr += "STOP\n"

    # Validate .out file
    still_capturing_error = 0
    still_capturing_warning = 0
    fvswarn = ""
    with open(outfile, 'r') as fh:
        for line in fh.readlines():
            if still_capturing_error > 0:
                fvserr += line
                still_capturing_error -= 1

            if still_capturing_warning > 0:
                fvswarn += line
                still_capturing_warning -= 1

            if "NO CLIMATE DATA FOR THIS STAND" in line:
                fvserr += line
                still_capturing_error = 0

            elif "ERROR" in line:
                if line.startswith("RATIO OF STANDARD ERRORS"):
                    continue
                # We've found a actual error, grab the next few lines
                fvserr += line
                still_capturing_error = 3

            elif "WARNING" in line:
                fvswarn += line
                # We've found a warning grab the next few lines
                still_capturing_warning = 3

    if fvserr:
        raise FVSError(fvserr)

    return fvsout, fvswarn

if __name__ == "__main__":
    args = docopt(__doc__, version='2.0')

    indata = args['PLOTDIRECTORY']
    apply_fvs_to_plotdir(indata)
