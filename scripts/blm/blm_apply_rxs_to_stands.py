import sqlite3

DATABASE = "master.sqlite"

rxs = {
    # All available rxs
    # explicitly list all? Or just keep blank????????????????????????????????????????????
    (u'BLM', u'PN'): "",
    (u'BLM', u'WC'): "",
    (u'BLM', u'NC'): "",
    (u'BLM', u'CA'): "",
    (u'BLM', u'SO'): "",

    # Grow only
    (u'GO', u'PN'): "1",
    (u'GO', u'WC'): "1",
    (u'GO', u'NC'): "1",
    (u'GO', u'CA'): "1",
    (u'GO', u'SO'): "1",

    # limited thinning due to spotted owl
    ######################################################### TODO 
    (u'NSOW', u'PN'): "1,8,9",
    (u'NSOW', u'WC'): "1,8,9",
    (u'NSOW', u'NC'): "1,8,9",
    (u'NSOW', u'CA'): "1,14,15",
    (u'NSOW', u'SO'): "1,14,15",
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
