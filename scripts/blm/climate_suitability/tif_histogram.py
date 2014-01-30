import sys, os, csv
from osgeo import gdal
from gdalconst import *
import numpy as np
from collections import Counter, OrderedDict

def get_tif_vals(fn):
	good_cases = [44,43,34,33]
	bad_cases = [42,41,32,31]

	ds = gdal.Open(fn, GA_ReadOnly)
	if ds is None:
		print 'Could not open ' + fn
		sys.exit(1)

	cols = ds.RasterXSize
	rows = ds.RasterYSize
	bands = ds.RasterCount

	if bands > 1:
		print 'Multiple bands exist: ' + bands
		import ipdb
		ipdb.set_trace()
		sys.exit(1)

	band = ds.GetRasterBand(1)
	data = band.ReadAsArray(0,0,cols,rows)
	nparray = np.array(data).astype(np.int64, copy=False)
	count = Counter(e for l in nparray for e in l)

	good = sum([count[x] for x in good_cases])
	bad = sum([count[x] for x in bad_cases])

	return (good,bad)

def write_csv(fileLocation, rows):
	with open('%sblm_change_value.csv' % fileLocation, 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['Species', 'RCP', 'Retained', 'Lost'])
		for row in rows:
			writer.writerow(row)

	print '%sblm_change_value.csv written' % fileLocation

	
if __name__ == "__main__":
	fileLocation = "geotifs/change_class/"
	if len(sys.argv) > 1:
		fileList = [sys.argv[1]]
	else:
		fileList = [
			"clipped_3309_ABCO_Ensemble_rcp45_change.tif",
			"clipped_3309_ABCO_Ensemble_rcp85_change.tif",
			"clipped_3309_ALRU2_Ensemble_rcp45_change.tif",
			"clipped_3309_ALRU2_Ensemble_rcp85_change.tif",
			"clipped_3309_PIPO_Ensemble_rcp45_change.tif",
			"clipped_3309_PIPO_Ensemble_rcp85_change.tif",
			"clipped_3309_PSME_Ensemble_rcp45_change.tif",
			"clipped_3309_PSME_Ensemble_rcp85_change.tif",
			"clipped_3309_TSHE_Ensemble_rcp45_change.tif",
			"clipped_3309_TSHE_Ensemble_rcp85_change.tif"
		]

	csv_rows = []

	for fn in fileList:
		(good,bad) = get_tif_vals(fileLocation + fn)
		fn_print = "%s_%s" % (fn.split("_")[2], fn.split("_")[4])
		print "\n%s" % fn_print
		print "Good: %s" % good
		print "Bad: %s\n" % bad

		csv_rows.append(fn_print.split("_") + [good, bad])

	write_csv(fileLocation, csv_rows)
