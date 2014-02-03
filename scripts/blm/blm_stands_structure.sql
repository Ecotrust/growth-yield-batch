DROP table stands;

CREATE TABLE "stands" (
  OGC_FID INTEGER PRIMARY KEY,
  GEOMETRY BLOB , 
  slope FLOAT, 
  aspect FLOAT, 
  elev FLOAT, 
  gnnfcid INTEGER, 
  sitecls INTEGER, 
  acres FLOAT, 
  standid INTEGER, 
  location INTEGER, 
  lat FLOAT, 
  batch VARCHAR(10),
  rx VARCHAR(128), 
  variant VARCHAR(3), 
  district VARCHAR(30),
  mgmtgrp TEXT);

-- modify to map the stands_orig structure to this

--PrjID       standid     unique across study area
--AvgElevM    elev        meters, mean
--b_slope     slope       median/mean
--b_aspect    aspect      majority based on classified slope map?
--SiteClass   sitecls     numeric site class code  corresponds to a site tree/index combo
--acres       acres    
--GNN_FCID    gnnfcid     zonal majority
--LocCode     location    3 digit location or region code, based on our hand-drawn map
--LAT         lat  
--          batch       LEAVE BLANK FOR NOW (a code to divide up the FVS runs)
--          rx      LEAVE BLANK FOR NOW (a comma-delimited list of valid rxs)
--Variant                variant     based on our hand drawn map
--DIST_NAME   district     
--Category    mgmtgrp         BLM, NSOW, GO (Exclusion/GrowOnly)

INSERT INTO stands (OGC_FID, GEOMETRY, slope, 
                    aspect, elev, gnnfcid, sitecls, acres, standid, 
                    location, lat, batch, rx, variant, district, mgmtgrp)
SELECT 
	OGC_FID as OGC_FID,
	GEOMETRY as GEOMETRY,
    b_slope as slope,
    b_aspect as aspect,
    AvgElevM as elev,
    GNN_FCID as gnnfcid,
    SiteClass as sitecls,
    acres as acres,
    PrjID as standid,
    LocCode as location,
    LAT as lat,
    "all" as batch,
    "" as rx,
    Variant as variant,
    DIST_NAME as district,
    Category as mgmtgrp
FROM stands_orig;
