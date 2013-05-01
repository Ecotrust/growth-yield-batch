#!/usr/bin/env python
"""extract.py

Extract variables from directories with FVS runs with offset plots; uses fvs .out files

Usage:
  extract.py INDIR OUTCSV
  extract.py (-h | --help)
  extract.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt
from pandas import DataFrame, merge
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


def classify_tree(spz, diam):
    diam_class = int(diam / 10.0)
    return "%s_%s" % (spz, diam_class)


def split_fixed(line, fixed_schema):
    funcs = {'int': int, 'float': float, 'str': str}
    data = {}
    for var in fixed_schema:
        data[var[0]] = funcs[var[3]](line[var[1]-1:var[2]])
    return data


def extract_data(indir):

    carbon_rows = []
    harvested_carbon_rows = []
    summary_rows = []
    activity_rows = []

    for outfile in glob.glob(os.path.join(indir, "*.out")):

        info = parse_name(outfile)

        ############# Extract Stand Carbon Report
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
                    ('total_stand_carbon', 77, 85, 'float'),
                ]
                data = split_fixed(line.strip(), fixed_schema)

                # calculate our own carbon
                carbon = float(data['agl']) + float(data['bgl']) + float(data['dead'])
                data['calc_carbon'] = carbon

                # need to include variant?
                data.update(info)
                carbon_rows.append(data)

        ############# Extract Harvested Carbon Report
        ready = False
        countdown = None
        with open(outfile, 'r') as fh:
            for line in fh:
                if "HARVESTED PRODUCTS REPORT" in line and not line.startswith("CARBCUT"):
                    # We've found the harvested products carbon report, data starts 9 lines down
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
                fixed_schema = [
                    ('year', 1, 4, 'int'),
                    ('merch_carbon_stored', 41, 49, 'float'),
                    ('merch_carbon_removed', 50, 58, 'float'),
                ]
                data = split_fixed(line.strip(), fixed_schema)

                # need to include variant?
                data.update(info)
                harvested_carbon_rows.append(data)

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
                    ('start_tpa', 9, 14, 'int'),
                    ('start_ba', 15, 18, 'int'),
                    ('start_total_ft3', 37, 42, 'int'),
                    ('start_merch_ft3', 43, 48, 'int'),
                    ('start_merch_bdft', 49, 54, 'int'),
                    ('removed_tpa', 56, 60, 'int'),
                    ('removed_total_ft3', 61, 66, 'int'),
                    ('removed_merch_ft3', 67, 72, 'int'),
                    ('removed_merch_bdft', 73, 78, 'int'),
                    ('after_ba', 79, 82, 'int'),
                ]
                data = split_fixed(line.strip(), fixed_schema)

                data['after_tpa'] = data['start_tpa'] - data['removed_tpa']
                data['after_total_ft3'] = data['start_total_ft3'] - data['removed_total_ft3']
                data['after_merch_ft3'] = data['start_merch_ft3'] - data['removed_merch_ft3']
                data['after_merch_bdft'] = data['start_merch_bdft'] - data['removed_merch_bdft']

                data.update(info)
                summary_rows.append(data)

        ############# Extract Activity Summary
        """
        NSONEST             spotted owl nesting suitability
        NSOFRG               spotted owl foraging suitability
        NSODIS                spotted owl dispersal suitability
        PP_BTL                                 mountain pine beetle hazard rating for ponderosa pine
        LP_BTL                  mountain pine beetle hazard rating for lodgepole pine
        ES_BTL                  spruce beetle hazard rating for Englemann spruce
        FIREHZD               wildfire hazard rating
        DDI                 diameter diversity index
        """
        looking_for = [
            "NSONEST",
            "NSOFRG",
            "NSODIS",
            "PP_BTL",
            "LP_BTL",
            "ES_BTL",
            "FIREHZD",
            "DDI",
        ]

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

        ############# Extract Treelist info
        ## TODO: There might be a way to accomplish this WITHOUT parsing the treelists
        ## using compute variables and defining merchantable timber
        #
        # data = None
        # ready = False
        # with open(outfile.replace(".out", ".trl"), 'r') as fh:
        #     for line in fh:
        #         if line[:4] == "-999":
        #             # We've found a summary stats header
        #             """
        #             column 81 has a T, C, D, or A code:
        #             T = Live trees at beginning of current cycle/end of previous cycle
        #             D = Dead trees at beginning of current cycle/end of previous cycle
        #             C = Trees cut during this cycle
        #             A = Live trees following cutting in current cycle but prior to growth modeling in current cycle
        #             """
        #             import json
        #             # save previous section data
        #             if data:
        #                 print json.dumps(data, indent=2, sort_keys=True)

        #             # start new section
        #             code = line[80]
        #             year = line[15:19]
        #             data = None

        #             # We only want cut lists for now
        #             if code == "C":
        #                 ready = True
        #             else:
        #                 ready = False
        #                 continue

        #             data = {'year': year, 'code': code}
        #             data.update(info)

        #         elif ready:
        #             # we're reading data points within the section
        #             spz = line[14:16]
        #             diam = float(line[47:53])
        #             treeclass = classify_tree(spz, diam)

        #             #tpa = float(line[30:38])
        #             #dead_tpa = float(line[40:47])
        #             #merch_ft3 = float(line[101:108])
        #             #merch_bdft = float(line[108:116])
        #             total_ft3 = float(line[94:101])

        #             # TODO class by diameter/spz category
        #             # TODO aggregate by class
        #             key_tmpl = treeclass + "_cut_total_ft3"
        #             if key_tmpl in data.keys():
        #                 data[key_tmpl] += int(total_ft3)
        #             else:
        #                 data[key_tmpl] = int(total_ft3)

    # load into pandas dataframes, join
    activity_df = DataFrame(activity_rows)
    summary_df = DataFrame(summary_rows)
    carbon_df = DataFrame(carbon_rows)
    harvested_carbon_df = DataFrame(harvested_carbon_rows)
    c_merge = merge(carbon_df, harvested_carbon_df, how='outer', 
                     on=['var', 'rx', 'cond', 'site','offset', 'year'])
    ac_merge = merge(c_merge, activity_df, how='outer', 
                     on=['var', 'rx', 'cond', 'site','offset', 'year'])
    acs_merge = merge(ac_merge, summary_df, how="outer",
                      on=['var', 'rx', 'cond', 'site','offset', 'year'])

    return acs_merge


if __name__ == "__main__":
    args = docopt(__doc__, version='1.0')
    indir = os.path.abspath(args['INDIR'])
    csv = os.path.abspath(args['OUTCSV'])

    df = extract_data(indir)
    df.to_csv(csv)
