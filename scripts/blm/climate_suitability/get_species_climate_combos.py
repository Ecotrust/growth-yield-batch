#!/bin/python

import sqlite3
import climquery

if __name__ == "__main__":
    
    # RCPS = ['rcp45', 'rcp60', 'rcp85']
    RCPS = ['rcp45', 'rcp85']
    # CLIMATES = ['CCSM4', 'Ensemble', 'GFDLCM3', 'HadGEM2ES']
    CLIMATES = ['Ensemble']
    # YEARS = ['1990', '2030', '2060', '2090']
    YEARS = ['1990', '2060']

    con = sqlite3.connect('/usr/local/apps/OR_Climate_Grid/Data/orclimgrid.sqlite')
    cur = con.cursor()

    table_query = """PRAGMA table_info(climattrs);"""

    cur.execute(table_query)
    result = cur.fetchall()

    species = []
    for col in result:
        if col[0] > 20:
            species.append(col[1])

    # import ipdb
    # ipdb.set_trace()

    #FOR TESTING
    # species = species[0:1]

    for spec in species:
        for clim in CLIMATES:
            for rcp in RCPS:
                for year in YEARS:
                    print "Querying %s %s %s %s" % (spec, clim, rcp, year)
                    climquery.the_stuff(['climquery.py', clim, rcp, year, spec, 'file'])