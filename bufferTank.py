import os
from osgeo import osr
from json import dumps
import sys
import shapefile
import time
from osgeo import ogr
import os
from geojson import Point,MultiPoint,Feature, FeatureCollection, dump

new_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/home/bisag/.local/lib/python3.8/site-packages', '/usr/local/lib/python3.8/dist-packages', '/usr/lib/python3/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '.', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/shapetools/ext-libs']

for i in new_path:
    sys.path.append(i)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os.path
from qgis.core import (QgsApplication,QgsVectorLayer, QgsVectorLayer,QgsCoordinateReferenceSystem)

QgsApplication.setPrefixPath('/usr', True) #for avoiding "Application path not initialized"
qgs = QgsApplication([],False)
qgs.initQgis()

from qgis import processing
from qgis.analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

#bufferSize = 0.0045 #1000 meter(user defined)


latlongBfr = 0.011#2000 meter (fix)
dist = 0.05

cwd = "/home/bisag/Music/webMobility"
grd = cwd+'/geojson/mobility_grid_geojson'
savePath = cwd+'/geojson/bufferObstacle'
procCorr = grd+'/Mobility_Grid_Selected.geojson'

##########
file1 = open(cwd+"/num_tankrun.txt",'r')
content = file1.read()
nooftank = int(content)
print('no of tankrun:',nooftank)
file1.close()

file11 = open(cwd+"/intertankdist.txt",'r')###tank between distance
content1 = file11.read()
bufferSize = float(int(content1)/111000)
print('tank between distance:',bufferSize)
#########3

##backgrund algo:
temp = QgsVectorLayer(procCorr, "Wkt polygon", "ogr")#selectSaveGrid
single_symbol_renderer = temp.renderer()####holo (outerline black symbology)
symbol = single_symbol_renderer.symbol()
symbol.setColor(QColor("transparent"))
symbol.symbolLayer(0).setStrokeColor(QColor("black"))   # change the stroke colour (Fails)
symbol.symbolLayer(0).setStrokeWidth(1.5)   # change the stroke colour (Fails)
temp.triggerRepaint()
temp.commitChanges()
ex = temp.extent()
xmax = str(ex.xMaximum())
ymax = str(ex.yMaximum())
xmin = str(ex.xMinimum())
ymin = str(ex.yMinimum())
ex1 = xmax+','+xmin+','+ymax+','+ymin+' [EPSG:4326]'

gid = []###for save layer
for feat in temp.getFeatures():
    gid.append(feat['gid'])
    
gd = str(gid[0])
svpath = 'mobility_'+gd
#print("save path: ",svpath)

#####

mypath1 = savePath+'/'+svpath+"/shapefile/" #remove all files
mypath2 = savePath+'/'+svpath+"/buffer/"
mypath3 = savePath+'/'+svpath+"/output/"
l = [mypath1,mypath2,mypath3]

for delfol in l:
    for root, dirs, files in os.walk(delfol):
        for file in files:
            os.remove(os.path.join(root, file))
for root, dirs, files in os.walk(savePath+'/'+svpath):##remove geojson files
    for file in files:
        if file.endswith(".geojson"):
            os.remove(os.path.join(root, file))
for root, dirs, files in os.walk(savePath):##remove elevation image files
    for file in files:
        if file.endswith(".png"):
            os.remove(os.path.join(root, file))

wktfix = processing.run("native:fixgeometries",
                         {'INPUT':cwd+'/mobility_wkt1.geojson',
                         'OUTPUT':savePath+'/new/mobility_wkt1.geojson'})

clip1 = processing.run("native:clip",
                {'INPUT':wktfix['OUTPUT'],
                'OVERLAY':temp,
                'OUTPUT':savePath+'/new/clip.shp'})

temp1 = QgsVectorLayer(clip1['OUTPUT'], "clip", "ogr")#clip
single_symbol_renderer = temp1.renderer()
symbol = single_symbol_renderer.symbol()
symbol.setColor(QColor("black"))
symbol.symbolLayer(0).setStrokeColor(QColor("black"))   # change the stroke colour (Fails)
temp1.commitChanges()
temp1.triggerRepaint()

res3 = processing.run("native:rasterize",
                     {'EXTENT':ex1,
                        'EXTENT_BUFFER':0,
                        'TILE_SIZE':1024,
                        'MAP_UNITS_PER_PIXEL':0.00009,
                        'MAKE_BACKGROUND_TRANSPARENT':False,
                        'MAP_THEME':None,
                        'LAYERS':[temp1,temp],
                        'OUTPUT':savePath+'/output/convertMapRaster.tif'})
res4 = processing.run("gdal:cliprasterbyextent", 
                        {'INPUT':res3['OUTPUT'],
                        'PROJWIN':ex1,
                        'NODATA':None,
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'EXTRA':'',
                        'OUTPUT':savePath+'/output/convertMapRasterClip.tif'})

rearr = processing.run("gdal:rearrange_bands",
                        {'INPUT':res4['OUTPUT'],
                        'BANDS':[1],
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'OUTPUT':savePath+'/output/singleband.tif'})
                        
