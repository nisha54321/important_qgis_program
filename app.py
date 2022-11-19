from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
qgis_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/home/bisag/.local/lib/python3.8/site-packages', '/usr/local/lib/python3.8/dist-packages', '/usr/lib/python3/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python']
for i in qgis_path:
    sys.path.append(i)
import math, json 
import os
import time
import re, os.path
from osgeo import gdal
from osgeo import ogr
import uuid
import shapefile

from qgis import processing
from qgis.core import (QgsPointXY,QgsApplication,QgsVectorLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsVectorFileWriter)

from qgis.analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())


#import processing           
#from processing.core.Processing import Processing           
# Processing.initialize()

#src_filename = '/home/bisag/India_Viewshed/viewshed_output.tif'
#dst_filename = '/home/bisag/India_Viewshed/viewshed_output.geojson'
#dst_filename = "/home/bisag/India_Viewshed/" +uuid.uuid4()+".geojson" 

cwd = "/home/bisag/India_Viewshed"

app = Flask(__name__)
CORS(app)

def shape_publish(file_name,req_uuid):#this function filters _goArea with only records having attribute value=1
#This allows to remove the boundary polygon
#we output to the same shapefile.
    _goArea = cwd+"/output/"+req_uuid+"_goArea.shp"
    onlyGoViewshed.append(_goArea)

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
    w = shapefile.Writer(_goArea,shapeType)
    w.fields = rFields
    for shaperec in outlist:
        record = shaperec.record[0]
        if record == 1:
            w.record(record)
            w.shape(shaperec.shape)
    print("non boundry file success:")
    w.close()


def filter_geojson(tif_file,req_uuid):
    #this converts the viewshed tif to geojson, returns the required geojson
    gdal.AllRegister()
    argv = gdal.GeneralCmdLineProcessor(sys.argv)
    if argv is None:
        sys.exit(0)
    
    dst_layername = 'out'
    dst_fieldname = 'DN'
    dst_field = -1
    geojson_path = "/home/bisag/India_Viewshed/geojson/"+req_uuid+"_viewshed.geojson"
    #print(f"reading raster {output_tif_list[-1]}")
    src_ds = gdal.Open(tif_file)
    srcband = src_ds.GetRasterBand(1)
    drv = ogr.GetDriverByName('GeoJSON')
    dst_ds = drv.CreateDataSource(geojson_path)
    frmt = 'GeoJSON'
    maskband = None

    try:
        dst_layer = dst_ds.GetLayerByName(dst_layername)
    except:
        dst_layer = None

    if dst_layer is None:

        srs = src_ds.GetSpatialRef()
        dst_layer = dst_ds.CreateLayer(dst_layername, geom_type=ogr.wkbPolygon, srs=srs)
        fd = ogr.FieldDefn(dst_fieldname, ogr.OFTInteger)
        dst_layer.CreateField(fd)
        dst_field = 0
    else:
        if dst_fieldname is not None:
            dst_field = dst_layer.GetLayerDefn().GetFieldIndex(dst_fieldname)
            if dst_field < 0:
                print("Warning: cannot find field '%s' in layer '%s'" % (dst_fieldname, dst_layername))

    result = gdal.Polygonize(srcband, maskband, dst_layer, dst_field, [], callback=None)

    dst_ds.Destroy()

    fread = open(geojson_path,'r')
    from json import load
    fcontent = load(fread)
    # print(fcontent['features'])
    dn_0 = list(filter(lambda x: x['properties']['DN'] == 0, fcontent['features']))
    dn_1 = list(filter(lambda x: x['properties']['DN'] == 1, fcontent['features']))
    dn_255 = list(filter(lambda x: x['properties']['DN'] == 255, fcontent['features']))
    fcontent['features'] = dn_1
    fread.close()
    return fcontent



