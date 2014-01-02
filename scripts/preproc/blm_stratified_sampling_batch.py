import sqlite3
import math
import random

DATABASE = "master.sqlite"
RATIO = 0.1
SAMPLE_NAME = 'sample'

if __name__ == "__main__":

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    table_query = """SELECT mgmtgrp, variant, location, count(standid)
        FROM stands 
        GROUP BY mgmtgrp, variant, location"""

    cur.execute(table_query)
    combos = cur.fetchall()
    for mgmtgrp, variant, location, count in combos:
        sample = int(math.ceil(count * RATIO))
        print mgmtgrp, variant, location, count, sample

        # Get all stand ids
        query = """SELECT standid FROM stands
            WHERE mgmtgrp = '%s'
            AND variant = '%s'
            AND location = %s""" % (mgmtgrp, variant, location)
        cur.execute(query)
        standids = [x[0] for x in cur.fetchall()]

        # randomly sample 
        select_standids = random.sample(standids, sample)

        # UPDATE those rows with batch = SAMPLE_NAME
        query = """UPDATE stands
            SET batch = '%s'
            WHERE standid IN (%s)
            """ % (SAMPLE_NAME, ','.join([str(x) for x in select_standids]))
        print query
        cur.execute(query)
        print

    con.commit()
    cur.close()
