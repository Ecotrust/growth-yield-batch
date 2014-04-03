#!/usr/bin/env python
'''
See GDoc "Prepare GYB"
This data-prep script MUST be modified for the needs of each project

Requires stands, treeslist and climate tables
'''
import os
import sqlite3
import json
import glob
import sys

class GYBError(Exception):
    pass

TF = [
    # See "G:\projects\projects2011\LandOwnerTools\util\scripts\FVS TREEFMT Details.xlsx"
    #("Name", "Column", "fvsformat", "valtype", "valwidth", "cumulative", "valdec")

    ("Plot ID", None, "I6", "int", 6, 6, None), 
    ("Tree Number", "TreeID", "I3", "int", 3, 9, None), 
    ("Tree Count", "TPA", "F6.0", "float", 6, 15, 0), 
    ("Tree History", "TreeHist", "I1", "int", 1, 16, None), 
    ("Species", "{{variant}}_Spp", "A3", "str", 3, 19, None), 
    ("Diameter at Breast Height", "DBH", "F5.1", "float", 5, 24, 1), 
    ("DBH Increment", "Diam_Inc", "F3.1", "float", 3, 27, 1), 
    ("Live Height", "HT_ft", "F3.0", "float", 3, 30, 0), 
    ("Height to Top Kill", "HT_kill", "F3.0", "float", 3, 33, 0), 
    ("Height Increment", "HT_Inc", "F4.1", "float", 4, 37, 1), 
    ("Crown Ratio Code", "Crown", "I1", "int", 1, 38, None), 
    ("Damage Code 1", "Dmg1", "I2", "int", 2, 40, None), 
    ("Severity Code 1", "Sev1", "I2", "int", 2, 42, None), 
    ("Damage Code 2", "Dmg2", "I2", "int", 2, 44, None), 
    ("Severity Code 2", "Sev2", "I2", "int", 2, 46, None), 
    ("Damage Code 3", "Dmg3", "I2", "int", 2, 48, None), 
    ("Severity Code 3", "Sev3", "I2", "int", 2, 50, None), 
    ("Tree Value Class Code", "TreeValue", "I1", "int", 1, 51, None), 
    ("Cut/Leave Prescription Code", "RxREC", "I1", "int", 1, 52, None), 
    ("Plot slope percent ", None, "I2", "int", 2, 54, None), 
    ("Plot aspect in degrees", None, "I3", "int", 3, 57, None), 
    ("Plot habitat type code", None, "I3", "int", 3, 60, None), 
    ("Plot topographic position code", None, "I1", "int", 1, 61, None), 
    ("Plot site preparation code", None, "I1", "int", 1, 62, None), 
    ("Tree Age", "Tree_Age", "F3.0", "float", 3, 65, 0), 
]

# these are built into build_keys.py, no need to specify
# unless you want to override them
default_site_classes = {  
      "1": "SiteCode          DF       148         1",
      "2": "SiteCode          DF       125         1",
      "3": "SiteCode          DF       105         1",
      "4": "SiteCode          DF        85         1",
      "5": "SiteCode          DF        62         1"}

SITE_CLASSES =  {
    # "PN": default_site_classes,
    # "SO": default_site_classes,
    # "CA": default_site_classes,
    # "NC": default_site_classes,
    # "EC": default_site_classes,
    # "BM": default_site_classes,
    "WC": {
      "1": "SiteCode          DF       200         1",
      "2": "SiteCode          DF       170         1",
      "3": "SiteCode          DF       140         1",
      "4": "SiteCode          DF       110         1",
      "5": "SiteCode          DF        80         1"
    }
}

