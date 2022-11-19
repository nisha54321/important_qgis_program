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


import uuid

app = Flask(__name__)
CORS(app)


output_tif_list = []

cwd = "/home/bisag/ViewShade"
############### user input 
Azimuth = 90
Wedge = 60
    
radius_list =[]
yy = iter(radius_list)
gjsonPath = []

####
###########remove all files if existing
mypath1 = cwd+"/nogoarea/"
mypath2 = cwd+"/tifweb/"
mypath3 = cwd+"/output/"
mypath4 = cwd+"/goarea/"

l = [mypath1,mypath2,mypath3,mypath4]

for delfol in l:
    for root, dirs, files in os.walk(delfol):
        for file in files:
            os.remove(os.path.join(root, file))

##############remove boundry
onlyGoViewshed = []
arcshp = []
clipshp =[]
def shape_publish(file_name):
    #y = next(yy)

    notbounshp = cwd+"/output/"+"goArea_"+str(uuid.uuid4())+".shp"
    onlyGoViewshed.append(notbounshp)

    r = shapefile.Reader(file_name)
    outlist = []
    for shaperec in r.iterShapeRecords():
        outlist.append(shaperec)
    shapeType =  r.shapeType
    rFields = list(r.fields)
    r = None
    if os.path.exists(file_name):
        pass
    else:
        print("file does not exist"+ file_name)
    dbf_file = file_name.replace(".shp",".dbf")
    if os.path.exists(dbf_file):
        pass
    else:
        print("file does not exist" + dbf_file)
    shx_file = file_name.replace(".shp", ".shx")
    if os.path.exists(shx_file):
        pass
    else:
        print("file does not exist" + shx_file)
    w = shapefile.Writer(notbounshp,shapeType)
    w.fields = rFields
    for shaperec in outlist:
        record = shaperec.record[0]
        if record == 1:
            w.record(record)
            w.shape(shaperec.shape)
    print("non boundry file success:")
    w.close()

####
@app.route('/',methods=['GET'])
def index():
    output_list = []
    co_ord = request.args.get('cordinate')

    coorx,coory= [float(i)for i in co_ord.split(", ")]
    vl = QgsVectorLayer("Point?crs=EPSG:4326", "ViewPoint", "memory")
    f = QgsFeature()
    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx,coory)))
    pr = vl.dataProvider()
    pr.addFeature(f)
    QgsVectorFileWriter.writeAsVectorFormat(vl, cwd+"/output/viewpoint.shp", "UTF-8", vl.crs() , "ESRI Shapefile")

    xy = co_ord + " [EPSG:4326]"
    dempath = cwd+'/asterDem.tif'

    rad = request.args.get('radius')
    rad2 = request.args.get('radius1')
    rad3 = request.args.get('radius2')

    radius_list.append(rad3)
    radius_list.append(rad2)
    radius_list.append(rad)

    print(radius_list)

    Processing.initialize()
    ii = 0
    go1 = []
    nogo1 = []
    for i in radius_list:
        tif_file = cwd+"/tifweb/"+str(i)+".tif"
    #     rn = next(rname1)
        processing.run("grass7:r.viewshed", {'input':dempath,
                'coordinates': xy,
                'observer_elevation':1.75,
                'target_elevation':0,
                'max_distance': i,
                'refraction_coeff':0.14286,
                'memory':1500,
                '-c':False,
                '-r':False,
                '-b':True,
                '-e':False,
                'output':tif_file,
                'GRASS_REGION_PARAMETER':None,
                'GRASS_REGION_CELLSIZE_PARAMETER':0,
                'GRASS_RASTER_FORMAT_OPT':'',
                'GRASS_RASTER_FORMAT_META':''})
        output_tif_list.append(tif_file)
        retval = filter_geojson()
        output_list.append(retval)
        #########################arc shape for
        polygonshp = cwd+"/output/{}Go_Nogo.shp".format(i)
    
        ###tiff to shape
        polygonize1 = processing.run("gdal:polygonize", {'INPUT':tif_file,
                        'BAND':1,
                        'FIELD':'DN',
                        'EIGHT_CONNECTEDNESS':False,
                        'EXTRA':'',
                        'OUTPUT':polygonshp})
        ipgo_nogo = polygonize1["OUTPUT"]

        fixGeom = cwd+"/output/{}fixGo_Nogo.shp".format(i)

        f_geom = processing.run("native:fixgeometries", 
                {'INPUT':ipgo_nogo,
                'OUTPUT':fixGeom})
        f_geom_res = f_geom["OUTPUT"]


        ###############33remove boundry 
        shape_publish(f_geom_res)
        output_tif_list.append(tif_file)
        
        ####################create arc shape
        rad = int(i)/111111
        print("rad,azimuth shape:",rad,Azimuth)
        arc = processing.run("native:wedgebuffers",
            {'INPUT':cwd+"/output/viewpoint.shp",
            'AZIMUTH':Azimuth,
            'WIDTH':Wedge,
            'OUTER_RADIUS':rad,
            'INNER_RADIUS':0,
            'OUTPUT':cwd+"/output/"+ str(i)+"arc.shp"})
            
        arcShape = arc["OUTPUT"]
        arcshp.append(arcShape)

        ####clip go area
        ##go area
        print("clipp",onlyGoViewshed[ii])
        goclip = processing.run("native:clip", 
                        {'INPUT':onlyGoViewshed[ii],
                        'OVERLAY':arcShape,
                        'OUTPUT':cwd+"/goarea/"+ "ClipGo_{}.shp".format(i)})
        ##convert geojson
        reader = shapefile.Reader(goclip["OUTPUT"])
        fields = reader.fields[1:]
        field_names = [field[0] for field in fields]
        buffer = []

        for sr in reader.shapeRecords():
            atr = dict(zip(field_names, sr.record))
            geom = sr.shape.__geo_interface__
            buffer.append(dict(type="Feature", \
            geometry=geom, properties=atr)) 

        # write the GeoJSON file
        geojson1 = open(cwd+"/geojson/ClipGo_{}.geojson".format(str(i)), "w")
        clipshp.append({"type": "FeatureCollection", "features": buffer})
        geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
        geojson1.close()
        ii = ii +1
        
        #c##################clip nogo area with arc
        clip = processing.run("native:clip", 
                        {'INPUT':f_geom_res,
                        'OVERLAY':arcShape,
                        'OUTPUT':cwd+"/output/"+ "ClipGo_nogo"+str(i)+".shp"})
        
        arcShape1 = clip["OUTPUT"]

        ############area find
        area = processing.run("native:fieldcalculator", 
                    {'INPUT':arcShape1,
                    'FIELD_NAME':'area',
                    'FIELD_TYPE':0,
                    'FIELD_LENGTH':0,
                    'FIELD_PRECISION':0,
                    'FORMULA':'$area',
                    'OUTPUT':cwd+"/nogoarea/"+ str(i)+"_ClipArea.shp"})
                    
        area1 = QgsVectorLayer(area["OUTPUT"], "nogoClip", "ogr")

        ###############find the percentage of go and nogo area
        features = area1.getFeatures()
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

        sg = sum(go)
        go = (sg *100)/t

        nogo = 100 - go
        
        go1.append(go)
        nogo1.append(nogo)
        
        
    description = "{radius:(goarea,nogoarea)}"
    percentage = dict(zip(radius_list, zip(go1, nogo1)))
    #clipshp,output_list
    return jsonify(clipshp,description,percentage)



if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=5004)
