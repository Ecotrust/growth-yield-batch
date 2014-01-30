#!/bin/bash

for f in `ls geotifs/change_class/ | grep .tif$ | grep clipped`; do
    echo ""
    echo "$f"
    python tif_histogram.py geotifs/change_class/$f
done