def make_fvsfile(stand, outdir, con, variant):
    # query treelist.db for the condid
    # construct lines and write to file
    # make sure you've got an index on the standid column
    #  CREATE INDEX gnn_fcid_idx ON treelive(GNN_FCID);


    standid = stand['standid']
    fcid = stand['gnnfcid']
    path = os.path.join(outdir, "%d.fvs" % standid)

    cols = [x[1].replace("{{variant}}", variant) for x in TF if x[1] is not None]

    with open(path, 'w') as fh:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        sql = """SELECT %s
                 FROM treelist
                 WHERE GNN_FCID = %d;""" % (', '.join(cols), fcid)

        for i, row in enumerate(cur.execute(sql)):
            #line = " ".join([str(x) for x in row])
            line = ''
            for item in TF:
                col = item[1]
                if col is not None:
                    col = str(col.replace("{{variant}}", variant))

                valtype = item[3]
                valwidth = item[4]
                dec = item[6]

                if item[0] == "Plot ID": # special case
                    val = standid
                elif col is None:
                    val = ''
                    valtype = 'str'
                else:
                    val = row[col]

                if valtype == "str":
                    # assert len(val.strip()) <= valwidth, (col, val, valwidth)
                    pass
                elif valtype == "int":
                    # special case, convert pct to crown code
                    if col == "Crown":
                        try:
                            val = int(val)
                            val = 1 + int( (val - 1) / 10)
                            if val > 9:
                                val = 9
                        except ValueError:
                            val = ''

                    if val != '':
                        val = str(int(val))
                        if col == "TreeID":  # special case, just use autonum
                            val = str(i)
                        # assert len(val.strip()) <= valwidth, (col, val, valwidth)
                elif valtype == "float":
                    if val != '':
                        val = float(val)
                        mult = 10 ** dec
                        val = val * mult
                        val = str(int(round(val)))
                        # assert len(val.strip()) <= valwidth, (col, val, valwidth)

                fmt = '{0: >%d}' % valwidth
                fval = fmt.format(val)

                if len(fval) > valwidth:
                    if col == 'Tree_Age':
                        # special case, tree age >= 1000 gets assigned to 999
                        print "WARNING: Tree Age is '%s', setting to 999" % (val, )
                        val = '999'
                        fval = '999'
                    else:
                        print "WARNING: %s is '%s' should only be %d wide!!" % (col,
                            val, valwidth)
                line += fval[-1 * valwidth:]  # Just take the trailing chars 
            #print line
            fh.write(line)
            fh.write("\n")


