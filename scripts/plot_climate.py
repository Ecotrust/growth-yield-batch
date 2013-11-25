#!/bin/env python
import sqlite3
from collections import defaultdict
import matplotlib.pyplot as plt

def plot_climate(cond, rx, ext=""):
    con = sqlite3.connect("data%s.db" % ext)
    cur = con.cursor()
    
    sql = """
        SELECT climate, year, after_merch_bdft
        FROM trees_fvsaggregate
        WHERE cond = %s
        AND rx = %s
        AND offset = 0
        ORDER BY climate, year
    """ % (cond, rx)
    
    # Assume there are no gaps in years
    climdata = defaultdict(list)
    years = []
    res = cur.execute(sql)
    for row in res:
        climdata[row[0]].append(row[2])
        years.append(row[1])
    years = sorted(list(set(years)))
    
    fig, ax = plt.subplots(figsize=(14,7))

    for climate in sorted(climdata.keys()):
        data = climdata[climate]
        if climate == "NoClimate":
            climate = climate + "-na"
        circ, emm = climate.split("-")
    
        emmision_colors = {
            'rcp45': 'green',
            'rcp60': 'yellow',
            'rcp85': 'blue',
            'na': 'black'
        }
        
        dashes = {
            'CCSM4': [5, 10, 15, 10],
            'Ensemble': [8, 2, 2, 4, 2, 4] ,
            'GFDLCM3': [3, 10, 3, 10],
            'HadGEM2ES': [2, 2],
            'NoClimate': None,
        }
    
        line, = ax.plot(years, data, color=emmision_colors[emm], label=climate, lw=2.5)
        if dashes[circ]:
            line.set_dashes(dashes[circ])
    
    ax.spines['right'].set_color("none")
    ax.spines['top'].set_color("none")
    ax.yaxis.tick_left() # only ticks on the left side
    ax.xaxis.tick_bottom() # only ticks on the left side
    
    #ax.set_autoscaley_on(False)
    #ax.set_ylim([0,40000])
    
    ax.grid(True)
    ax.set_xlabel('Year', fontsize=18)
    ax.set_ylabel('Merchantable Board Feet', fontsize=18)
    ax.set_title('Condition %s, Rx %s Climate Scenarios' % (cond, rx), fontsize=18)
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)# upper left corner
    return fig

plot_climate(31566, 0).show()
plot_climate(31566, 5).show()
plot_climate(31566, 10).show()

import ipdb; ipdb.set_trace()