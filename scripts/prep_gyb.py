#!/usr/bin/env python
'''
See GDoc "Prepare GYB"

Requires stands.shp + treeslist.db + climate.db
'''
import os
import sqlite3
import json
import glob


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

def make_fvsfile(stand, outdir, treelistdb, variant):
    # query treelist.db for the condid
    # construct lines and write to file
    # make sure you've got an index on the standid column
    #  CREATE INDEX gnn_fcid_idx ON treelive(GNN_FCID);


    standid = stand['standid']
    fcid = stand['gnnfcid']
    path = os.path.join(outdir, "%d.fvs" % standid)

    cols = [x[1].replace("{{variant}}", variant) for x in TF if x[1] is not None]

    with open(path, 'w') as fh:
        with sqlite3.connect(treelistdb[0]) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            sql = """SELECT %s
                     FROM %s
                     WHERE GNN_FCID = %d;""" % (', '.join(cols), treelistdb[1], fcid)

            for i, row in enumerate(cur.execute(sql)):
                #line = " ".join([str(x) for x in row])
                line = ''
                for item in TF:
                    col = item[1]
                    if col is not None:
                        col = col.replace("{{variant}}", variant)
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
                        # special case, convert to code !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
                        # THIS SHOULD BE DONE IN THE ACCESS DB QUERY
                        if col == "Crown":
                            val = 1 + int( (val-1) / 10)
                            if val > 9:
                                val = 9

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
                        print "WARNING: %s is '%s' should only be %d wide!!" % (col,
                            val, valwidth)
                    line += fval[-1 * valwidth:]  # Just take the trailing chars 
                #print line
                fh.write(line)
                fh.write("\n")