reclass = processing.run("native:reclassifybytable",
            {'INPUT_RASTER':rearr['OUTPUT'],
            'RASTER_BAND':1,
            'TABLE':[0,38,1,38,255,2],
            'NO_DATA':-9999,
            'RANGE_BOUNDARIES':0,
            'NODATA_FOR_MISSING':False,
            'DATA_TYPE':5,
            'OUTPUT':savePath+'/recassify.tif'})

##find elevation profile
def elevation():
    os.system(f"python3 {savePath}/elevation_profile.py")

##buffer cerate for latlong:   
lat_long_list = open(cwd+"/lat_long_list.txt",'r')
content = lat_long_list.read()
content = content.split(",")
xy = [float(content[0].strip()),float(content[1].strip()),float(content[2].strip()),float(content[3].strip())]

file_path = savePath+'/'+svpath+'/lat_long_list.geojson'

point = Point((float(content[0].strip()),float(content[1].strip())))
point1 = Point((float(content[2].strip()),float(content[3].strip())))
features = []
features.append(Feature(geometry=point,properties={"id": 1}))
features.append(Feature(geometry=point1,properties={"id": 2}))
feature_collection = FeatureCollection(features)
with open(file_path, 'w') as f:
   dump(feature_collection, f)
lat_long_list.close()

# poinrbuffer = processing.run("native:buffer", {### buffer of point layer
#                     'INPUT':file_path,
#                     'DISTANCE':latlongBfr,
#                     'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,
#                     'OUTPUT':savePath+'/'+svpath+'/latlongbuffer.geojson'})

##########################perpendicular line to buffer processing:
pth1 = processing.run("qgis:pointstopath",
            {'INPUT':file_path,
            'CLOSE_PATH':False,
            'ORDER_FIELD':'id',
            'GROUP_FIELD':'',
            'DATE_FORMAT':'',
            'OUTPUT':savePath+'/'+svpath+'/shapefile/path.shp'})
e0 =processing.run("native:extractspecificvertices", 
            {'INPUT':pth1['OUTPUT'],
            'VERTICES':'0',
            'OUTPUT':savePath+'/'+svpath+'/shapefile/e0.shp'})
e1 =processing.run("native:extractspecificvertices", 
            {'INPUT':pth1['OUTPUT'],
            'VERTICES':'-1',
            'OUTPUT':savePath+'/'+svpath+'/shapefile/e1.shp'})
            
mpoints = processing.run("native:mergevectorlayers", {'LAYERS':[e0['OUTPUT'],e1['OUTPUT']],
                                        'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':savePath+'/'+svpath+'/shapefile/points.shp'})
perpend = processing.run("native:geometrybyexpression", 
            {'INPUT':mpoints['OUTPUT'],
            'OUTPUT_GEOMETRY':1,
            'WITH_Z':False,
            'WITH_M':False,
            'EXPRESSION':f'extend(make_line($geometry,project ($geometry, {dist},radians(\"angle\"-90))),{dist},0)',
            'OUTPUT':savePath+'/'+svpath+'/shapefile/perpendicular.shp'})
            
poinrbuffer = processing.run("native:buffer", {### buffer of point layer
                    'INPUT':perpend['OUTPUT'],
                    'DISTANCE':latlongBfr,
                    'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,
                    'OUTPUT':savePath+'/'+svpath+'/latlongbuffer.geojson'})
###########################
def fivemeterPath(c):
    print(f'start route{c}...')

    os.system(f"python3 {savePath}/shortest_path.py {xy[-4]} {xy[-3]} {xy[-2]} {xy[-1]}")
    elevation()

    f = open(savePath+"/path.txt", "r")
    x = f.read()
    f.close()

    wkt = x.split("\n")
    wkt = [i for i in wkt if i]#remove empty string

    wktval = wkt[0]

    spatialref = osr.SpatialReference()
    spatialref.ImportFromProj4('+proj=longlat +datum=WGS84 +no_defs')

    driver = ogr.GetDriverByName("ESRI Shapefile")

    input_folder = savePath+f"/{svpath}/shapefile/line{c}.shp"
    dstfile = driver.CreateDataSource(input_folder)
    dstlayer = dstfile.CreateLayer("line", spatialref, geom_type=ogr.wkbLineString)
    fielddef = ogr.FieldDefn("ID", ogr.OFTInteger)
    fielddef.SetWidth(10)
    dstlayer.CreateField(fielddef)
    poly = ogr.CreateGeometryFromWkt(wktval)
    feature = ogr.Feature(dstlayer.GetLayerDefn())
    feature.SetGeometry(poly)
    feature.SetField("ID", c)
    dstlayer.CreateFeature(feature)
    feature.Destroy()
    dstfile.Destroy()

    try:
        from pyproj import Geod
        from shapely import wkt

        #in meter
        line =wkt.loads(wktval)
        geod = Geod(ellps="WGS84")

        len2 = geod.geometry_length(line)
        
        len1 = str(len2)
        #print("length is (meter):",len1)
    except Exception as e:
        print(e)


    ##convert shape to geojson
    reader = shapefile.Reader(input_folder)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    line = []

    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        try:
            geom = sr.shape.__geo_interface__
            if geom['type'] == 'LineString':
                atr['length(m'] = len1

            line.append(dict(type="Feature", \
            geometry=geom, properties=atr)) 
        except Exception as e:
            print(e)

    # write the GeoJSON file

    op = savePath+f'/{svpath}'
    geojson11 = open(op+"/line{}.geojson".format(str(c)), "w")
    geojson11.write(dumps({"type": "FeatureCollection", "features": line}, indent=2) + "\n")
    geojson11.close()

    bfr = processing.run("native:buffer", ##1000 meter fix buffer
                {'INPUT':input_folder,
                'DISTANCE':bufferSize,
                'SEGMENTS':5,
                'END_CAP_STYLE':0,
                'JOIN_STYLE':0,
                'MITER_LIMIT':2,
                'DISSOLVE':False,
                'OUTPUT':op+"/buffer"+'/buffer{}.shp'.format(str(c))})

    ########### Buffer to geojson
    reader = shapefile.Reader(bfr['OUTPUT'])
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []

    for sr in reader.shapeRecords():
        try:
            atr = dict(zip(field_names, sr.record))

            atr['name2'] = "/Buffer_{}".format(str(c))
            geom = sr.shape.__geo_interface__
            buffer.append(dict(type="Feature", \
            geometry=geom, properties=atr))
        except Exception as e:
            print(e)
    
    # write the GeoJSON file
    
    geojson1 = open(op+"/buffer/Buffer_line{}.geojson".format(str(c)), "w")
    geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
    geojson1.close()
   
   
