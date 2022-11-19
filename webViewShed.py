
# -*- coding: utf-8 -*-
import sys
import os
import os.path

new_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder/extlibs', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis2web', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms']
for i in new_path:
    sys.path.append(i)
from qgis import processing

from qgis.core import (
    QgsApplication,
    QgsVectorLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsVectorFileWriter,QgsPointXY
)
from qgis.analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

from qgis.core import *
from qgis.utils import *
from json import dumps

import shapefile

cwd = os.getcwd()
output_folder = cwd+'/output'#/home/bisag/Documents/webViewShed/webViewShed.py

###user input
rad = 600
coorx,coory = 71.515452,20.903966
Azimuth = 30
Wedge = 60
    
xy = str(coorx) +","+str(coory) + " [EPSG:4326]"
print(xy)
dempath = cwd+'/asterDem.tif'
visImgOp = output_folder+"/viewshed_op.tif"
processing.run("grass7:r.viewshed", {'input':dempath,
            'coordinates':xy,
            'observer_elevation':1.75,
            'target_elevation':0,
            'max_distance':rad ,
            'refraction_coeff':0.14286,
            'memory':500,
            '-c':False,
            '-r':False,
            '-b':True,
            '-e':False,
            'output':visImgOp,
            'GRASS_REGION_PARAMETER':None,
            'GRASS_REGION_CELLSIZE_PARAMETER':0,
            'GRASS_RASTER_FORMAT_OPT':'',
            'GRASS_RASTER_FORMAT_META':''})


#CREATE VIEW POINT
vl = QgsVectorLayer("Point?crs=EPSG:4326", "ViewPoint", "memory")

f = QgsFeature()
f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx,coory)))
pr = vl.dataProvider()

vl.updateFields()
pr.addFeature(f)
vl.updateExtents() 

QgsVectorFileWriter.writeAsVectorFormat(vl, output_folder+"/viewpoint.shp", "UTF-8", vl.crs() , "ESRI Shapefile")

polygonshp = output_folder+"/polygon.shp"
# if os.path.exists(polygonshp):
#     os.remove(polygonshp)
processing.run("gdal:polygonize", {'INPUT':visImgOp,
                'BAND':1,
                'FIELD':'DN',
                'EIGHT_CONNECTEDNESS':False,
                'EXTRA':'',
                'OUTPUT':polygonshp})
go1 =[]
nogo1 = []
rad1 = rad/111111 ##convert meter to degree

##for create arc shape
layer = QgsVectorLayer(output_folder+"/viewpoint.shp","viewpoint","ogr")
res = processing.run("native:wedgebuffers",
        {'INPUT':layer,
        'AZIMUTH':Azimuth,
        'WIDTH':Wedge,
        'OUTER_RADIUS':rad1,
        'INNER_RADIUS':0,
        'OUTPUT':output_folder+"/arcShape.shp"})

#clip polygone to arc shape
res = processing.run("native:clip", 
            {'INPUT':polygonshp,
            'OVERLAY':output_folder+"/arcShape.shp",
            'OUTPUT':output_folder+"/shapeClip.shp"})

##area find
res1 = processing.run("native:fieldcalculator", 
            {'INPUT':output_folder+"/shapeClip.shp",
            'FIELD_NAME':'area',
            'FIELD_TYPE':0,
            'FIELD_LENGTH':0,
            'FIELD_PRECISION':0,
            'FORMULA':'$area',
            'OUTPUT':output_folder+"/shapeClipArea.shp"})

##convert clipArc shape to geojson
reader = shapefile.Reader(output_folder+"/shapeClipArea.shp")
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
buffer = []

for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature", \
    geometry=geom, properties=atr)) 

# write the GeoJSON file
geojson1 = open(output_folder+"/shapeClipWithOp.geojson", "w")
geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
geojson1.close()

###find percentage
layer = QgsVectorLayer(output_folder+"/shapeClipArea.shp", "shapeClip", "ogr")

features = layer.getFeatures()

nogo = []
go = []
for feat in features:
    attr = feat.attributes()[1]
    attr1 = feat.attributes()[0]
    if attr1 == 1:
        go.append((int(attr)))
    else:
        nogo.append((int(attr)))
t = sum(nogo)+sum(go)

print("sum nogo",sum(nogo))
print("sum go",sum(go))
print("total",t)
sg = sum(go)
go = (sg *100)/t

nogo = 100 - go
go1.append(go)
nogo1.append(nogo)
print("nogo percentage",nogo)
print("go percentage",go)

    

