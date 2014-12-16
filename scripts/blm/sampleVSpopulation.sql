

select batch, count(*) from stands group by batch;

UPDATE stands
SET batch = 'batch1_sample4' 
WHERE standid IN (SELECT distinct(standid) FROM fvs_stands);

SELECT s.batch, AVG(QMDA_DOM), AVG(SDI), AVG(BAA_GE_3), AVG(QMDA_DOM), AVG(AGE_DOM)
FROM gnn_standattrs as gnn
JOIN stands as s
ON s.gnnfcid = gnn.fcid
GROUP BY s.batch;


SELECT s.batch, count(*), gnn.IMAP_DOMSPP
FROM gnn_standattrs as gnn
JOIN stands as s
ON s.gnnfcid = gnn.fcid
GROUP BY s.batch, gnn.IMAP_DOMSPP;
