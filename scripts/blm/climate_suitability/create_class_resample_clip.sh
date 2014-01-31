#!/bin/bash

./make_tifs.sh
./create_class_rasters.sh

#Do raster calc on all rasters in ./categorize/
echo ''
echo '---RASTER CLASS CALCULATION---'
for f in `ls categorize | grep 1990`; do
    echo ""
    count=`expr ${#f} - 17`
    name=`echo ${f:0:$count}`
    echo "$name"
    rm 'change_class/'$name'_Delta.img'
    gdal_calc.py -A 'categorize/'$name'_1990_classed.img' \
    -B 'categorize/'$name'_2060_classed.img' \
    --calc "A+B" --outfile 'change_class/'$name'_Delta.img' \
    --format HFA
done

#Downsample the rasters to be in 100m^2 pieces
echo ''
echo '---RASTER DOWNSAMPLING---'
for f in `ls change_class | grep '_Delta.img$'`; do
    echo ""
    count=`expr ${#f} - 10`
    name=`echo ${f:0:$count}`
    echo "$name"
    rm 'change_class/'$name'_100s.img'
    gdalwarp -of HFA -tr 100 100 'change_class/'$f 'change_class/'$name'_100s.img'
done

#Clip the raster to BLM Land only
echo ''
echo '---RASTER CLIPPING---'
for f in `ls change_class | grep '_100s.img$'`; do
    echo ""
    count=`expr ${#f} - 9`
    name=`echo ${f:0:$count}`
    echo "$name"
    rm 'clipped_deltas/'$name'_100s.img'
    gdalwarp -q -cutline shapefiles/BLM_district_land_3309.shp \
    -crop_to_cutline -of HFA 'change_class/'$f 'clipped_deltas/'$name'_clipped.img'
done

#Create a report of the climate change data for the BLM Land
echo ''
echo '---REPORTING---'
list=''
for f in `ls clipped_deltas/ | grep .img$`; do
    list=$list$f' '
done
python tif_histogram.py $list



