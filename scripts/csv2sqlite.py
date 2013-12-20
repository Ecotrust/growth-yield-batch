import sqlite3
import sys
import csv
import os
from decimal import Decimal, InvalidOperation


def data_generator(csv_path):
    with open(csv_path, 'rb') as fh:
        cr = csv.reader(fh, delimiter=',', quotechar='"')
        cr.next()  # skip header
        for row in cr:
            yield row


def create_table_sql(csv_path, table):
    with open(csv_path, 'rb') as fh:
        cr = csv.reader(fh, delimiter=',', quotechar='"')
        header = cr.next()
        cols = []
        # just check first row
        for i, val in enumerate(cr.next()):
            key = header[i]

            # special case, stupid headers on fvsclimattrs 
            if key.startswith("20") and key.endswith("PST"):
                key = "StandID"

            try:
                Decimal(val)
                nt = 'REAL'
                try:
                    int(val)
                    nt = "INTEGER"
                except ValueError:
                    pass
            except InvalidOperation:
                # string
                nt = "TEXT"
            cols.append('"%s" %s' % (key, nt))
        sql = "CREATE TABLE %s(%s);" % (table, ',\n'.join(cols))
    print sql 
    return sql


if __name__ == "__main__":
    INCSV = sys.argv[1]
    DATABASE = sys.argv[2]
    TABLE = sys.argv[3]

    if not os.path.exists(INCSV):
        raise Exception("%s doesn't exist" % INCSV)

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    table_query = """SELECT name FROM sqlite_master WHERE type='table' AND name='%s';""" % (TABLE,)
    cur.execute(table_query)
    table_exists = len(cur.fetchall())

    if table_exists == 0:
        print "Creating table"
        sql = create_table_sql(INCSV, TABLE)
        cur.execute(sql)
    else:
        print "Table exists; Trying to insert into existing table"

    columns_query = "PRAGMA table_info(%s)" % TABLE
    cur.execute(columns_query)
    numcol = len(cur.fetchall())

    print "Inserting data into table"
    sql = "INSERT INTO %s VALUES (%s);" % (TABLE, ",".join("?"*numcol))
    cur.executemany(sql, data_generator(INCSV))

    con.commit()
    cur.close()
