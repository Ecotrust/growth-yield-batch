.mode csv
.headers on


-- create table fvs_stands as 
    select  
        total_stand_carbon * acres as carbon,
        removed_merch_bdft * acres / 1000.0 as timber, -- mbf
        after_merch_bdft * acres / 1000.0 as standing, --mbf
        NSONEST * acres as owl,
        (CASE WHEN FIREHZD > 3 THEN acres ELSE 0 END) as fire,
        removed_merch_bdft * slope * acres / 1000.0 as cost, -- OK as proxy
        removed_total_ft3 * acres as removed_vol, -- per period
        accretion * acres * 5 as accretion_vol, -- annual
        mortality * acres * 5 as mortality_vol, -- annual
        start_total_ft3 * acres as start_vol, -- per period
        fortype,
        year,
        standid,
        variant,
        district,
        mgmtgrp,
        fvs.rx as rx,
        "offset",
        climate,
        acres
    from fvsaggregate fvs
    join stands as s
    on s.standid = fvs.cond
    where fvs.total_stand_carbon is not null -- should remove any blanks
    ORDER BY standid, year;



.output graph_vegtype.csv
SELECT s.year as year, s.climate as climate, s.fortype as fortype, 
       sum(s.acres) as acres
    FROM fvs_stands as s
    JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
    GROUP BY s.year, s.climate, s.fortype;


.output graph_scheduled_bydistrict.csv
SELECT s.year, s.district, s.climate as climate,
                sum(carbon) as carbon, sum(timber) as timber, 
                sum(standing) as standing, sum(fire) as fire,
                sum(owl) as owl, sum(cost) as cost
    FROM fvs_stands as s
    JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
    GROUP BY s.year, s.climate, s.district;


.output graph_scheduled_byside.csv
SELECT s.year,  
        (CASE WHEN s.district 
            IN ('Medford District', 'Roseburg District', 'Lakeview District') 
            THEN 'South/Dry' ELSE 'North/Moist' END) as side,
        s.climate as climate,
        sum(carbon) as carbon, sum(timber) as timber, 
        sum(standing) as standing, sum(fire) as fire,
        sum(owl) as owl, sum(cost) as cost
    FROM fvs_stands as s
    JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
    GROUP BY s.year, s.climate, side;

.output graph_scheduled.csv
SELECT s.year, s.climate as climate,
                sum(carbon) as carbon, sum(timber) as timber, 
                sum(standing) as standing, sum(fire) as fire,
                sum(owl) as owl, sum(cost) as cost
    FROM fvs_stands as s
    JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
    GROUP BY s.year, s.climate;


.output graph_rx_by_climate.csv
SELECT 'rx' || o.rx as rx, o.rx as rxnum, s.climate as climate, 
       sum(s.acres) as acres, count(s.acres) as num
    FROM fvs_stands as s
    JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
    WHERE s.year = 2013 -- rx doesn't change over time
    GROUP BY o.rx, s.climate;


.output graph_growonly.csv
SELECT year, district, climate, sum(carbon) as carbon
    FROM fvs_stands 
    WHERE rx = 1 
    GROUP BY year, district, climate
    ORDER BY year, district, climate;


.output growonly_fortype_district_year_rcp.csv
SELECT s.year as year, s.climate as climate, s.fortype as fortype, 
       sum(s.acres) as acres, s.district as district
    FROM fvs_stands as s
    WHERE s.climate in ('Ensemble-rcp45', 'Ensemble-rcp85', 'NoClimate')
    AND s.rx = 1
    GROUP BY s.year, s.climate, s.fortype, s.district;


.output growonly_vols_district_year_rcp.csv
SELECT sum(s.start_vol) as start_vol, sum(s.accretion_vol) as accretion_vol, 
       sum(s.mortality_vol) as mortality_vol, sum(s.removed_vol) as removed_vol, 
       s.year as year, s.climate as climate, sum(s.acres) as acres, 
       s.district as district
    FROM fvs_stands as s
    WHERE s.rx = 1
    -- AND s.climate in ('Ensemble-rcp45', 'Ensemble-rcp85', 'NoClimate')
    GROUP BY s.year, s.climate, s.district;

 
