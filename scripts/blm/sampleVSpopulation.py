from __future__ import print_function
import sqlite3
import pystaggrelite3
import pandas as pd


with sqlite3.connect('master.sqlite') as con:
    con.create_aggregate("stdev", 1, pystaggrelite3.stdev)

    query = """SELECT
        s.batch,
        AVG(QMDA_DOM) as avg_qmda_dom, stdev(QMDA_DOM) as stdev_qmda_dom,
        AVG(SDI) as avg_sdi, stdev(SDI) as stdev_sdi,
        AVG(BAA_GE_3) as avg_baa_ge_3, stdev(BAA_GE_3) as stdev_baa_ge_3,
        AVG(AGE_DOM) as avg_age_dom, stdev(AGE_DOM) as stdev_age_dom
    FROM gnn_standattrs as gnn
    JOIN stands as s
    ON s.gnnfcid = gnn.fcid
    GROUP BY s.batch;
    """

    df = pd.read_sql(query, con)
    df.to_excel('data/sampleVSpopulation/continuous.xlsx')


with sqlite3.connect('master.sqlite') as con:
    con.create_aggregate("stdev", 1, pystaggrelite3.stdev)

    query = """SELECT
        s.batch, s.district,
        AVG(QMDA_DOM) as avg_qmda_dom, stdev(QMDA_DOM) as stdev_qmda_dom,
        AVG(SDI) as avg_sdi, stdev(SDI) as stdev_sdi,
        AVG(BAA_GE_3) as avg_baa_ge_3, stdev(BAA_GE_3) as stdev_baa_ge_3,
        AVG(AGE_DOM) as avg_age_dom, stdev(AGE_DOM) as stdev_age_dom
    FROM gnn_standattrs as gnn
    JOIN stands as s
    ON s.gnnfcid = gnn.fcid
    GROUP BY s.batch, s.district;
    """

    df = pd.read_sql(query, con)
    df.to_excel('data/sampleVSpopulation/continuous_by_district.xlsx')



with sqlite3.connect('master.sqlite') as con:

    query = """SELECT 
        s.batch as batch, 
        count(*) as count, gnn.VEGCLASS as vegclass
    FROM gnn_standattrs as gnn
    JOIN stands as s
    ON s.gnnfcid = gnn.fcid
    GROUP BY s.batch, gnn.VEGCLASS;

    """

    df = pd.read_sql(query, con)
    df.to_excel('data/sampleVSpopulation/vegclass.xlsx')



with sqlite3.connect('master.sqlite') as con:

    query = """SELECT 
        s.batch as batch, s.district as district, 
        count(*) as count, gnn.VEGCLASS as vegclass
    FROM gnn_standattrs as gnn
    JOIN stands as s
    ON s.gnnfcid = gnn.fcid
    GROUP BY s.batch, s.district, gnn.VEGCLASS;

    """

    df = pd.read_sql(query, con)
    df.to_excel('data/sampleVSpopulation/vegclass_by_district.xlsx')