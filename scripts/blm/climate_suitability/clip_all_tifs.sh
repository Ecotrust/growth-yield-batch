#!/bin/bash

for f in `ls geotifs/change_class/ | grep .tif$`; do
    echo ""
    echo "$f"
    gdalwarp \
    -q -cutline geotifs/change_class/BLM_district_land_3309.shp \
    -crop_to_cutline -of GTiff \
    geotifs/change_class/$f geotifs/change_class/clipped_$f
done
