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
    AVG(c.mat) as MeanTemp,
    AVG(c.map) as MeanPrecip,

    c.Year as Year,
    s.district as District
FROM climate as c
JOIN stands as s
ON s.standid = c.StandID
GROUP BY s.district, c.scenario, c.Year;

.output forest_type_climate_change_sankey.csv
SELECT 
    standid, fortype, year, climate, rx
FROM 
    fvs_stands
WHERE
    rx = 1 AND Year IN (2013, 2063, 2108)
GROUP BY 
    standid, climate, year;

.output pSite_change_by_stand.csv
SELECT
    c.Scenario as Scenario,
    c.pSite as pSite,
    c.Year as Year,
    s.district as District
FROM climate as c
JOIN stands as s
ON s.standid = c.StandID
GROUP BY s.district, c.scenario, c.Year;
