#!/usr/bin/env python
"""build_keys.py

Construct key files from project directory containing Rx and Condition data.

See https://github.com/Ecotrust/growth-yield-batch#building-the-batch-directory-structure-from-base-data
for details on how to set up your project directory (example below)

project_directory
|-- config.json
|-- cond
|   |-- 31566.cli
|   |-- 31566.fvs
|   |-- 31566.site
|   `-- 31566.std
`-- rx
    |-- varWC_rx1.key
    `-- varWC_rx25.key

Usage:
  build_keys.py [DIR]
  build_keys.py (-h | --help)
  build_keys.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt
from shutil import copyfile, rmtree
import os
import glob
import json


def check_indir(indir):
    """ make sure this logic matches the top-level docstring """
    # TODO MORE REQUIREMENTS ......
    subdirs = [name for name in os.listdir(indir) if os.path.isdir(os.path.join(indir, name))]
    required = ['rx', 'cond']
    for req in required:
        if req not in subdirs:
            return False
    return True


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
        rmtree(plotsdir)

    with open(os.path.join(indir, 'config.json'), 'r') as fh:
        conf = json.loads(fh.read())
        assert sorted([
            'climate_scenarios', 
            'sites', 
            'offsets']) == sorted(conf.keys())

    basekeys = glob.glob(os.path.join(indir, 'rx', '*.key'))

    include = {}
    for inc_path in glob.glob(os.path.join(indir, 'rx', 'include',"*")):
        inc_var = os.path.splitext(os.path.basename(inc_path))[0]
        with open(inc_path, 'r') as fh:
            inc_content = fh.read()
        include[inc_var] = inc_content

    for fvs in glob.glob(os.path.join(indir, 'cond', '*.fvs')):
        condid = os.path.splitext(os.path.basename(fvs))[0]
        print "Generating keyfiles for condition", condid

        cli = fvs.replace('.fvs','.cli')
        std = fvs.replace('.fvs','.std')

        stdinfo_path = fvs.replace(".fvs", ".std")
        stdinfo = open(stdinfo_path, 'r').read().strip()

        cli = fvs.replace(".fvs", ".cli")
        assert os.path.exists(cli)

        for basekey in basekeys:
            key_prefix = os.path.splitext(os.path.basename(basekey))[0]
            variant, rx = key_prefix.split('_')

            variant = variant.replace('var','')
            rx = rx.replace('rx','')

            for site_class, sitecode in conf['sites'].items():

                for climate in conf['climate_scenarios']:

                    climate_safe = climate.replace("_", '-')  # no underscores

                    out = "var%s_rx%s_cond%s_site%s_clim%s" % (
                        variant, rx, condid, site_class, climate_safe)
                    print "\t", out
                    outdir = os.path.join(plotsdir, out)
                    os.makedirs(outdir)

                    stdident = "%s    var%s_rx%s_cond%s_site%s_clim%s" % (
                        condid, variant, rx, condid, site_class, climate_safe)

                    copyfile(fvs, os.path.join(outdir, os.path.basename(fvs)))
                    copyfile(cli, os.path.join(outdir, os.path.basename(cli)))
                    copyfile(std, os.path.join(outdir, os.path.basename(std)))

                    for offset in conf['offsets']:

                        keyout = out + "_off%s.key" % (offset, )
                        keyoutpath = os.path.join(outdir, keyout)

                        from jinja2 import Template
                        with open(basekey, 'r') as fh:
                            template = Template(fh.read())
                        content = template.render(locals())

                        with open(keyoutpath, 'w') as fh:
                            fh.write(content)

    print
    print "Batch keyfile directory output to", plotsdir