def anotherpath(c):
    print(f'start buffer as a obstacles:route{c}...')

    if os.path.exists(reclass['OUTPUT']):
        os.remove(reclass['OUTPUT'])
    

    ##all buffer merge:
    bfr = []
    bfrpath = savePath+f"/{svpath}/buffer/"
    for root, dirs, files in os.walk(bfrpath):##remove geojson files
        for file in files:
            if file.endswith(".geojson"):
                bfr.append(os.path.join(root, file))
    #print(bfr,'\n this is buffer files:')

    mbfr =processing.run("native:mergevectorlayers", 
                        {'LAYERS':bfr,
                        'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                        'OUTPUT':savePath+"/another"+f'/mergeBfr{c}.shp'})

    df2 = processing.run("native:difference", 
            {'INPUT':mbfr['OUTPUT'],
            'OVERLAY':poinrbuffer['OUTPUT'],
            'OUTPUT':savePath+"/another"+f'/difBfr{c}.shp'})
    
    df2 = processing.run("native:dissolve", {'INPUT':df2['OUTPUT'],
                            'FIELD':[],
                            'OUTPUT':savePath+"/another"+f'/dissolveDiff{c}.shp'})
    ########################
    vlayer = QgsVectorLayer(df2['OUTPUT'], "Buffer", "ogr")
    single_symbol_renderer = vlayer.renderer()####holo (outerline black symbology)
    symbol = single_symbol_renderer.symbol()
    symbol.setColor(QColor("black"))
    symbol.symbolLayer(0).setStrokeColor(QColor("black"))   # change the stroke colour (Fails)
    #symbol.symbolLayer(0).setStrokeWidth(1)   # change the stroke colour (Fails)

    vlayer.triggerRepaint()
    vlayer.commitChanges()

    #######################333
    res3 = processing.run("native:rasterize", 
                        {'EXTENT':ex1,
                        'EXTENT_BUFFER':0,
                        'TILE_SIZE':1024,
                        'MAP_UNITS_PER_PIXEL':0.00009,
                        'MAKE_BACKGROUND_TRANSPARENT':False,
                        'MAP_THEME':None,
                        'LAYERS':[temp1,temp,vlayer],
                        #'LAYERS':bfr,

                        'OUTPUT':savePath+"/another"+f'/convertMapRaster{c}.tif'})

    res4 = processing.run("gdal:cliprasterbyextent", 
                {'INPUT':res3['OUTPUT'],
                'PROJWIN':ex1,
                'NODATA':None,
                'OPTIONS':'',
                'DATA_TYPE':0,
                'EXTRA':'',
                'OUTPUT':savePath+f'/another/convertMapRasterClip{c}.tif'})

    rb = processing.run("gdal:rearrange_bands",
                {'INPUT':res4['OUTPUT'],
                'BANDS':[1],
                'OPTIONS':'',
                'DATA_TYPE':0,
                'OUTPUT':savePath+f'/another/singleband{c}.tif'})
                
    
    reclassanother1 = processing.run("native:reclassifybytable",
                {'INPUT_RASTER':rb['OUTPUT'],
                'RASTER_BAND':1,
                'TABLE':[0,38,1,38,255,2],
                'NO_DATA':-9999,
                'RANGE_BOUNDARIES':0,
                'NODATA_FOR_MISSING':False,
                'DATA_TYPE':5,
                'OUTPUT':savePath+'/recassify.tif'})


if __name__ == "__main__":
    start = time.time()
    
    for k in range(nooftank):
        fivemeterPath(k+1)
        anotherpath(k+1)
        
    print(f'Generated {nooftank} paths in {time.time() - start} (second)')
        