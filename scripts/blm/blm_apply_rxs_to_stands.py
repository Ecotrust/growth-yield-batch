import sqlite3

DATABASE = "master.sqlite"

rxs = {
    # All available rxs
    (u'BLM', u'PN'): "1,2,3,4,5,6,7",
    (u'BLM', u'WC'): "1,2,3,4,5,6,7",
    (u'BLM', u'NC'): "1,4,5,6,7,8,9",
    (u'BLM', u'CA'): "1,4,5,6,7,8,9",
    (u'BLM', u'SO'): "1,4,5,6,7,8,9",

    # Grow only
    (u'Exclusion or Stream Buffer', u'PN'): "1",
    (u'Exclusion or Stream Buffer', u'WC'): "1",
    (u'Exclusion or Stream Buffer', u'NC'): "1",
    (u'Exclusion or Stream Buffer', u'CA'): "1",
    (u'Exclusion or Stream Buffer', u'SO'): "1",

    # limited thinning due to spotted owl
    (u'NSOW', u'PN'): "1,6,7",
    (u'NSOW', u'WC'): "1,6,7",
    (u'NSOW', u'NC'): "1,6,7",
    (u'NSOW', u'CA'): "1,6,7",
    (u'NSOW', u'SO'): "1,6,7",
}

if __name__ == "__main__":

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    table_query = """SELECT mgmtgrp, variant
        FROM stands 
        GROUP BY mgmtgrp, variant"""

    cur.execute(table_query)
    combos = cur.fetchall()

    for mgmtgrp, variant in combos:
        print "updating", mgmtgrp, variant
        query = """UPDATE stands
            SET rx = '%s'
            WHERE mgmtgrp = '%s'
            AND variant = '%s'""" % (rxs[(mgmtgrp, variant)], mgmtgrp, variant)
        cur.execute(query)

    con.commit()
    cur.close()
