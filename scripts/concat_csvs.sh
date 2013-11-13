# copy header
sed -n 1p `ls var*csv | head -n 1` > merged.csv
#copy all but the first line from all other files
for i in var*.csv; do sed 1d $i >> merged.csv ; done