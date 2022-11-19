import os
from osgeo import osr
from json import dumps
import sys
import shapefile
import time
from osgeo import ogr
import os

new_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python3.6/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms', '/home/bisag/.local/lib/python3.6/site-packages/IPython/extensions']

for i in new_path:
    sys.path.append(i)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os.path
from qgis.core import (QgsApplication,QgsProject,QgsVectorLayer, QgsVectorLayer,QgsCoordinateReferenceSystem)

QgsApplication.setPrefixPath('/usr', True) #for avoiding "Application path not initialized"
qgs = QgsApplication([],False)
qgs.initQgis()

from qgis import processing
from qgis.analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

cwd = "/home/bisag/Music/webMobility"
bfrDis = 0.005
grd = cwd+'/geojson/mobility_grid_geojson/'
savePath = cwd+'/geojson/multisource'
procCorr = cwd+'/geojson/allgrid.geojson'
#remove all files
mypath1 = savePath+"/shapefile/"
mypath2 = savePath+"/buffer/"
mypath3 = savePath+"/output/"
l = [mypath1,mypath2,mypath3]
for delfol in l:
    for root, dirs, files in os.walk(delfol):
        for file in files:
            os.remove(os.path.join(root, file))

for root, dirs, files in os.walk(savePath):##remove geojson files
    for file in files:
        if file.endswith(".geojson"):
            os.remove(os.path.join(root, file))
########dynamic grid
grd = cwd+'/geojson/mobility_grid_geojson'
g =[]
for root, dirs, files in os.walk(grd):
        for file in files:
            if file.endswith(".geojson") and file.startswith("Mobility_Grid"):
                if file.startswith("Mobility_Grid_Selected"):
                            continue
                g.append(os.path.join(root, file))
                #os.remove(os.path.join(root, file))

grid =processing.run("native:mergevectorlayers", 
            {'LAYERS':g,
            'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT':grd+'/grid.geojson'})
            
# grid = processing.run("native:addautoincrementalfield", 
#             {'INPUT':m['OUTPUT'],
#             'FIELD_NAME':'id',
#             'START':1,
#             'GROUP_FIELDS':[],
#             'SORT_EXPRESSION':'',
#             'SORT_ASCENDING':True,
#             'SORT_NULLS_FIRST':False,
#             'OUTPUT':grd+'/grid.geojson'})
#procCorr = grid['OUTPUT']
##################

##backgrund algo:
temp = QgsVectorLayer(procCorr, "Wkt polygon", "ogr")
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

wktfix = processing.run("native:fixgeometries",
                         {'INPUT':cwd+'/mobility_wkt1.geojson',
                         'OUTPUT':savePath+'/new/mobility_wkt1.geojson'})

clip1 = processing.run("native:clip",
                {'INPUT':wktfix['OUTPUT'],
                'OVERLAY':temp,
                'OUTPUT':savePath+'/new/clip.shp'})

temp1 = QgsVectorLayer(clip1['OUTPUT'], "clip", "ogr")
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
savePath = cwd+'/geojson/multisource'


##find elevation profile
def elevation():
    os.system(f"python3 {savePath}/elevation_profile.py")

def tankrun():
    start = time.time()
   
    source = open(savePath+"/source.txt",'r')
    content = source.read()
    content = content.split(",")
   
    content =list(zip(content[::2], content[1::2]))
    xy =[''.join(i[0]+','+i[1])for i in content]
    source.close()

    dest = open(savePath+"/destination.txt",'r')
    content1 = dest.read()
    xyd = content1.split(",")
    xyd =[''.join(xyd[0]+','+xyd[1])]
    dest.close()
    
    # print('source:\n',xy)
    # print('desination:\n',xyd)

    coord = []    
    for i in xy:
        i = i.split(',')
        j = xyd[-1]
        j = j.split(',')
        k = i[0]+','+i[1]+','+j[0]+','+j[1]
        coord.append(k)

    p1 = 1
    for y in coord:
        y = y.split(",")
        xy = [float(i) for i in y]
        #print("mobility coridor:",p1)
      
        os.system(f"python3 {savePath}/shortest_path.py {xy[-4]} {xy[-3]} {xy[-2]} {xy[-1]}")#####3change shortest_path.py (input = savePath+'/recassify1.tif')

        try:
            f = open(savePath+"/path.txt", "r")
            x = f.read()
            f.close()

            wkt2 = x.split("\n")
            wkt2 = [i for i in wkt2 if i]#remove empty string
            spatialref = osr.SpatialReference()
            spatialref.ImportFromProj4('+proj=longlat +datum=WGS84 +no_defs')

            driver = ogr.GetDriverByName("ESRI Shapefile")
            c= 1
            for wktval in wkt2:

                ###################convert shp
                input_folder = savePath+"/shapefile/line{}_{}.shp".format(str(p1),str(c))

                dstfile = driver.CreateDataSource(input_folder)
                dstlayer = dstfile.CreateLayer("line", spatialref, geom_type=ogr.wkbLineString)
                fielddef = ogr.FieldDefn("ID", ogr.OFTInteger)
                fielddef.SetWidth(10)
                dstlayer.CreateField(fielddef)
                poly = ogr.CreateGeometryFromWkt(wktval)
                feature = ogr.Feature(dstlayer.GetLayerDefn())
                feature.SetGeometry(poly)
                feature.SetField("ID", p1)
                dstlayer.CreateFeature(feature)
                feature.Destroy()
                dstfile.Destroy()

                try:
                    from pyproj import Geod
                    from shapely import wkt

                    #in meter
                    line =wkt.loads(wktval)
                    geod = Geod(ellps="WGS84")

                    len1 = geod.geometry_length(line)

                    #print("length is (m):",len1)
                    #log1.write("length is (m):"+str(len1))

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
                            atr['length_(m)'] = round(len1, 2)
                            atr['id'] = str(c)

                        line.append(dict(type="Feature", \
                        geometry=geom, properties=atr)) 
                    except Exception as e:
                        print(e)

                # write the GeoJSON file
                op = cwd+'/geojson/multisource'
                geojson11 = open(op+"/line{}_{}.geojson".format(str(p1),str(c)), "w")
                geojson11.write(dumps({"type": "FeatureCollection", "features": line}, indent=2) + "\n")
                geojson11.close()

                # temp = QgsVectorLayer(op+"/line{}_{}.geojson".format(str(p1),str(c)), f"line{p1}_{c}", "ogr")
              
                # single_symbol_renderer = temp.renderer()
                # symbol = single_symbol_renderer.symbol()
                # symbol.setWidth(1.08)

                # #add maptips(mouse hover)
                # expression = """[%  @layer_name  %]"""
                # temp.setMapTipTemplate(expression)
                # QgsProject.instance().addMapLayer(temp)#

                #buffer1()#find the buffer of shortest path(500 meter)
                # processing.run("native:buffer", 
                #             {'INPUT':input_folder,
                #             'DISTANCE':0.0021,
                #             'SEGMENTS':5,
                #             'END_CAP_STYLE':0,
                #             'JOIN_STYLE':0,
                #             'MITER_LIMIT':2,
                #             'DISSOLVE':False,
                #             'OUTPUT':savePath+"/buffer"+'/buffer{}.shp'.format(str(c))})
            ########################
                c = c+1

        except Exception as e:
            print(e)
        p1 = p1 +1

    print(f'Generated  tank run for multiple source and one destination in {time.time() - start}s')
    
if __name__ == "__main__":
    tankrun()