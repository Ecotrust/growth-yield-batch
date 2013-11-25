#!/usr/bin/env python
import pyodbc
import os
from shutil import copyfile

db = r"G:\projects\projects2011\LandOwnerTools\data\IDB_for_FVS\climate_lookup.accdb"
BASEOUTDIR = os.path.abspath(r"output")
INDIR = r"G:\projects\projects2011\LandOwnerTools\data\IDB_for_FVS\cond"


conn = pyodbc.connect("Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s;" % db)
cursor = conn.cursor()

sql = """
SELECT *
FROM CondForProject
"""
cursor.execute(sql)
project = []
for row in cursor:
    project.append({
        'var': row.Variant,
        'cond': int(row.COND_ID),
        'site': row.SiteClass 
    })

# New cursor necessary? 
del cursor
cursor = conn.cursor()

header = """StandID,Scenario,Year,mat,map,gsp,mtcm,mmin,mtwm,mmax,sday,ffp,dd5,gsdd5,d100,dd0,smrpb,smrsprpb,sprp,smrp,winp,ABAM,ABCO,ABGR,ABLA,ABLAA,ABMA,ABPR,ABSH,ACGL,ACGR3,ACMA3,AECA,ALRH2,ALRU2,ARME,BEPA,BEPAC,CADE27,CELE3,CHCH7,CHLA,CHNO,CONU4,FRLA,JUCO11,JUDE2,JUMO,JUOC,JUOS,JUSC2,LALY,LAOC,LIDE3,OLTE,PIAL,PIAR,PIAT,PIBR,PICO,PICO3,PIED,PIEN,PIFL2,PIJE,PILA,PILO,PIMO,PIMO3,PIPO,PIPU,PISI,PIST3,PODEM,POTR5,PROSO,PRUNU,PSME,QUAG,QUCH2,QUDO,QUEM,QUGA,QUGA4,QUHY,QUKE,QULO,QUOB,QUWI2,RONE,SALIX,SEGI2,TABR2,THPL,TSHE,TSME,UMCA,pSite,DEmtwm,DEmtcm,DEdd5,DEsdi,DEdd0,DEpdd5"""

for vcs in project:
    print "-----"
    print vcs
    sql = """
    SELECT *
    FROM ClimateByCond
    WHERE StandID = %s
    """ % vcs['cond']

    # make variant directory if not done
    outdir = os.path.join(BASEOUTDIR, vcs['var'], 'cond')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # write cli
    cursor.execute(sql)
    with open(os.path.join(outdir, "%d.cli" % vcs['cond']),'w') as fh:
        fh.write(header)
        fh.write("\n")
        for row in cursor:
            fh.write(",".join([str(x) for x in row[1:]])) # dont include 1st col (access pk)
            fh.write("\n")

    # write .site
    with open(os.path.join(outdir, "%d.site" % vcs['cond']),'w') as fh:
        fh.write(str(vcs['site']))
        fh.write("\n")

    # copy fvs
    copyfile(
        os.path.join(INDIR, vcs['var'].upper(), "fvs", "%d.fvs" % vcs['cond']), 
        os.path.join(outdir, "%d.fvs" % vcs['cond']), 
    )
    copyfile(
        os.path.join(INDIR, vcs['var'].upper(), "fvs", "%d.std" % vcs['cond']), 
        os.path.join(outdir, "%d.std" % vcs['cond']), 
    )