def tif_path(input_coord):
    min_dist_original = 360. # distance is in degree decimal
    min_dist_degree_plus1_plus1 = 360. # distance is in degree decimal
    file_id_original = 0 # file_id is in range: 1-256
    file_id_degree_plus1_plus1 = 0 # file_id is in range: 1-289

    def dist(p,q):
        return math.sqrt(sum((px - qx) ** 2.0 for px, qx in zip(p, q)))

    #now we will compute nearest distance from two dictionary collections
    grid_original = open(cwd + r'/grid_centroids_original.geojson','r')
    read = grid_original.read()
    content = json.loads(read)
    for i in content['features']:
        this_distance = dist(input_coord, i['geometry']['coordinates'])
        if (min_dist_original >= this_distance):
            min_dist_original = this_distance
            file_id_original = i['properties']['id']

    #print(file_id_original)

    grid_degree_plus1_plus1 = open(cwd + r'/grid_centroids_degree_plus1_plus1.geojson','r')
    read = grid_degree_plus1_plus1.read()
    content = json.loads(read)
    for i in content['features']:
        this_distance = dist(input_coord, i['geometry']['coordinates'])
        if (min_dist_degree_plus1_plus1 >= this_distance):
            min_dist_degree_plus1_plus1 = this_distance
            file_id_degree_plus1_plus1 = i['properties']['id']

    #print(file_id_degree_plus1_plus1)

    if (min_dist_degree_plus1_plus1 >= min_dist_original):
        return(cwd + r'/grid_original_tif/'+str(file_id_original)+'.tif')
    else:
        return(cwd + r'/grid_degree_plus1_plus1_tif/'+str(file_id_degree_plus1_plus1)+'.tif')


