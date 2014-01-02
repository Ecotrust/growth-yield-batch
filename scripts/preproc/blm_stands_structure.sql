CREATE TABLE "stands" (
  OGC_FID INTEGER PRIMARY KEY,
  GEOMETRY BLOB , 
  area FLOAT, 
  perimeter FLOAT, 
  inside INTEGER, 
  slope FLOAT, 
  aspect FLOAT, 
  elev FLOAT, 
  gnnfcid INTEGER, 
  sitecls INTEGER, 
  acres FLOAT, 
  standid INTEGER, 
  location INTEGER, 
  lat FLOAT, 
  variant VARCHAR(3), 
  rx VARCHAR(128), 
  batch VARCHAR(10),
  mgmtgrp TEXT)

-- modify to map the stands_orig structure to this
-- e.g.   PrjID as standid, 

INSERT INTO stands (OGC_FID, GEOMETRY, area, perimeter, inside, slope, 
                    aspect, elev, gnnfcid, sitecls, acres, standid, 
                    location, lat, variant, rx, batch, mgmtgrp)
SELECT 
	OGC_FID as OGC_FID,
	GEOMETRY as GEOMETRY,
    area as area, 
    perimeter as permimeter, 
    inside as inside,
    slope as slope,
    aspect as aspect,
    elev as elev,
    gnnfcid as gnnfcid,
    sitecls as sitecls,
    acres as acres,
    standid as standid,
    location as location,
    lat as lat,
    variant as variant,
    rx as rx,
    batch as batch,
    mgmtgrp as mgmtgrp
FROM stands_orig