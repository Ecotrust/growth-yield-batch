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
    >>> parse_name("/path/to/some/varWC_rx25_cond31566_site3_climNoClimate_off20.key")
    >>> parse_name("varWC_rx25_cond31566_site3_climNoClimate_off20.key")
    >>> parse_name("varWC_rx25_cond31566_site3_climNoClimate_off20")

    {'var': 'WC', 'cond': '31566', 'rx': '25', 'site': '3', 'offset': '20', 'climate': 'NoClimate'}
    """
    basename = os.path.splitext(os.path.basename(filename))[0]
    exp = re.compile("var([a-zA-Z]+)_rx([0-9a-zA-Z]+)_cond([0-9a-zA-Z]+)_site([0-9a-zA-Z]+)_clim([0-9a-zA-Z-]+)_off([0-9]+)")
    parts = exp.match(basename).groups()
    conv_parts = []
    for part in parts:
        try:
            part = int(part)
        except ValueError:
            part = str(part)
        conv_parts.append(part)

    keys = ("var", "rx", "cond", "site", "climate", "offset")
    return dict(zip(keys, conv_parts))


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
    econ_rows = []
    summary_rows = []
    activity_rows = []

    for outfile in glob.glob(os.path.join(indir, "*.out")):

        info = parse_name(outfile)

        ############# Extract Stand Carbon Report
        ready = False
        countdown = None

        with open(outfile, 'r') as fh:
            lines = fh.readlines()

        for line in lines:
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
        for line in lines:
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

        ############# Extract ECONOMIC ANALYSIS SUMMARY REPORT 
        ready = False
        countdown = None
        for line in lines:
            if line.startswith("ECONOMIC ANALYSIS SUMMARY REPORT"):
                # We've found the econ summary report, data starts 6 lines down
                ready = True
                countdown = 6

            if not ready or countdown > 0:
                if countdown:
                    countdown -= 1
                continue

            if line.strip() == "":
                # blank line == we're done
                break

            # Got it: this is a data line
            fixed_schema = [
                ('year', 1, 5, 'int'),
                ('undiscounted_revenue', 29, 37, 'int'),  # TODO Check all these once DD gets econ reporting in place
                ('econ_removed_merch_ft3', 101, 107, 'int'),
                ('econ_removed_merch_bdft', 108, 114, 'int'),
            ]
            data = split_fixed(line.strip(), fixed_schema)

            # need to include variant?
            data.update(info)
            econ_rows.append(data)

        ############# Extract HARVEST VOLUME AND GROSS VALUE REPORT
        ready = False
        countdown = None
        blanks = 0
        for line in lines:
            if line.startswith("HARVEST VOLUME AND GROSS VALUE REPORT"):
                # We've found the econ summary report, data starts 6 lines down
                ready = True
                countdown = 2

            if not ready or countdown > 0:
                if countdown:
                    countdown -= 1
                continue

            print line.strip()
            if line.strip() == "":
                # 3 blank lines == we're done
                blanks += 1
                if blanks == 3:
                    break

            # # Got it: this is a data line
            # fixed_schema = [
            #     ('year', 1, 5, 'int'),
            #     ('undiscounted_revenue', 29, 37, 'int'),  # TODO Check all these once DD gets econ reporting in place
            #     ('econ_removed_merch_ft3', 101, 107, 'int'),
            #     ('econ_removed_merch_bdft', 108, 114, 'int'),
            # ]
            # data = split_fixed(line.strip(), fixed_schema)

            # # need to include variant?
            # data.update(info)
            # econ_rows.append(data)

        ############# Extract Summary Statistics
        ready = False
        countdown = None
        data = None
        for line in lines:
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
                ('after_sdi', 83, 87, 'int'),
                ('after_qmd', 96, 100, 'float'),
                ('accretion', 109, 113, 'int'),
                ('mortality', 114, 119, 'int'),
                ('stand_structure', 132, 134, 'int')
            ]
            data = split_fixed(line.strip(), fixed_schema)

            data['after_tpa'] = data['start_tpa'] - data['removed_tpa']
            data['after_total_ft3'] = data['start_total_ft3'] - data['removed_total_ft3']
            data['after_merch_ft3'] = data['start_merch_ft3'] - data['removed_merch_ft3']
            data['after_merch_bdft'] = data['start_merch_bdft'] - data['removed_merch_bdft']

            data.update(info)
            summary_rows.append(data)

        ############# Extract Activity Summary
        # List of Compute Variables to look for
        looking_for = [

            # Harvest BF by species group
            "PINE_HRV",
            "SPRC_HRV",
            "CEDR_HRV",
            "DF_HRV",
            "HW_HRV",
            "MNCONHRV",
            "MNHW_HRV",
            "WJ_HRV",
            "WW_HRV",

            # Standing BF by species group
            "PINE_BF",
            "SPRC_BF",
            "CEDR_BF",
            "DF_BF",
            "HW_BF",
            "MNCONBF",
            "MNHW_BF",
            "WJ_BF",
            "WW_BF",

            # ??? Are we using these ??
            "SPPRICH",
            "SPPSIMP",

            # Cost Model
            "SM_CF",
            "SM_HW",
            "SM_TPA",
            "LG_CF",
            "LG_HW",
            "LG_TPA",
            "CH_CF",
            "CH_HW",
            "CH_TPA",
            "CUT_TYPE",
            # "PLANT" ESTAB PLANT; multiple per year though! 

            # Habitat
            "NSONEST",
            "NSOFRG",
            "NSODIS",

            # Pests
            #"PP_BTL",
            #"LP_BTL",
            "PINEBTL",
            "DF_BTL",
            "ES_BTL",
            "DEFOL",

            # Fire
            "FIREHZD",
        ]

        ready = False
        countdown = None
        within_year = None
        data = {}
        for line in lines:
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
                # initialize year with null values for all variables
                for var in looking_for:
                    data[var] = None
                # special case ESTB PLANT keyword
                data['PLANT'] = 0
            else:
                var = line[24:34].strip()
                status = line[40:59].strip()  # disregard NOT DONE or DELETED OR CANCELED
                if status.startswith("DONE IN") and var in looking_for:
                    val = float(line[61:72])  # Is this wide enough??
                    data[var] = val
                elif status.startswith("DONE IN") and var == 'PLANT':
                    # special case ESTB PLANT keyword aggregates second column
                    val = float(line[73:82])
                    data[var] += val

    # load into pandas dataframes, join
    activity_df = DataFrame(activity_rows)
    summary_df = DataFrame(summary_rows)
    carbon_df = DataFrame(carbon_rows)
    econ_df = DataFrame(econ_rows)

    harvested_carbon_df = DataFrame(harvested_carbon_rows)
    c_merge = merge(carbon_df, harvested_carbon_df, how='outer',
                    on=['var', 'rx', 'cond', 'site', 'offset', 'year', 'climate'])
    ac_merge = merge(c_merge, activity_df, how='outer',
                     on=['var', 'rx', 'cond', 'site', 'offset', 'year', 'climate'])
    acs_merge = merge(ac_merge, summary_df, how="outer",
                      on=['var', 'rx', 'cond', 'site', 'offset', 'year', 'climate'])
    final_merge = merge(acs_merge, econ_df, how="outer",
                      on=['var', 'rx', 'cond', 'site', 'offset', 'year', 'climate'])

    # manage types
    final_merge[['offset']] = final_merge[['offset']].astype(int)
    final_merge[['rx']] = final_merge[['rx']].astype(int)
    final_merge[['year']] = final_merge[['year']].astype(int)
    final_merge[['cond']] = final_merge[['cond']].astype(int)

    return final_merge


if __name__ == "__main__":
    args = docopt(__doc__, version='1.0')
    indir = os.path.abspath(args['INDIR'])
    csv = os.path.abspath(args['OUTCSV'])

    df = extract_data(indir)
    df.to_csv(csv, index=False, header=True)

    keys = [x.lower() for x in df.columns]
    vals = [x.name for x in df.dtypes]

    print "-" * 80
    print "class FVSAggregate(models.Model):"
    for colname, coltype in zip(keys, vals):
        if coltype == "float64":
            print "    %s = models.FloatField(null=True, blank=True)" % colname
        elif coltype == "int64":
            print "    %s = models.IntegerField(null=True, blank=True)" % colname
        elif coltype == "object" and colname in ['var']:
            print "    %s = models.CharField(max_length=2)" % colname
        elif coltype == "object" and colname in ['site', 'cond', 'offset', 'rx']:
            print "    %s = models.IntegerField()" % colname
        else:  # default
            print "    %s = models.FloatField(null=True, blank=True)" % colname

    print "-" * 80
    print """
            COPY trees_fvsaggregate(%s)
            FROM '%s'
            DELIMITER ',' CSV HEADER;""" % (",".join(['"%s"' % x for x in keys]), "merged_file.csv")

    print "-" * 80
    print """
            cd /usr/local/data/out

            # copy header
            sed -n 1p first.csv > merged_file.csv

            #copy all but the first line from all other files
            for i in *.csv; do sed 1d $i; done >> merged_file.csv"""

    print "-" * 80
    print """
    1. Run fvsbatch
    2. copy model defn
    3. schemamigration
    4. migrate
    5. sed merge csvs
    6. postgres copy
    7. create indicies
    """
    print
