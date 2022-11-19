import os
import ogr,osr

from json import dumps
import sys
import shapefile
from shapely.wkt import loads

import geojson
import shapely.wkt

new_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder/extlibs', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis2web', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms']
for i in new_path:
    sys.path.append(i)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os.path
from qgis import processing
from qgis.core import (
    QgsApplication,
    QgsVectorLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsVectorFileWriter,QgsCoordinateReferenceSystem
)

from qgis.analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

cwd = os.getcwd()
output_folder = cwd+'/output'

#remove all files
mypath = cwd+"/geojson/"
mypath1 = cwd+"/shapefile/"
mypath2 = cwd+"/buffer/"
mypath3 = cwd+"/output/"

l = [mypath,mypath1,mypath2,mypath3]
for delfol in l:
    #print(delfol)
    for root, dirs, files in os.walk(delfol):
        for file in files:
            os.remove(os.path.join(root, file))

############background run algorithm

#read wkt file
f = open(cwd+"/mobility_wkt1.txt", "r")
wkt = f.read()
f.close()

temp = QgsVectorLayer("MultiPolygon?crs=EPSG:4326", "Wkt polygon", "memory")

single_symbol_renderer = temp.renderer()
symbol = single_symbol_renderer.symbol()
symbol.setColor(QColor.fromRgb(0,255,28))
symbol.symbolLayer(0).setStrokeStyle(Qt.PenStyle(Qt.NoPen))

temp.triggerRepaint()

temp.startEditing()
geom = QgsGeometry()
geom = QgsGeometry.fromWkt(wkt)
feat = QgsFeature()
feat.setGeometry(geom)
temp.dataProvider().addFeatures([feat])
temp.commitChanges()
#save file code
QgsVectorFileWriter.writeAsVectorFormat(temp, cwd+"/wktpolygon.shp", "UTF-8", temp.crs(), "ESRI Shapefile")

processing.run("native:rasterize",
        {'EXTENT':'71.004347413,71.266877426,26.193131580,26.432582205 [EPSG:4326]',
        'EXTENT_BUFFER':0,
        'TILE_SIZE':1024,
        'MAP_UNITS_PER_PIXEL':0.00005,
        'MAKE_BACKGROUND_TRANSPARENT':False,
        'MAP_THEME':None,
        'LAYERS':[temp],
        'OUTPUT':cwd+'/output/convertMapRaster.tif'})
        
processing.run("gdal:rearrange_bands",
            {'INPUT':cwd+'/output/convertMapRaster.tif',
            'BANDS':[1],
            'OPTIONS':'',
            'DATA_TYPE':0,
            'OUTPUT':cwd+'/output/singleband.tif'})
            
processing.run("native:reclassifybytable",
            {'INPUT_RASTER':cwd+'/output/singleband.tif',
            'RASTER_BAND':1,
            'TABLE':[0,38,1,38,255,2],
            'NO_DATA':-9999,
            'RANGE_BOUNDARIES':0,
            'NODATA_FOR_MISSING':False,
            'DATA_TYPE':5,
            'OUTPUT':cwd+'/recassify.tif'})

#find the buffer of shortest path(500 meter)
def buffer1():
    shp_path = cwd+"/shapefile"
    shpfiles = []

    for file in os.listdir(shp_path):
        if file.endswith(".shp"):
            fpath = os.path.join(shp_path, file)
            shpfiles.append(fpath)
    #print(shpfiles)

    path1 = cwd+"/buffer"

    c = 1
    for input in shpfiles:
        
        processing.run("native:buffer", 
                    {'INPUT':input,
                    'DISTANCE':0.002100,
                    'SEGMENTS':5,
                    'END_CAP_STYLE':0,
                    'JOIN_STYLE':0,
                    'MITER_LIMIT':2,
                    'DISSOLVE':False,
                    'OUTPUT':path1+'/buffer{}.shp'.format(str(c))})

        c = c+1

##find elevation profile
def elevation():
    os.system(f"python3 {cwd}/elevation_profile.py")
    #os.system(f"eog {cwd}/elevation_profile.png")


input = cwd+'/recassify.tif'
def shortest_path():
    
    #source and destination of latlong given by user
    
    xy =  [71.09667353612812, 26.36652696373544, 71.14452977572878, 26.28154859435108]
    os.system(f"python3 {cwd}/a_star.py {xy[-4]} {xy[-3]} {xy[-2]} {xy[-1]}")

    elevation()

    ############convert to geojson and shape file

    f = open(cwd+"/filtered_joints.txt", "r")
    x = f.read()
    f.close()

    wkt11 = x
    spatialref = osr.SpatialReference()
    spatialref.ImportFromProj4('+proj=longlat +datum=WGS84 +no_defs')

    driver = ogr.GetDriverByName("ESRI Shapefile")
    c= 1

    ###################convert shp
    input_folder = cwd+"/shapefile/line{}.shp".format(str(c))

    dstfile = driver.CreateDataSource(input_folder)
    dstlayer = dstfile.CreateLayer("line", spatialref, geom_type=ogr.wkbLineString)
    fielddef = ogr.FieldDefn("ID", ogr.OFTInteger)
    fielddef.SetWidth(10)
    dstlayer.CreateField(fielddef)
    poly = ogr.CreateGeometryFromWkt(wkt11)
    feature = ogr.Feature(dstlayer.GetLayerDefn())
    feature.SetGeometry(poly)
    feature.SetField("ID", 0)
    dstlayer.CreateFeature(feature)
    feature.Destroy()
    dstfile.Destroy()

    ##convert shape to geojson
    reader = shapefile.Reader(input_folder)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    line = []

    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        line.append(dict(type="Feature", \
        geometry=geom, properties=atr)) 

    # write the GeoJSON file
    op = cwd+'/geojson'

    geojson11 = open(op+"/line{}.geojson".format(str(c)), "w")
    geojson11.write(dumps({"type": "FeatureCollection", "features": line}, indent=2) + "\n")
    geojson11.close()
    
    ###########create Buffer
    buffer1()
    
    ###################################convert geojson buffer

    bpath= cwd+'/buffer'
    shpfiles = []
    for file in os.listdir(bpath):
        if file.endswith(".shp"):
            fpath = os.path.join(bpath, file)
            shpfiles.append(fpath)
    print("bfr:",shpfiles)

    op = cwd+'/geojson'
    c1 = 1
    for bshp in shpfiles:
        #convert geojson using python
        reader = shapefile.Reader(bshp)
        fields = reader.fields[1:]
        field_names = [field[0] for field in fields]
        buffer = []

        for sr in reader.shapeRecords():
            atr = dict(zip(field_names, sr.record))
            geom = sr.shape.__geo_interface__
            buffer.append(dict(type="Feature", \
            geometry=geom, properties=atr)) 

        # write the GeoJSON file
        geojson1 = open(op+"/Buffer_line{}.geojson".format(str(c1)), "w")
        geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
        geojson1.close()

    ###find length of line(wkt)
    from pyproj import Geod
    from shapely import wkt

    line = loads(wkt11)
    print (line.length)#degree

    #in meter
    line =wkt.loads(wkt11)
    geod = Geod(ellps="WGS84")

    len1 = geod.geometry_length(line)

    print("length is (meter):",len1)


if __name__ == "__main__":
    shortest_path()
    