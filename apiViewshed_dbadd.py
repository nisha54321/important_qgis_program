#http://192.168.13.232:5004/?cordinate=71.51459076930828,%2020.9079174228675&radius=500&radius1=800&radius2=1000
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys,os
qgis_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder/extlibs', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis2web', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms']

for i in qgis_path:
    sys.path.append(i)

from osgeo import gdal
from osgeo import ogr
import shapefile
from json import dumps

import processing           
from processing.core.Processing import Processing           
from qgis.core import (QgsPointXY,QgsApplication,QgsVectorLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsVectorFileWriter)
import psycopg2
import json 
import os
connection = psycopg2.connect(user="postgres", password="postgres", host="localhost", database="project")
cursor = connection.cursor()

app = Flask(__name__)
CORS(app)


output_tif_list = []

cwd = "/home/bisag/Music/apiViewShade1"
############### user input 
Azimuth = 90
Wedge = 60
    
radius_list =[]
yy = iter(radius_list)
gjsonPath = []


##############remove boundry
onlyGoViewshed = []
arcshp = []
clipshp =[]


####
@app.route('/',methods=['GET'])
def index():
    squery = "CREATE TABLE IF NOT EXISTS resJson (id SERIAL,latlong text,radius text,geom Geometry,PRIMARY KEY (id))"
    cursor.execute(squery)


    output_list = []
    co_ord = request.args.get('cordinate')

    coorx,coory= [float(i)for i in co_ord.split(", ")]
    vl = QgsVectorLayer("Point?crs=EPSG:4326", "ViewPoint", "memory")
    f = QgsFeature()
    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx,coory)))
    pr = vl.dataProvider()
    pr.addFeature(f)
    QgsVectorFileWriter.writeAsVectorFormat(vl, cwd+"/output/viewpoint.shp", "UTF-8", vl.crs() , "ESRI Shapefile")

    

    rad = request.args.get('radius')
    rad2 = request.args.get('radius1')
    rad3 = request.args.get('radius2')

    radius_list.append(rad3)
    radius_list.append(rad2)
    radius_list.append(rad)

    print(radius_list)

    Processing.initialize()
    ii = 0
    
    goclip = ["/home/bisag/Music/apiViewShade1/goarea/ClipGo_1000.shp","/home/bisag/Music/apiViewShade1/goarea/ClipGo_800.shp","/home/bisag/Music/apiViewShade1/goarea/ClipGo_500.shp"]
    for i in radius_list:
    
        
        ##convert geojson
        reader = shapefile.Reader(goclip[ii])
        fields = reader.fields[1:]
        field_names = [field[0] for field in fields]
        buffer = []
        buffer1 = []

        g = ''
        for sr in reader.shapeRecords():
            atr = dict(zip(field_names, sr.record))
            geom = sr.shape.__geo_interface__
        
            #print(geom)
            # data = {"type": "Polygon","coordinates": list(geom)}
            cursor.execute("""INSERT INTO resJson (latlong,radius,geom)  VALUES(%s,%s,ST_GeomFromGeoJSON(%s))""" ,(str(co_ord),str(i),json.dumps(geom)))
            buffer.append(dict(type="Feature", geometry=geom, properties=atr)) 
            clipshp.append(dict(geometry=geom)) 
       

        # write the GeoJSON file
        geojson1 = open(cwd+"/geojson/ClipGo_{}.geojson".format(str(i)), "w")
        #clipshp.append(buffer)
        geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
        geojson1.close()
        ii = ii +1
        

        connection.commit()

        # cursor.close()

        # connection.close()
    return jsonify(clipshp)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=5004)