def make_stdinfofile(stand, outdir, treelistdb):
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

    # 2 (habitat code) is hard to determine.
    #    (may be able to construct via GNN stand-level forest types?)
    #    It drives site tree/index and max density but we override the first two anyways
    #    LEAVE BLANK AND USE DEFUALT FOR NOW - ie accept the default max stand density !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # and 3 (stand age) could be derived from the data in the treelist?
    #    for now, just do TPA-weighted average of ALL live trees?
    #    ONLY dominiant species? 
    # Should we just join with sppz_attr_all and use age_dom_no_rem? !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 

    standid = stand['standid']
    fcid = stand['gnnfcid']
    path = os.path.join(outdir, "%d.std" % standid)

    with sqlite3.connect(treelistdb[0]) as con:
        cur = con.cursor()
        sql = """SELECT TPA, Tree_Age, Tree_Age * TPA as MULT
                 FROM %s
                 WHERE GNN_FCID = %d;""" % (treelistdb[1], fcid)

        data = list(cur.execute(sql))
        if len(data) == 0:
            warn = "WARNING, no treelist data for standid %s, fcid %s (skipping)" % (standid, fcid)
            raise Exception(warn)
            return
        sumtpa = sum([d[0] for d in data])
        summult = sum([d[2] for d in data])
        age = int(summult/sumtpa)

    with open(path, 'w') as fh:
        line = concat_fvs_line("STDINFO", [
            stand['location'],
            '',
            age,
            int(stand['aspect']),
            int(stand['slope']),
            int(stand['elev']),
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


def make_climatefile(stand, outdir, climatedb):
    # query climate.db
    # write to .cli
    # return available climates
    # make sure you've got an index on the standid column
    #  CREATE INDEX stand_idx ON fvsclimattrs(StandID);

    header = "StandID,Scenario,Year,mat,map,gsp,mtcm,mmin,mtwm,mmax,sday," \
    "ffp,dd5,gsdd5,d100,dd0,smrpb,smrsprpb,sprp,smrp,winp,ABAM,ABCO,ABGR,ABLA," \
    "ABLAA,ABMA,ABPR,ABSH,ACGL,ACGR3,ACMA3,AECA,ALRH2,ALRU2,ARME,BEPA,BEPAC," \
    "CADE27,CELE3,CHCH7,CHLA,CHNO,CONU4,FRLA,JUCO11,JUDE2,JUMO,JUOC,JUOS,JUSC2," \
    "LALY,LAOC,LIDE3,OLTE,PIAL,PIAR,PIAT,PIBR,PICO,PICO3,PIED,PIEN,PIFL2,PIJE," \
    "PILA,PILO,PIMO,PIMO3,PIPO,PIPU,PISI,PIST3,PODEM,POTR5,PROSO,PRUNU,PSME,QUAG," \
    "QUCH2,QUDO,QUEM,QUGA,QUGA4,QUHY,QUKE,QULO,QUOB,QUWI2,RONE,SALIX,SEGI2,TABR2," \
    "THPL,TSHE,TSME,UMCA,pSite,DEmtwm,DEmtcm,DEdd5,DEsdi,DEdd0,DEpdd5"

    standid = orig_standid = stand['standid']
    #fcid = stand['gnnfcid']
    path = os.path.join(outdir, "%d.cli" % standid)

    with open(path, 'w') as fh:
        fh.write(header)
        fh.write("\n")
        with sqlite3.connect(climatedb[0]) as con:
            #con.row_factory = sqlite3.Row
            cur = con.cursor()

            # TODO until we get the new fvs climate data associated with standids
            # grab a random id  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            import random
            standid = random.choice([1, 7, 10])

            sql = """SELECT %s
                     FROM %s
                     WHERE StandID = %d;""" % (header, climatedb[1], standid)
            for i, row in enumerate(cur.execute(sql)):
                # TODO when fixed ... fh.write(",".join([str(x) for x in row]))
                fh.write(",".join([str(orig_standid)] + [str(x) for x in row[1:]]))
                fh.write("\n")


def make_sitefile(stand, outdir):
    # read site from stand and write number to file
    # return site indecies
    standid = stand['standid']
    path = os.path.join(outdir, "%d.site" % standid)
    with open(path, 'w') as fh:
        fh.write(str(stand['sitecls']))
        fh.write("\n")


def get_sitecls(variant):
    #TODO more site classes and variants !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if variant in ['PN', 'WC', 'CA']:
        sitecls = {
            "2": "SiteCode          DF       125         1",
            "3": "SiteCode          DF       105         1"
        }
    return sitecls


def get_climates(climatedb):
    # connect to climatedb and find all unique climate names
    with sqlite3.connect(climatedb[0]) as con:
        cur = con.cursor()
        sql = """SELECT DISTINCT Scenario
                 FROM %s""" % (climatedb[1], )
        scenarios = [x[0] for x in cur.execute(sql)]
    return scenarios


def stand_iter(shp):
    import shapefile
    sf = shapefile.Reader(shp)
    fields = [x[0] for x in sf.fields[1:]]
    for record in sf.iterRecords():
        dd = dict(zip(fields, record))
        yield dd      


def write_config(variant, climatedb, outdir):
    # write config.json 
    # default to 0, 5, 10, 15 offsets
    sitecls = get_sitecls(variant)
    clims = get_climates(climatedb)
    data = {
      "climate_scenarios": clims,
      "sites": sitecls,
      "offsets": [0, 5, 10, 15]
    }
    with open(os.path.join(outdir, 'config.json'), 'w') as fh:
        fh.write(json.dumps(data, indent=2))



#------------------------------------------------------------------------------#


def main(variant, shp='stands_aea_join.shp'):
    treelistdb = ('treelist.db', 'treelive')
    climatedb = ('sample.db', 'fvsclimattrs')
    #climatedb = ('climate.db', 'fvsclimattrs')

    outdir = "./output"
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for stand in stand_iter(shp):
        try:
            make_climatefile(stand, outdir, climatedb)
            make_fvsfile(stand, outdir, treelistdb, variant)
            make_stdinfofile(stand, outdir, treelistdb)
            make_sitefile(stand, outdir)
        except Exception as exc:
            print exc.message
            # clean up
            for path in glob.glob(os.path.join(outdir, "%s*" % stand['standid'])):
                os.remove(path)

    write_config(variant, climatedb, outdir)

main('PN')
