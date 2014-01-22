import sqlite3, sys, os, csv
from osgeo import gdal
import numpy as np

def create_grid_raster(extent,outfile,format,array):
    ydist = extent[3] - extent[1]
    xdist = extent[2] - extent[0]
    #xcount = int((xdist/cellsize)+1)
    xcount = 686
    #ycount = int((ydist/cellsize)+1)
    ycount = 516

    cellsize = float(xdist)/float(xcount)       #This should == 1000

    # Create output raster  
    driver = gdal.GetDriverByName( format )
    dst_ds = driver.Create( outfile, xcount, ycount, 1, gdal.GDT_Float32 )

    # This is bizzarly complicated
    # the GT(2) and GT(4) coefficients are zero,    
    # and the GT(1) is pixel width, and GT(5) is pixel height.    
    # The (GT(0),GT(3)) position is the top left corner of the top left pixel
    gt = (extent[0],cellsize,0,extent[3],0,(cellsize*-1.))
    dst_ds.SetGeoTransform(gt)
   
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(array,0,0)
    print "Created output %s at %s" % (format, outfile)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print 'please include at least the climate, rcp, and year:'
        print 'USAGE: python climquery.py CLIMATE RCP YEAR [METRIC] [ID/infile]'
        print 'Where if you enter text instead of ID a resultfile will replace DB Queries'
        sys.exit()

    CLIMATE = sys.argv[1]
    RCP = sys.argv[2]
    YEAR = sys.argv[3]
    METRIC = False
    ID = False
    INPUTFILE = False

    if CLIMATE not in ("CCSM4", "Ensemble", "GFDLCM3", "HadGEM2ES"):
        print 'Available climates include: "CCSM4", "Ensemble", "GFDLCM3", "HadGEM2ES"'
        print 'USAGE: python climquery.py CLIMATE RCP YEAR [METRIC] [ID]'
        sys.exit()

    if RCP not in ("rcp45", "rcp60", "rcp85"):
        print 'Available RCPs include: "rcp45", "rcp60", "rcp85"'
        print 'USAGE: python climquery.py CLIMATE RCP YEAR [METRIC] [ID]'
        sys.exit()
        
    if YEAR not in ("1990", "2030", "2060", "2090"):
        print 'Available years include: 1990, 2030, 2060, 2090'
        print 'USAGE: python climquery.py CLIMATE RCP YEAR [METRIC] [ID]'
        sys.exit()

    if len(sys.argv) > 4:
        METRIC = sys.argv[4]
        if METRIC not in ("mat","map","gsp","mtcm","mmin","mtwm","mmax","sday","ffp","dd5","gsdd5","d100","dd0","smrpb","smrsprpb","sprp","smrp","winp","ABAM","ABCO","ABGR","ABLA","ABLAA","ABMA","ABPR","ABSH","ACGL","ACGR3","ACMA3","AECA","ALRH2","ALRU2","ARME","BEPA","BEPAC","CADE27","CELE3","CHCH7","CHLA","CHNO","CONU4","FRLA","JUCO11","JUDE2","JUMO","JUOC","JUOS","JUSC2","LALY","LAOC","LIDE3","OLTE","PIAL","PIAT","PIBR","PICO","PICO3","PIED","PIEN","PIFL2","PIJE","PILA","PILO","PIMO","PIMO3","PIPO","PIPU","PISI","PIST3","PODEM","POTR5","PROSO","PRUNU","PSME","QUAG","QUCH2","QUDO","QUEM","QUGA","QUGA4","QUHY","QUKE","QULO","QUOB","QUWI2","RONE","SALIX","SEGI2","TABR2","THPL","TSHE","TSME","UMCA","pSite","DEmtwm","DEmtcm","DEdd5","DEsdi","DEdd0","DEpdd5"):
            print 'Available metrics for query include: "mat","map","gsp","mtcm","mmin","mtwm","mmax","sday","ffp","dd5","gsdd5","d100","dd0","smrpb","smrsprpb","sprp","smrp","winp","ABAM","ABCO","ABGR","ABLA","ABLAA","ABMA","ABPR","ABSH","ACGL","ACGR3","ACMA3","AECA","ALRH2","ALRU2","ARME","BEPA","BEPAC","CADE27","CELE3","CHCH7","CHLA","CHNO","CONU4","FRLA","JUCO11","JUDE2","JUMO","JUOC","JUOS","JUSC2","LALY","LAOC","LIDE3","OLTE","PIAL","PIAT","PIBR","PICO","PICO3","PIED","PIEN","PIFL2","PIJE","PILA","PILO","PIMO","PIMO3","PIPO","PIPU","PISI","PIST3","PODEM","POTR5","PROSO","PRUNU","PSME","QUAG","QUCH2","QUDO","QUEM","QUGA","QUGA4","QUHY","QUKE","QULO","QUOB","QUWI2","RONE","SALIX","SEGI2","TABR2","THPL","TSHE","TSME","UMCA","pSite","DEmtwm","DEmtcm","DEdd5","DEsdi","DEdd0","DEpdd5"'
            print 'USAGE: python climquery.py CLIMATE RCP YEAR [METRIC] [ID]'
            sys.exit()

    if len(sys.argv) == 6:
        if sys.argv[5].isalpha():
            INPUTFILE = sys.argv[5]
        else:
            ID = sys.argv[5]

    SCENARIO = "%s_%s" % (CLIMATE, RCP)

    if INPUTFILE:
        try:
            f = open('query_results/%s_%s_%s_resultfile.txt' % (METRIC, SCENARIO, YEAR), 'r')
            file_text = f.read()
            f.close()
            result = eval(file_text)
        except:
            INPUTFILE = False
            print "No result file found. Querying Database..."
            pass

    if not INPUTFILE:        
        con = sqlite3.connect('/usr/local/apps/OR_Climate_Grid/Data/orclimgrid.sqlite')
        cur = con.cursor()

        if METRIC and ID:
            table_query = """SELECT %s FROM climattrs WHERE ID='%s' AND Scenario='%s' AND Year=%s ORDER BY ID;""" % (METRIC, ID, SCENARIO, YEAR)
        elif METRIC:
            table_query = """SELECT %s FROM climattrs WHERE Scenario='%s' AND Year=%s ORDER BY ID;""" % (METRIC, SCENARIO, YEAR)
        else:
            table_query = """SELECT * FROM climattrs WHERE Scenario='%s' AND Year=%s ORDER BY ID;""" % (SCENARIO, YEAR)

        cur.execute(table_query)
        result = cur.fetchall()

        f = open('query_results/%s_%s_%s_resultfile.txt' % (METRIC, SCENARIO, YEAR), 'w')
        f.write(str(result))
        f.close()

    np_array = np.fromiter((x[0] for x in result), float)
    two_d_array = np.flipud(np.reshape(np_array, [516,686]))
    # The 'flipud' is necessary as the tif is built from bottom to top, so [0][0] is bottom left corner.

    extent = [-396304.91, 421638.32, 289695.09, 937638.32]
    #cellsize = 1
    outfile = "%s_%s_%s.tif" % (METRIC, SCENARIO, YEAR)
    format = "GTiff"

    create_grid_raster(extent, outfile, format, two_d_array)
