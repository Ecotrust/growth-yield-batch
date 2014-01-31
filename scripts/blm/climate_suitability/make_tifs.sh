#!/bin/bash

echo "Starting PSME"
python climquery.py Ensemble rcp45 1990 PSME file
echo "rcp45 1990 done."
python climquery.py Ensemble rcp45 2060 PSME file
echo "rcp45 2060 done."
python climquery.py Ensemble rcp85 1990 PSME file
echo "rcp85 1990 done."
python climquery.py Ensemble rcp85 2060 PSME file
echo "rcp85 2060 done."
echo "Finishing PSME"

echo "Starting TSHE"
python climquery.py Ensemble rcp45 1990 TSHE file
echo "rcp45 1990 done."
python climquery.py Ensemble rcp45 2060 TSHE file
echo "rcp45 2060 done."
python climquery.py Ensemble rcp85 1990 TSHE file
echo "rcp85 1990 done."
python climquery.py Ensemble rcp85 2060 TSHE file
echo "rcp85 2060 done."
echo "Finishing TSHE"

echo "Starting ABCO"
python climquery.py Ensemble rcp45 1990 ABCO file
echo "rcp45 1990 done."
python climquery.py Ensemble rcp45 2060 ABCO file
echo "rcp45 2060 done."
python climquery.py Ensemble rcp85 1990 ABCO file
echo "rcp85 1990 done."
python climquery.py Ensemble rcp85 2060 ABCO file
echo "rcp85 2060 done."
echo "Finishing ABCO"

echo "Starting PIPO"
python climquery.py Ensemble rcp45 1990 PIPO file
echo "rcp45 1990 done."
python climquery.py Ensemble rcp45 2060 PIPO file
echo "rcp45 2060 done."
python climquery.py Ensemble rcp85 1990 PIPO file
echo "rcp85 1990 done."
python climquery.py Ensemble rcp85 2060 PIPO file
echo "rcp85 2060 done."
echo "Finishing PIPO"

echo "Starting ALRU"
python climquery.py Ensemble rcp45 1990 ALRU2 file
echo "rcp45 1990 done."
python climquery.py Ensemble rcp45 2060 ALRU2 file
echo "rcp45 2060 done."
python climquery.py Ensemble rcp85 1990 ALRU2 file
echo "rcp85 1990 done."
python climquery.py Ensemble rcp85 2060 ALRU2 file
echo "rcp85 2060 done."
echo "Finishing ALRU"

echo "complete."
