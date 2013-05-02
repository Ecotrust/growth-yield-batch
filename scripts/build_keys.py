#!/usr/bin/env python
"""build_keys.py

Construct key files from .fvs, .stdinfo and base .key files

# INDIR
indir/rx/varPN_rx17_CONDID_site2.key
indir/fvs/42.fvs
indir/fvs/42.std  <-- our own thing, a single line for the stand info

# OUTDIR
indir/plots/varPN_rx17_cond42_site2/varPN_rx17_cond42_site2_original.key
indir/plots/varPN_rx17_cond42_site2/42.fvs

Usage:
  build_keys.py DIR
  build_keys.py (-h | --help)
  build_keys.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt
from shutil import copyfile
import os
import glob
import fileinput


def check_indir(indir):
    """ make sure this logic matches the top-level docstring """
    subdirs = [name for name in os.listdir(indir) if os.path.isdir(os.path.join(indir, name))]
    required = ['rx', 'fvs']
    for req in required:
        if req not in subdirs:
            return False
    return True


def process_text(keyout, basekey, shortkeyname, keyname, fvs):
    next_line_is_stdident = False
    next_line_is_fvs = False
    with open(keyout, 'w') as fh:
        for line in fileinput.input(basekey, mode='r'):
            # STDIDENT
            if line.startswith("STDIDENT"):
                next_line_is_stdident = True
            elif next_line_is_stdident:
                line = "%s   %s\n" % (shortkeyname, keyname)
                next_line_is_stdident = False

            # STDINFO
            elif line.startswith("STDINFO"):
                line = stdinfo_text + "\n"

            # .fvs FILE
            elif line.startswith("OPEN"):
                next_line_is_fvs = True
            elif next_line_is_fvs and ".fvs" in line:
                line = os.path.basename(fvs) + "\n"
                next_line_is_fvs = False

            fh.write(line)

if __name__ == "__main__":
    args = docopt(__doc__, version='Build Keys 1.0')

    indir = os.path.abspath(args['DIR'])
    outdir = os.path.join(indir, "plots")
    #outdir = os.path.abspath(args['OUTDIR'])
    if not os.path.exists(indir):
        raise Exception("%s does not exist" % indir)
    if not check_indir(indir):
        raise Exception("%s is not configured correctly; see --help" % indir)
    if os.path.exists(outdir):
        raise Exception("%s already exists" % outdir)

    basekeys = glob.glob(os.path.join(indir, 'rx', '*.key'))

    for fvs in glob.glob(os.path.join(indir, 'fvs', '*.fvs')):
        stdinfo = fvs.replace(".fvs", ".std")
        stdinfo_text = open(stdinfo, 'r').read()
        assert os.path.exists(stdinfo)
        condid = os.path.splitext(os.path.basename(fvs))[0]
        print "Generating keyfiles for condition", condid

        for basekey in basekeys:
            key = basekey.replace("CONDID", "cond%s" % condid)
            keyname = os.path.splitext(os.path.basename(key))[0]
            # create a shorter version for the fvs stand id
            shortkeyname = keyname.replace("var", "")
            shortkeyname = shortkeyname.replace("rx", "")
            shortkeyname = shortkeyname.replace("cond", "")
            shortkeyname = shortkeyname.replace("site", "")
            #print "  constructing", keyname, shortkeyname

            keyoutdir = os.path.join(outdir, keyname)
            os.makedirs(keyoutdir)
            keyout = os.path.join(keyoutdir, "%s_original.key" % keyname)

            copyfile(fvs, os.path.join(keyoutdir, os.path.basename(fvs)))

            process_text(keyout, basekey, shortkeyname, keyname, fvs)

            keyout = keyout.replace("_original", "_growonly")
            keycomp = keyname.split("_")
            keycomp[1] = "rx1"   # Assume rx1 is grow only
            keycomp[2] = "CONDID"  # Use the generic base key
            gokeyname = "_".join(keycomp)
            basekey = os.path.join(indir, 'rx', '%s.key' % gokeyname) 
            process_text(keyout, basekey, shortkeyname, keyname, fvs)

    print
    print "Batch keyfile directory output to", outdir