.output scheduled_fortype_district_year_rcp.csv
SELECT s.year as year, s.climate as climate, s.fortype as fortype, 
       sum(s.acres) as acres, s.district as district
    FROM fvs_stands as s
    JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
    WHERE s.climate in ('Ensemble-rcp45', 'Ensemble-rcp85', 'NoClimate')
    GROUP BY s.year, s.climate, s.fortype, s.district;


.output scheduled_vols_district_year_rcp.csv
SELECT sum(s.start_vol) as start_vol, sum(s.accretion_vol) as accretion_vol, 
       sum(s.mortality_vol) as mortality_vol, sum(s.removed_vol) as removed_vol, 
       s.year as year, s.climate as climate, sum(s.acres) as acres, s.district as district
    FROM fvs_stands as s
    JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
    --WHERE s.climate in ('Ensemble-rcp45', 'Ensemble-rcp85', 'NoClimate')
    GROUP BY s.year, s.climate, s.district;


.output graph_rx_by_climate_and_mgmtgrp.csv
SELECT 'rx' || o.rx as rx, o.rx as rxnum, s.climate as climate, 
       sum(s.acres) as acres, count(s.acres) as num, s.mgmtgrp as mgmtgrp
    FROM fvs_stands as s
    JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
    WHERE s.year = 2013 -- rx doesn't change over time
    GROUP BY o.rx, s.climate, s.mgmtgrp;

.output climate_change_by_district.csv
SELECT
    c.Scenario as Scenario,
    c.Year as Year,
    s.district as District,
    AVG(c.mat) as AVG_MAT,
    AVG(c.map) as AVG_MAP,
    AVG(c.gsp) as AVG_GSP,
    AVG(c.mtcm) as AVG_MTCM,
    AVG(c.mmin) as AVG_MMIN,
    AVG(c.mtwm) as AVG_MTWM,
    AVG(c.mmax) as AVG_MMAX,
    AVG(c.sday) as AVG_SDAY,
    AVG(c.ffp) as AVG_FFP,
    AVG(c.dd5) as AVG_DD5,
    AVG(c.gsdd5) as AVG_GSDD5,
    AVG(c.d100) as AVG_D100,
    AVG(c.dd0) as AVG_DD0,
    AVG(c.smrpb) as AVG_SMRPB,
    AVG(c.smrsprpb) as AVG_SMRSPRPB,
    AVG(c.sprp) as AVG_SPRP,
    AVG(c.smrp) as AVG_SMRP,
    AVG(c.winp) as AVG_WINP
FROM climate as c
JOIN stands as s
ON s.standid = c.StandID
GROUP BY s.district, c.scenario, c.Year;

.output forest_type_climate_change_sankey.csv
SELECT 
    s.standid,   
    s.fortype,
    s.year,
    s.climate,
    s.rx, 
    s.acres
FROM 
    fvs_stands as s
JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
WHERE
    s.Year IN (2013, 2063, 2108) AND
    s.climate IN ('NoClimate', 'Ensemble-rcp45', 'Ensemble-rcp85')
GROUP BY 
    s.standid,
    s.climate,
    s.year;

.output pSite_change_by_stand.csv
SELECT 
    f.standid,
    c.Scenario,
    c.Year,
    c.pSite,
    s.district
FROM climate as c
JOIN fvs_stands as f
ON c.StandID = f.standid AND (
    (c.Scenario = 'CCSM4_rcp45' AND f.climate='CCSM4-rcp45') OR
    (c.Scenario = 'CCSM4_rcp85' AND f.climate='CCSM4-rcp85') OR
    (c.Scenario = 'Ensemble_rcp45' AND f.climate='Ensemble-rcp45') OR
    (c.Scenario = 'Ensemble_rcp85' AND f.climate='Ensemble-rcp85') OR
    (c.Scenario = 'GFDLCM3_rcp45' AND f.climate='GFDLCM3-rcp45') OR
    (c.Scenario = 'GFDLCM3_rcp85' AND f.climate='GFDLCM3-rcp85') OR
    (c.Scenario = 'HadGEM2ES_rcp45' AND f.climate='HadGEM2ES-rcp45') OR
    (c.Scenario = 'HadGEM2ES_rcp85' AND f.climate='HadGEM2ES-rcp85')
)
JOIN stands as s
ON s.standid = f.standid
GROUP BY f.standid, c.scenario, c.year, c.pSite, s.district;
