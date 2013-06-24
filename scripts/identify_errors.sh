#!/bin/bash
datadir=/mnt/ebs1a

echo "1. identify explicit errors"
echo

#mkdir -p /tmp/to_fix

for i in $datadir/out/var*.err; 
do
   x=${i%.*}
   name=${x##*/}
   var=${name:3:2}   
   echo $datadir/realdata/$var/plots/$name
   #cp -r $datadir/realdata/$var/plots/$name /tmp/to_fix/$name
done

echo "2. identify original data that hasn't got csvs or bz2s (not yet run for whatever reason)"
echo 
for i in $datadir/realdata/*/plots/*;
do
   x=${i%.*}
   name=${x##*/}
   var=${name:3:2}   
   # we already got the errors in the first step
   if [ ! -f $datadir/out/$name.csv ] && [ ! -f $datadir/out/$name.err ] ;
   then
       echo
       echo $datadir/realdata/$var/plots/$name
       #cp -r $datadir/realdata/$var/plots/$name /tmp/to_fix/$name
   fi
   if [ ! -f $datadir/out/$name.tar.bz ];
   then
       echo
       echo $datadir/realdata/$var/plots/$name
       #cp -r $datadir/realdata/$var/plots/$name /tmp/to_fix/$name
   fi
   
done


####
echo
echo "Now run 'fvsbatch /tmp/to_fix'"
# echo "(clean out /usr/local/data/out/*.err if running on same machine!)"
####