def make_stdinfofile(stand, outdir, con):
    '''
    field 1: Numeric Region and National Forest code where stand is located.
    RFF where R = region, FF = 2-digit forest code
    (NOTE: this is misleading! see fvs variant overviews)
     
    field 2: Stand habitat type code or plant community code (ecological unit code in SN.) 
     
    field 3: Stand age in years. 
     
    field 4: Stand aspect in degrees (0 or 360 = north). 
     
    field 5: Stand slope percent. 
     
    field 6: Stand elevation in 100s of feet (10s of feet in AK variant). For example, a 
    code of 52 would mean elevation is 5200 feet (520 feet in AK). 
     
    field 7: Stand Latitude in degrees.
    '''
    # 1, 4, 5, 6, 7 from shapefile; field names = ['location', 'aspect', 'slope', 'elev', 'lat']


    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # 2 (habitat code) is hard to determine.
    #    (may be able to construct via GNN stand-level forest types?)
    #    It drives site tree/index and max density but we override the first two anyways
    #    LEAVE BLANK AND USE DEFUALT FOR NOW - ie accept the default max stand density 

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    standid = stand['standid']
    fcid = stand['gnnfcid']
    path = os.path.join(outdir, "%d.std" % standid)

    variant = stand['variant']

    default_habitat = {
        'PN': '40', # CHS133
        'WC': '52', # CFS551
        'NC': 'CWC221', # 
        'CA': '46', #  CWC221
        'SO': '49', #  CPS111
        'EC': '114'
    }
    habitat = default_habitat.get(variant.upper(), "")

    cur = con.cursor()
    sql = """SELECT TPA, DBH, HT_ft, Tree_Age
             FROM treelist
             WHERE GNN_FCID = %d
             AND TreeHist = 1;""" % (fcid, )

    treedata = list(cur.execute(sql))
    if len(treedata) == 0:
        warn = "WARNING, no treelist data for standid %s, fcid %s (skipping)" % (standid, fcid)
        raise GYBError(warn)
        return

    # TODO age_dom or age_dom_no_rem ?? 
    sql = """SELECT AGE_DOM_NO_REM as age, SDI_REINEKE, QMDA_DOM, HCB, OGSI
             FROM SPPSZ_ATTR_ALL
             WHERE FCID = %d;""" % (fcid, )
    data = list(cur.execute(sql))
    age = float(data[0]['age'])

    if age == 0:
        """
        GNN AGE has failed us, try to apply a simple linear regression to guess age
        Using the 3994 FCIDs on BLM property that had a valid age
        predict AGE_DOM_NO_REM using AGE_DOM_NO_REM ~ SDI_REINEKE + QMDA_DOM + HCB + OGSI - 1

        SDI_REINEKE    0.038342
        QMDA_DOM       1.257999
        HCB           -2.183154
        OGSI           1.213396

                                    OLS Regression Results                            
        ==============================================================================
        Dep. Variable:         AGE_DOM_NO_REM   R-squared:                       0.853
        Model:                            OLS   Adj. R-squared:                  0.853
        Method:                 Least Squares   F-statistic:                     6303.
        Date:                Mon, 17 Feb 2014   Prob (F-statistic):               0.00
        Time:                        08:53:24   Log-Likelihood:                -22160.
        No. Observations:                4355   AIC:                         4.433e+04
        Df Residuals:                    4351   BIC:                         4.435e+04
        Df Model:                           4                                         
        ===============================================================================
                          coef    std err          t      P>|t|      [95.0% Conf. Int.]
        -------------------------------------------------------------------------------
        SDI_REINEKE     0.0383      0.004      8.696      0.000         0.030     0.047
        QMDA_DOM        1.2580      0.045     27.694      0.000         1.169     1.347
        HCB            -2.1832      0.138    -15.858      0.000        -2.453    -1.913
        OGSI            1.2134      0.050     24.180      0.000         1.115     1.312
        ==============================================================================
        Omnibus:                     1047.808   Durbin-Watson:                   1.752
        Prob(Omnibus):                  0.000   Jarque-Bera (JB):             6835.787
        Skew:                           0.984   Prob(JB):                         0.00
        Kurtosis:                       8.813   Cond. No.                         78.1
        ==============================================================================
        """
        # apply regression coefficients, no intercept
        try:
            age = (float(data[0]['SDI_REINEKE']) * 0.038342) + \
              (float(data[0]['QMDA_DOM']) * 1.257999) + \
              (float(data[0]['HCB']) * -2.183154) + \
              (float(data[0]['OGSI']) * 1.213396)
        except:
            import ipdb; ipdb.set_trace()

        if age < 0:
            age = 0


    with open(path, 'w') as fh:
        line = concat_fvs_line("STDINFO", [
            stand['location'],
            habitat,
            int(age),
            int(stand['aspect']),
            int(stand['slope']),
            int(round(stand['elev'] / 100.0)),  # elev assumed to be in ft, FVS expects ft/100
            int(stand['lat']),
        ])

        fh.write(line)
        fh.write("\n")


def concat_fvs_line(keyword, fields):
    col = "%10s"
    line = "{0:<10}".format(keyword.upper(), )
    for field in fields:
        line += col % field
    return line


