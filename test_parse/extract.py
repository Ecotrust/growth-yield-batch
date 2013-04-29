#!/usr/bin/env python
"""extract.py

Extract stuff from fvs .out files

Usage:
  extract.py DIR
  extract.py (-h | --help)
  extract.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt
import glob
import os
import re


def parse_name(filename):
    """
    >>> parse_name("/path/to/some/varPN_rx4_cond43_site2_00.key")
    >>> parse_name("varPN_rx4_cond43_site2_00.key")
    >>> parse_name("varPN_rx4_cond43_site2_00")

    {'var': 'PN', 'cond': '43', 'rx': '4', 'site': '2', 'offset': '00'}
    """
    basename = os.path.splitext(os.path.basename(filename))[0]
    exp = re.compile("var([a-zA-Z]+)_rx([0-9a-zA-Z]+)_cond([0-9a-zA-Z]+)_site([0-9a-zA-Z]+)_([0-9]+)")
    parts = exp.match(basename).groups()
    keys = ("var", "rx", "cond", "site", "offset")
    return dict(zip(keys, parts))


def split_fixed(line, fixed_schema):
    funcs = {'int': int, 'float': float, 'str': str}
    data = {}
    for var in fixed_schema:
        data[var[0]] = funcs[var[3]](line[var[1]-1:var[2]])
    return data


carbon_rows = []
summary_rows = []
activity_rows = []


def extract_data(outfile):
    info = parse_name(outfile)

    ############# Extract Carbon Report
    ready = False
    countdown = None
    with open(outfile, 'r') as fh:
        for line in fh:
            if "STAND CARBON REPORT" in line:
                # We've found the carbon report, data starts 9 lines down
                ready = True
                countdown = 9

            if not ready or countdown > 0:
                if countdown:
                    countdown -= 1
                continue

            if line.strip() == "":
                # blank line == we're done
                break

            # Got it: this is a data line
            """
            'year', 'agl', 'agl_merch', 'bgl', 'bgd', 'dead', 'ddw', 'floor', 'shbhrb',
            'total_stand_carbon', 'total_removed_carbon', 'carbon_fire'
            """
            fixed_schema = [
                ('year', 1, 4, 'int'),
                ('agl', 5, 13, 'float'),
                ('bgl', 23, 31, 'float'),
                ('dead', 41, 49, 'float'),
            ]
            data = split_fixed(line.strip(), fixed_schema)

            # calculate our own carbon
            carbon = float(data['agl']) + float(data['bgl']) + float(data['dead'])
            # convert to co2e / acre
            data['co2_acre'] = (0.404685 * carbon) * 3.66667

            # need to include variant?
            data.update(info)
            carbon_rows.append(data)

    ############# Extract Summary Statistics
    ready = False
    countdown = None
    data = None
    with open(outfile, 'r') as fh:
        for line in fh:
            if "SUMMARY STATISTICS (PER ACRE OR STAND BASED ON TOTAL STAND AREA)" in line:
                # We've found the summary stats, data starts 7 lines down
                ready = True
                countdown = 7

            if not ready or countdown > 0:
                if countdown:
                    countdown -= 1
                continue

            if line.strip() == "":
                # blank line == we're done
                break

            # Got it: this is a data line
            """
            'year', 'age', 'num_trees', 'ba', 'sdi', 'ccf', 'top_ht', 'qmd', 'total_ft3',
            'merch_ft3', 'merch_bdft', 'cut_trees', 'cut_total_ft3', 'cut_merch_ft3', 
            'cut_merch_bdft', 'after_ba', 'after_sdi', 'after_ccf', 'after_ht', 'after_qmd',
            'growth_yrs', 'growth_accreper', 'growth_mortyear', 'mai_merch_ft3', 'for_ss_typ_zt'
            """
            fixed_schema = [
                ('year', 1, 4, 'int'),
                ('age', 5, 8, 'int'),
                ('num_trees', 9, 14, 'int'),
                ('ba', 15, 18, 'int'),
                ('total_ft3', 37, 42, 'int'),
                ('merch_ft3', 43, 48, 'int'),
                ('merch_ft3_removed', 67, 72, 'int'),
            ]
            data = split_fixed(line.strip(), fixed_schema)

            data.update(info)
            summary_rows.append(data)

    ############# Extract Activity Summary
    looking_for = ['FIREHZD', 'NSONESTN', 'BAAGE1']
    ready = False
    countdown = None
    within_year = None
    data = {}
    with open(outfile, 'r') as fh:
        for line in fh:
            if "ACTIVITY SUMMARY" in line:
                # We've found the summary stats, data starts x lines down
                ready = True
                countdown = 9

            if not ready or countdown > 0:
                if countdown:
                    countdown -= 1
                continue

            if line.strip() == "":
                # blank line == we're done with this TIME PERIOD
                within_year = None
                activity_rows.append(data)
                data = {}
                continue

            if line.startswith("-----"):
                activity_rows.append(data)
                break

            # This is the start of a time period
            if not within_year:
                within_year = int(line[7:11])
                data['year'] = within_year
                data.update(info)
            else:
                var = line[24:34].strip()
                if var in looking_for:
                    val = float(line[63:72])
                    data[var] = val


if __name__ == "__main__":
    args = docopt(__doc__, version='1.0')
    indir = os.path.abspath(args['DIR'])

    for outfile in glob.glob(os.path.join(indir, "*.out")):
        extract_data(outfile)

    # TODO no globals, load into pandas dataframes, join, write to a csv
    # uid = (info['var'], info['rx'], info['cond'], info['site'], info['offset'], 'YEAR TBD')
    #print json.dumps(carbon_rows[0], indent=2)
    #print json.dumps(summary_rows[0], indent=2)
    from pandas import DataFrame, merge
    activity_df = DataFrame(activity_rows)
    summary_df = DataFrame(summary_rows)
    carbon_df = DataFrame(carbon_rows)
    ac_merge = merge(activity_df, carbon_df, how='outer', 
                     on=['var', 'rx', 'cond', 'site','offset', 'year'])
    acs_merge = merge(ac_merge, summary_df, how="outer",
                      on=['var', 'rx', 'cond', 'site','offset', 'year'])

    acs_merge.to_csv("test.csv")
