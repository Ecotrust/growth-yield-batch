"""
BLM Harvest Scheduler
Requires a sqlite database with a pre-processed table, fvs_stands
fvs_stands is derived from the outputs of the growth-yield-batch process and 
is created using the sql query in scripts/prep_scheduler.sql
"""
import sys
sys.path.insert(0, '/usr/local/apps/harvest-scheduler')
from scheduler.scheduler_graph import schedule
from scheduler.utils import print_results, write_stand_mgmt_csv
import sqlite3
import numpy as np
import json
 
def prep_db2(db="./master.sqlite", climate="Ensemble-rcp60", cache=None, verbose=False):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Check cache
    if cache is not None:
        try:
            stand_data = np.load('cache.array.%s.npy' % cache)
            axis_map = json.loads(open('cache.axis_map.%s.json' % climate).read())
            valid_mgmts = json.loads(open('cache.valid_mgmts.%s.json' % climate).read())
            print "Using cached data to reduce calculation time..."
            return stand_data, axis_map, valid_mgmts
        except:
            pass  # calculate it

    axis_map = {'mgmt': [], 'standids': []} 

    # Get all unique stands
    sql = "SELECT distinct(standid) FROM fvs_stands"
    for row in cursor.execute(sql):
        axis_map['standids'].append(row['standid'])

    # Get all unique mgmts
    sql = 'SELECT rx, "offset" FROM fvs_stands GROUP BY rx, "offset"'
    for row in cursor.execute(sql):
        # mgmt is a tuple of rx and offset
        axis_map['mgmt'].append((row['rx'], row['offset']))
 
    valid_mgmts = [] # 2D array holding valid mgmt ids for each stand
    
    list4D = []
    for standid in axis_map['standids']:
        if verbose:
            print standid

        temporary_mgmt_list = []
        list3D = []
        for i, mgmt in enumerate(axis_map['mgmt']):
            rx, offset = mgmt
            if verbose:
                print "\t", rx, offset

            sql = """SELECT year, timber as timber, carbon, owl, fire, cost
                from fvs_stands
                WHERE standid = '%(standid)s'
                and rx = %(rx)d
                and "offset" = %(offset)d
                and climate = '%(climate)s'; 
                -- original table MUST be ordered by standid, year
            """ % locals()

            list2D = [ map(float, [r['timber'], r['carbon'], r['owl'], 
                                   r['fire'], r['cost']]) for r in cursor.execute(sql)]
            if list2D == []:
                list2D = [[0.0, 0.0, 0.0, 0.0, 0.0]] * 20
            else:
                temporary_mgmt_list.append(i)

            ## Instead we assume that if it's in fvs_stands, we consider it
            # if stand['restricted_rxs']:
            #     if rx in stand['restricted_rxs']:
            #         temporary_mgmt_list.append(mgmt_id)
            # else:
            #     temporary_mgmt_list.append(mgmt_id)
            #assert len(list2D) == 20

            list3D.append(list2D)

        list4D.append(list3D)

        assert len(temporary_mgmt_list) > 0
        valid_mgmts.append(temporary_mgmt_list)

    arr = np.asarray(list4D, dtype=np.float32)

    # caching
    np.save('cache.array.%s' % cache, arr)
    with open('cache.axis_map.%s.json' % cache, 'w') as fh:
        fh.write(json.dumps(axis_map, indent=2))
    with open('cache.valid_mgmts.%s.json' % cache, 'w') as fh:
        fh.write(json.dumps(valid_mgmts, indent=2))

    return arr, axis_map, valid_mgmts



climates = [
    "CCSM4-rcp45",
    "CCSM4-rcp85",
    "Ensemble-rcp45",
    "Ensemble-rcp85",
    "GFDLCM3-rcp45",
    "GFDLCM3-rcp85",
    "HadGEM2ES-rcp45",
    "HadGEM2ES-rcp85",
    "NoClimate",
    ]

# climates = ['NoClimate']

with open("results.csv", 'w') as fh:
    fh.write("year,climate,timber,carbon,owl,fire,cost")
    fh.write("\n")

for climate in climates:
    print climate

    #----------- STEP 1: Read source data -------------------------------------#
    # 4D: stands, rxs, time periods, variables
    stand_data, axis_map, valid_mgmts = prep_db2(db="./master.sqlite", 
                                                 climate=climate, cache=climate)

    #----------- STEP 2: Identify and configure variables ---------------------#
    # THIS MUST MATCH THE DATA COMING FROM prep_data!!!
    """ 
    171 mmbf: 1995 - 2010 annual average
    210 mmbf: 2005-2010 annual average 
    502 mmbf: PRMP (proposed resource management plan)
    727 mmbf: the allowable sale quantity max (alternative 2)
    # annual target ->  convert to mbf, divide to the 4.77% subset, times 5 time periods
    # mmbf_target*1000*0.0477*5  = mmbf * 238.5
    # before, multiply by 
    # afterwards divide by 238.5 to get mmbf per year 
    """
    mmbf_target = 502
    period_target = mmbf_target*1000*0.0477*5
    print period_target, " TO ", period_target * 1.05

    axis_map['variables'] = [  
        {   
            'name': 'timber',
            #'strategy': 'evenflow_target',
            #'strategy': 'cumulative_maximize', 'targets': [period_target] * 20,
            'strategy': 'within_bounds', 'targets': ([period_target * 0.99] * 20, [period_target * 1.05] * 20),
            'weight': 6.0 },
        {   
            'name': 'carbon',
            'strategy': 'cumulative_maximize',
            'weight': 1.0 },
        {   
            'name': 'owl habitat',
            'strategy': 'cumulative_maximize',
            'weight': 1.0 },
        {   
            'name': 'fire risk',
            #'strategy': 'cumulative_minimize',
            'strategy': 'within_bounds', 
            'targets': ([0] * 20, [15000] * 20),
            'weight': 1.0 },
        {   
            'name': 'cost proxy',
            'strategy': 'cumulative_minimize',
            'weight': 1.0 },

    ]


    #----------- STEP 3: Optimize (annealing over objective function) ---------#

    # Do a quick run to get a good starting condition
    best_start = float("inf")
    for i in range(1):
        best, optimal_stand_rxs, vars_over_time = schedule(
            stand_data,
            axis_map,
            valid_mgmts,
            steps=5000 + (1000*i),
            report_interval=1000,
            temp_min=1e-5,
            temp_max=5.0
        )
        if best < best_start:
            best_start = best
            best_mgmts = optimal_stand_rxs

    # Now run the full schedule
    best, optimal_stand_rxs, vars_over_time = schedule(
        stand_data,
        axis_map,
        valid_mgmts,
        steps=255000,
        report_interval=5000,
        temp_min=0.00005,
        temp_max=20.0,
        starting_mgmts=best_mgmts,
        live_plot=False
    )

    #----------- STEP 4: output results ---------------------------------------#,
    print_results(axis_map, vars_over_time)

    with open("results.csv", 'a') as fh:
        for i, data in enumerate(vars_over_time.tolist()):
            row = [2013 + i*5, climate] + data
            fh.write(",".join([str(x) for x in row]))
            fh.write("\n")

    write_stand_mgmt_csv(optimal_stand_rxs, axis_map, filename="%s_stands_rx.csv" % climate, climate=climate)
    #import ipdb; ipdb.set_trace()
