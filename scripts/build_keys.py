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
  build_keys.py [DIR]
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


def check_indir(indir):
    """ make sure this logic matches the top-level docstring """
    # TODO MORE REQUIREMENTS ......
    subdirs = [name for name in os.listdir(indir) if os.path.isdir(os.path.join(indir, name))]
    required = ['rx', 'fvs']
    for req in required:
        if req not in subdirs:
            return False
    return True

def get_sitecode(variant, site):
    # TODO get from G:\projects\projects2011\LandOwnerTools\util\scripts\Site Index Override Addfiles
    return "SITECODE          DF       125         1"


if __name__ == "__main__":
    args = docopt(__doc__, version='Build Keys 1.0')

    indir = args['DIR']
    if not indir:
        indir = os.path.curdir
    indir = os.path.abspath(indir)
    plotsdir = os.path.join(indir, "plots")
    if not os.path.exists(indir):
        raise Exception("%s does not exist" % indir)
    if not check_indir(indir):
        raise Exception("%s is not configured correctly; see --help" % indir)
    if os.path.exists(plotsdir):
        raise Exception("%s already exists" % plotsdir)

    # Require a climate.conf
    #     lines starting with # are ignored, one climate scenario name
    with open(os.path.join(indir, 'climate.conf'), 'r') as fh:
        climate_scenarios = [x.strip() for x in fh.readlines() if not x.startswith('#')]

    # Look for an offset.conf
    offsets = [0]
    try:
        with open(os.path.join(indir, 'offset.conf'), 'r') as fh:
            offsets.extend([int(x.strip()) for x in fh.readlines()])
    except OSError:
        pass

    # Require a default.site
    #     one site index per line
    with open(os.path.join(indir, 'default.site'), 'r') as fh:
        site_indexes = [x.strip() for x in fh.readlines()]

    basekeys = glob.glob(os.path.join(indir, 'rx', '*.key'))

    for fvs in glob.glob(os.path.join(indir, 'fvs', '*.fvs')):
        condid = os.path.splitext(os.path.basename(fvs))[0]
        print "Generating keyfiles for condition", condid

        stdinfo_path = fvs.replace(".fvs", ".std")
        stdinfo = open(stdinfo_path, 'r').read().strip()

        cli = fvs.replace(".fvs", ".cli")
        assert os.path.exists(cli)

        for basekey in basekeys:
            key_prefix = os.path.splitext(os.path.basename(basekey))[0]
            variant, rx = key_prefix.split('_')

            variant = variant.replace('var','')
            rx = rx.replace('rx','')

            for site in site_indexes:

                out = "var%s_rx%s_cond%s_site%s" % (variant, rx, condid, site)
                print "\t", out
                outdir = os.path.join(plotsdir, out)
                os.makedirs(outdir)

                stdident = "%s    var%s_rx%s_cond%s_site%s" % (
                    condid, variant, rx, condid, site)

                cli = fvs.replace('.fvs','.cli')
                std = fvs.replace('.fvs','.std')
                copyfile(fvs, os.path.join(outdir, os.path.basename(fvs)))
                copyfile(cli, os.path.join(outdir, os.path.basename(cli)))
                copyfile(std, os.path.join(outdir, os.path.basename(std)))

                sitecode = get_sitecode(variant, site)

                for climate in climate_scenarios:

                    for offset in offsets:
                        print "\t\t", climate, offset,

                        keyout = out + "_clim%s_off%s.key" % (
                            climate.replace("_","-"), offset)
                        keyoutpath = os.path.join(outdir, keyout)
                        print keyoutpath

                        from jinja2 import Template
                        with open(basekey, 'r') as fh:
                            template = Template(fh.read())
                        content = template.render(locals())

                        with open(keyoutpath, 'w') as fh:
                            fh.write(content)

    print
    print "Batch keyfile directory output to", plotsdir
