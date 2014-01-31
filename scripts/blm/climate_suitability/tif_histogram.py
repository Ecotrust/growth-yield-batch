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

	classes = [
		count[11], count[12], count[13], count[14], 
		count[21], count[22], count[23], count[24], 
		count[31], count[32], count[33], count[34], 
		count[41], count[42], count[43], count[44]
	]

	good = sum([count[x] for x in good_cases])
	bad = sum([count[x] for x in bad_cases])

	return (good,bad,classes)

def write_csv(fileLocation, rows):
	with open('%sblm_change_value.csv' % fileLocation, 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['Species', 'RCP', 'Retained', 'Lost', '11', '12', '13', '14', '21', '22', '23', '24', '31', '32', '33', '34', '41', '42', '43', '44'])
		for row in rows:
			writer.writerow(row)

	print '%sblm_change_value.csv written' % fileLocation


if __name__ == "__main__":
	fileLocation = "clipped_deltas/"

	if len(sys.argv) > 1:
		fileList = []
		for filename in sys.argv[1:]:
			fileList.append(filename)
	else:
		print 'No files given to '
		sys.exit()

	csv_rows = []

	for fn in fileList:
		print fn
		(good,bad,classes) = get_tif_vals(fileLocation + fn)
		fn_print = "%s_%s" % (fn.split("_")[0], fn.split("_")[2])
		print "\n%s" % fn_print
		print "Good: %s" % good
		print "Bad: %s\n" % bad

		csv_rows.append(fn_print.split("_") + [good/100, bad/100, 
			classes[0]/100, classes[1]/100, classes[2]/100, classes[3]/100, 
			classes[4]/100, classes[5]/100, classes[6]/100, classes[7]/100, 
			classes[8]/100, classes[9]/100, classes[10]/100, classes[11]/100, 
			classes[12]/100, classes[13]/100, classes[14]/100, classes[15]/100
		])

	write_csv(fileLocation, csv_rows)
