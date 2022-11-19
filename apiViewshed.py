import sys
import os 
import uuid
import shapefile
from matplotlib import pyplot as plt

qgis_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder/extlibs', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis2web', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms']

for i in qgis_path:
    sys.path.append(i)

from qgis import processing
from qgis.core import (QgsPointXY,QgsApplication,QgsVectorLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsVectorFileWriter)

from qgis.analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

############### user input 
coorx,coory = 71.51459076930828, 20.9079174228675
Azimuth = 90
Wedge = 60
    
xy = str(coorx) +","+str(coory) + " [EPSG:4326]"
radius_list = [1000,800,500]

cwd = "/home/bisag/Documents/webViewShed"
dempath = cwd+'/asterDem.tif'
output_tif_list = []
output_list = []

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
x = iter(radius_list)

def shape_publish(file_name):
    y = next(x)

    notbounshp = cwd+"/output/"+"goArea_"+str(y)+".shp"
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

##viewpoint create
vl = QgsVectorLayer("Point?crs=EPSG:4326", "ViewPoint", "memory")
f = QgsFeature()
f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx,coory)))
pr = vl.dataProvider()
pr.addFeature(f)
QgsVectorFileWriter.writeAsVectorFormat(vl, cwd+"/output/viewpoint.shp", "UTF-8", vl.crs() , "ESRI Shapefile")

go1 = []
nogo1 = []
ii = 0
for i in radius_list:
    tif_file = cwd+"/tif/"+ str(i)+".tif"

    processing.run("grass7:r.viewshed", {'input':dempath,
                'coordinates':xy,
                'observer_elevation':1.75,
                'target_elevation':0,
                'max_distance':i ,
                'refraction_coeff':0.14286,
                'memory':500,
                '-c':False,
                '-r':False,
                '-b':True,
                '-e':False,
                'output':tif_file,
                'GRASS_REGION_PARAMETER':None,
                'GRASS_REGION_CELLSIZE_PARAMETER':0,
                'GRASS_RASTER_FORMAT_OPT':'',
                'GRASS_RASTER_FORMAT_META':''})
                
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
    rad = i/111111
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
    processing.run("native:clip", 
                    {'INPUT':onlyGoViewshed[ii],
                    'OVERLAY':arcShape,
                    'OUTPUT':cwd+"/goarea/"+ "ClipGo_{}.shp".format(i)})
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
    
    print("radius",str(i)," :nogo percentage",nogo)
    print("radius",str(i)," :go percentage",go)

    
print("success")
print("go:",go1)
print("nogo:",nogo1)