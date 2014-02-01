#!/bin/bash

list=''
for f in `ls clipped_deltas/ | grep .img$`; do
    list=$list' '$f
done
# echo 'List is: '$list
'python tif_histogram.py'$list