def make_climatefile(stand, outdir, con):
    # query climate.db
    # write to .cli
    # return available climates
    # make sure you've got an index on the standid column
    #  CREATE INDEX stand_idx ON fvsclimattrs(StandID);

    standid = stand['standid']
    #fcid = stand['gnnfcid']
    path = os.path.join(outdir, "%d.cli" % standid)

    con.row_factory = None
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    columns_query = "PRAGMA table_info(climate)"
    cur.execute(columns_query)
    header = ','.join([x['name'] for x in cur.fetchall()])

    with open(path, 'w') as fh:
        fh.write(header)
        fh.write("\n")

        sql = """SELECT %s
                 FROM climate
                 WHERE StandID = %d;""" % (header, standid)

        i = None
        noclim = None
        for i, row in enumerate(cur.execute(sql)):
            if row['Year'] == 1990 and row['Scenario'] == "Ensemble_rcp60":
                # grab the line for NoClimate
                noclim = list(row)
            fh.write(",".join([str(x) for x in row]))
            fh.write("\n")

        if not i:
            warn = "WARNING, Climate data missing for standid %s (skipping)" % standid
            raise GYBError(warn)

        if not noclim:
            warn = "WARNING, Could not find the 1990 ensemble rcp60 scenario to use as NoClimate %s (skipping)" % standid
            raise GYBError(warn)

        # write noclim
        noclim[1] = "NoClimate"
        for year in [1990, 2030, 2060, 2090]:
            noclim[2] = year
            fh.write(",".join([str(x) for x in noclim]))
            fh.write("\n")



    con.row_factory = sqlite3.Row


def make_sitefile(stand, outdir):
    # read site from stand and write number to file
    # return site indecies
    standid = stand['standid']
    path = os.path.join(outdir, "%d.site" % standid)
    with open(path, 'w') as fh:
        fh.write(str(stand['sitecls']))
        fh.write("\n")


def make_rxfile(stand, outdir):
    # read variant and rxs from stand
    # write to file in csv format, no header. return them
    standid = stand['standid']
    variant = stand['variant']
    rxtxt = stand['rx']
    if rxtxt:
        rxs = [int(x) for x in rxtxt.strip().split(",")]
    else:
        rxs = ["*"]

    path = os.path.join(outdir, "%d.rx" % standid)
    with open(path, 'w') as fh:
        for rx in rxs:
            fh.write("%s,%s" % (variant, rx))
            fh.write("\n")

    return variant, rxs


def get_climates(con):
    # connect to climatedb and find all unique climate names
    cur = con.cursor()
    sql = """SELECT DISTINCT Scenario FROM climate"""
    scenarios = [x[0] for x in cur.execute(sql)]
    return scenarios


def stand_iter(batch, con):
    # import shapefile
    # sf = shapefile.Reader(shp)
    # fields = [x[0] for x in sf.fields[1:]]
    # for record in sf.iterRecords():
    #     dd = dict(zip(fields, record))
    #     yield dd      
    cur = con.cursor()
    sql = """SELECT * FROM stands WHERE batch='%s'""" % batch  #TODO unsafe 
    for i, row in enumerate(cur.execute(sql)):
        yield dict(zip(row.keys(), row))  


def write_config(con, outdir):
    # write config.json 
    # default to 0, 5, 10, 15 offsets
    clims = get_climates(con)
    clims.append("NoClimate")
    data = {
      "climate_scenarios": clims,
      "site_classes": SITE_CLASSES,
      "offsets": [0, 10]
    }
    with open(os.path.join(outdir, 'config.json'), 'w') as fh:
        fh.write(json.dumps(data, indent=2))



#------------------------------------------------------------------------------#


def main(batch):
    print "Starting to prepare GYB batch (%s)" % batch

    outdir = "./%s/cond" % batch
    if os.path.exists(outdir):
        import shutil
        shutil.rmtree(outdir)
    os.makedirs(outdir)
    print "Writing to %s" % outdir

    conn = sqlite3.connect('/home/mperry/projects/BLM_climate/Batch1/master.sqlite')
    conn.row_factory = sqlite3.Row

    for stand in stand_iter(batch, conn):
        try:
            make_climatefile(stand, outdir, conn)
            make_stdinfofile(stand, outdir, conn)
            make_sitefile(stand, outdir)
            variant, _ = make_rxfile(stand, outdir)
            make_fvsfile(stand, outdir, conn, variant)
            # print "\t", stand['standid'], "complete"
        except GYBError as exc:
            print "\t", exc.message
            # clean up and just skip it
            for path in glob.glob(os.path.join(outdir, "%s*" % stand['standid'])):
                os.remove(path)

    print "Writing config"
    write_config(conn, os.path.join(outdir, '..'))
    print "DONE"


batch = sys.argv[1]
main(batch)