@app.route('/',methods=['GET'])
def index():
    req_uuid = str(uuid.uuid4())
    co_ord = request.args.get('coordinateXY')#this should always take as lon,lat
    #Put a validation for correct co-ordinate (within range)
    xy = co_ord + " [EPSG:4326]"
    xy_float = [float(co_ord.split(',')[0]),float(co_ord.split(',')[1])]
    #dempath = "/home/user/Documents/1DEM/asterDem.tif"
    dempath =  tif_path(xy_float)
    rad1 = request.args.get('radius1')#this is the
    rad2 = request.args.get('radius2')
    rad3 = request.args.get('radius3')#this is the largest
    azimuth = request.args.get('azimuth')
    bearing = request.args.get('bearing')
    sectorwidth = request.args.get('sectorwidth')
    #Put a validation for the above parameters, if anyone of the paramter is not present, do not continue
    radius = [rad1, rad2, rad3]
    #print(dempath)
    #for viewshed using grass 
    Processing.initialize()
    viewpoint_output = cwd+"/output/"+ req_uuid +"_viewpoint.shp"
    vl = QgsVectorLayer("Point?crs=EPSG:4326", "ViewPoint", "memory")
    f = QgsFeature()
    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(xy_float[0],xy_float[1])))
    pr = vl.dataProvider()
    pr.addFeature(f)
    QgsVectorFileWriter.writeAsVectorFormat(vl, viewpoint_output, "UTF-8", vl.crs() , "ESRI Shapefile")

    go1 = []
    nogo1 = []
    onlyGoViewshed = []
    arcshp = []
    
    # Processing.updateAlgsList()
    #print(dempath + " " + xy +  " " + rad + " "+ src_filename)
    
    # if i is None:
    #     continue 
    #print(f"started r.viewshed with radius {i}")
    tif_file = cwd + r"/tif/" + req_uuid + "_viewshed.tif"
    #print(tif_file)
    processing.run("grass7:r.viewshed", {'input':dempath,
    'coordinates': xy,
    'observer_elevation':1.75,
    'target_elevation':0,
    'max_distance': rad3,#we generate the viewshed for the outermost radius
    'refraction_coeff':0.14286,
    'memory':1500,
    '-c':False, '-r':False, '-b':True, '-e':False,
    'output':tif_file,
    'GRASS_REGION_PARAMETER':None,
    'GRASS_REGION_CELLSIZE_PARAMETER':0,
    'GRASS_RASTER_FORMAT_OPT':'',
    'GRASS_RASTER_FORMAT_META':''})
    
    retval = filter_geojson(tif_file,req_uuid)

    polygonshp = cwd+"/output/"+ req_uuid +"_viewshed.shp"

    ###tiff to shape
    polygonize1 = processing.run("gdal:polygonize", {'INPUT':tif_file,
                    'BAND':1,
                    'FIELD':'DN',
                    'EIGHT_CONNECTEDNESS':False,
                    'EXTRA':'',
                    'OUTPUT':polygonshp})
    ipgo_nogo = polygonize1["OUTPUT"]

    ###############33remove boundry 
    shape_publish(polygonshp, req_uuid)

    id = 0

    for i in radius:    
        ####################create arc shape
        my_rad = i/111111#raidus is in meter, it is converted into DMS
        #print("rad,azimuth shape:",rad,Azimuth)
        arc = processing.run("native:wedgebuffers",
            {'INPUT':viewpoint_output,
            'AZIMUTH':azimuth,
            'WIDTH':sectorwidth,
            'OUTER_RADIUS':my_rad,
            'INNER_RADIUS':0,
            'OUTPUT':cwd+"/output/"+req_uuid+"_"+str(i)+"_"+str(id)+"_arc.shp"})
          
        arcShape = arc["OUTPUT"]
        arcshp.append(arcShape)

        ####clip go area
        ##go area
        
        processing.run("native:clip", 
                        {'INPUT':onlyGoViewshed[id],
                        'OVERLAY':arcShape,
                        'OUTPUT':cwd+"/goarea/"+req_uuid+"_ClipGo_{}.shp".format(id)})
        ii = ii +1
        
        #c##################clip nogo area with arc
        clip = processing.run("native:clip", 
                        {'INPUT':ipgo_nogo,
                        'OVERLAY':arcShape,
                        'OUTPUT':cwd+"/output/"+req_uuid+"_ClipGo_nogo"+str(id)+".shp"})
        
        arcShape1 = clip["OUTPUT"]

        ############area find
        area = processing.run("native:fieldcalculator", 
                    {'INPUT':arcShape1,
                    'FIELD_NAME':'area',
                    'FIELD_TYPE':0,
                    'FIELD_LENGTH':0,
                    'FIELD_PRECISION':0,
                    'FORMULA':'$area',
                    'OUTPUT':cwd+"/clip/"+req_uuid +"_"+str(id)+"_ClipArea.shp"})
                    
        area1 = QgsVectorLayer(area["OUTPUT"], "nogoClip", "ogr")#LayerPath,LayerName,LayerDriver

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

        #data = [nogo, go]

        #label = ['nogo', 'go']

        #fig = plt.figure(figsize =(10, 5))
        #plt.pie(data,labels=label,autopct='%1.1f%%')

        #plt.legend(title = "percentage")
        #plt.title('Area percentage for '+str(i)+" radius")
        #plt.show()
        id += 1

    # print("First")
    #print(retval)
    #processing.run("native:clip", {'INPUT':QgsProcessingFeatureSourceDefinition('Input_1.geojson', selectedFeaturesOnly=False, featureLimit=-1, flags=QgsProcessingFeatureSourceDefinition.FlagOverrideDefaultGeometryCheck, geometryCheck=QgsFeatureRequest.GeometrySkipInvalid),'OVERLAY':QgsProcessingFeatureSourceDefinition('Input_2.geojson', selectedFeaturesOnly=False, featureLimit=-1, flags=QgsProcessingFeatureSourceDefinition.FlagOverrideDefaultGeometryCheck, geometryCheck=QgsFeatureRequest.GeometrySkipInvalid),'OUTPUT':'Output_2.geojson'})
    print(retval)
    print(nogo1)
    print(go1)
    return jsonify([retval,nogo1, go1])


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
