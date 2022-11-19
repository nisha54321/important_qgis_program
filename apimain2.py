import os
from osgeo import osr
from json import dumps
import sys
import shapefile
import time
import shutil
from osgeo import ogr
import os
from collections import defaultdict
from itertools import chain
import operator
import re
import uuid##hello

new_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python3.6/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms', '/home/bisag/.local/lib/python3.6/site-packages/IPython/extensions']

for i in new_path:
    sys.path.append(i)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os.path
from qgis.core import (QgsFeature,QgsGeometry,QgsPointXY,QgsField,QgsRaster,QgsVectorFileWriter,QgsRasterLayer,QgsApplication,QgsProject,QgsVectorLayer, QgsVectorLayer,QgsCoordinateReferenceSystem,QgsProcessingFeatureSourceDefinition,QgsFeatureRequest)
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
output_folder = cwd+'/output'
bfrDis = 0.005
grd = cwd+'/geojson/mobility_grid_geojson/'
procCorr = grd+"/Mobility_Grid2.geojson"
mxPntRtWise = 3 ##var
norouteSee = 3 ###var
path3 = cwd+'/vis_viewshed/output/vshedGeojson/'
linepath = cwd+'/geojson/LINE.geojson'
dis = '5000'


#remove all files
mypath1 = cwd+"/shapefile/"
mypath2 = cwd+"/buffer/"
mypath3 = cwd+"/output/"
mypath4 =cwd+"/distance/"

l = [mypath1,mypath2,mypath3,mypath4]
for delfol in l:
    for root, dirs, files in os.walk(delfol):
        for file in files:
            os.remove(os.path.join(root, file))

# mypath = cwd+"/geojson/"
# for root, dirs, files in os.walk(mypath):
#         for file in files:
#             if file.endswith(".geojson"):
#                 os.remove(os.path.join(root, file))

# g =[]
# for root, dirs, files in os.walk(grd):
#     for file in files:
#         if file.endswith(".geojson") and file.startswith("Mobility_Grid"):
#             g.append(os.path.join(root, file))
#             #os.remove(os.path.join(root, file))

############background run algorithm
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

gid = []###for save layer
for feat in temp.getFeatures():
    gid.append(feat['gid'])
    
gd = str(gid[0])
svpath = 'mobility_'+gd
print("save path: ",svpath)

wktfix = processing.run("native:fixgeometries",
                         {'INPUT':cwd+'/mobility_wkt1.geojson',
                         'OUTPUT':cwd+'/new/mobility_wkt1.geojson'})

clip1 = processing.run("native:clip",
                {'INPUT':wktfix['OUTPUT'],
                'OVERLAY':temp,
                'OUTPUT':cwd+'/new/clip.shp'})

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
                        'OUTPUT':cwd+'/output/convertMapRaster.tif'})
res4 = processing.run("gdal:cliprasterbyextent", 
                        {'INPUT':res3['OUTPUT'],
                        'PROJWIN':ex1,
                        'NODATA':None,
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'EXTRA':'',
                        'OUTPUT':cwd+'/output/convertMapRasterClip.tif'})

processing.run("gdal:rearrange_bands",
                        {'INPUT':res4['OUTPUT'],
                        'BANDS':[1],
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'OUTPUT':cwd+'/output/singleband.tif'})
                        
reclass = processing.run("native:reclassifybytable",
            {'INPUT_RASTER':cwd+'/output/singleband.tif',
            'RASTER_BAND':1,
            'TABLE':[0,38,1,38,255,2],
            'NO_DATA':-9999,
            'RANGE_BOUNDARIES':0,
            'NODATA_FOR_MISSING':False,
            'DATA_TYPE':5,
            'OUTPUT':cwd+'/recassify.tif'})

##find elevation profile
def elevation():
    os.system(f"python3 {cwd}/elevation_profile.py")#var
    #os.system(f"eog /home/bisag/Music/webMobility/elevation_profile.png")

input = cwd+'/recassify1.tif'
def shortest_path():
    start = time.time()
    log1 = open(cwd+'/log.txt','a')

    
    lat_long_list = open(cwd+"/lat_long_list.txt",'r')
    content = lat_long_list.read()
    content = content.split(",")
    xy = [float(content[0].strip()),float(content[1].strip()),float(content[2].strip()),float(content[3].strip())]
    lat_long_list.close()

    print(xy)
    os.system(f"python3 {cwd}/shortest_path.py {xy[-4]} {xy[-3]} {xy[-2]} {xy[-1]}")#####3change shortest_path.py (input = cwd+'/recassify1.tif')
    elevation()

    ############convert to geojson and shape file
    f = open(cwd+"/path.txt", "r")
    x = f.read()
    f.close()

    wkt = x.split("\n")
    wkt = [i for i in wkt if i]#remove empty string

    print(len(wkt))

    spatialref = osr.SpatialReference()
    spatialref.ImportFromProj4('+proj=longlat +datum=WGS84 +no_defs')

    driver = ogr.GetDriverByName("ESRI Shapefile")
    c= 1

    for wktval in wkt:

        ###################convert shp
        input_folder = cwd+"/shapefile/line{}.shp".format(str(c))

        dstfile = driver.CreateDataSource(input_folder)
        dstlayer = dstfile.CreateLayer("line", spatialref, geom_type=ogr.wkbLineString)
        fielddef = ogr.FieldDefn("ID", ogr.OFTInteger)
        fielddef.SetWidth(10)
        dstlayer.CreateField(fielddef)
        poly = ogr.CreateGeometryFromWkt(wktval)
        feature = ogr.Feature(dstlayer.GetLayerDefn())
        feature.SetGeometry(poly)
        feature.SetField("ID", 0)
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
            ####

            print("length is (m):",len1)
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
                line.append(dict(type="Feature", geometry=geom, properties=atr))
            except Exception as e:
                print(e)
        for sr in reader.shapeRecords():
            atr = dict(zip(field_names, sr.record))
            try:
                geom = sr.shape.__geo_interface__
                if geom['type'] == 'LineString':
                    atr['length(m)'] = len1

                line.append(dict(type="Feature", \
                geometry=geom, properties=atr)) 
            except Exception as e:
                print(e)

        # write the GeoJSON file
        op = cwd+'/geojson'

        geojson11 = open(op+"/"+svpath+"/line{}.geojson".format(str(c)), "w")
        geojson11.write(dumps({"type": "FeatureCollection", "features": line}, indent=2) + "\n")
        geojson11.close()

        processing.run("native:buffer", ##500 meter
                    {'INPUT':input_folder,
                    'DISTANCE':0.0021,
                    'SEGMENTS':5,
                    'END_CAP_STYLE':0,
                    'JOIN_STYLE':0,
                    'MITER_LIMIT':2,
                    'DISSOLVE':False,
                    'OUTPUT':cwd+"/buffer"+'/buffer{}.shp'.format(str(c))})

        ########### Buffer to geojson
        reader = shapefile.Reader(cwd+"/buffer"+'/buffer{}.shp'.format(str(c)))
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
        geojson1 = open(op+"/"+svpath+"/Buffer_line{}.geojson".format(str(c)), "w")
        geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
        geojson1.close()
        print("successs")
 
        c = c+1
    print(f'Generated 5 paths in {time.time() - start}s')
    log1.write(f'Generated 5 paths in {time.time() - start}s'+'\n')
    log1.close()
  
###for visibility analysis
def visibilityAnalysis():
    
    log1 = open(cwd+'/log.txt','a')
    ########## remove layer#"/"+svpath+
    p1 = cwd+f'/geojson/{svpath}/viewshed'
    p3 = cwd+f'/plugin'
    p4 = cwd+f'/geojson/{svpath}/maxpointvshed'
    l = [p1,p3,p4]
    for delfol in l:
        for root, dirs, files in os.walk(delfol):
            for file in files:
                os.remove(os.path.join(root, file))

    highpointpath = cwd+'/viewshed/layer/First High.shp'

    log1.write("VISIBILITY ANALYSIS::\n")
    start = time.time()

    print('extent is:',ex1)
    log1.write('extent:'+str(ex1)+"\n")

    res2 =processing.run("native:clip", 
                {'INPUT':cwd+'/vis_viewshed/grid.shp',
                'OVERLAY':procCorr,
                'OUTPUT':cwd+'/gridvs.shp'})

    highpointpath = cwd+'/vis_viewshed/vshedPoints.shp'
    ###### clip point using selected corridor
    res3 =processing.run("native:clip", 
                {'INPUT':highpointpath,
                'OVERLAY':res2["OUTPUT"],
                'OUTPUT':cwd+'/plugin/clipPoint.shp'})

    ###intersection first high point and grid (2000*2000)
    intersect = processing.run("native:intersection",
        {'INPUT':res3["OUTPUT"],
        'OVERLAY':res2["OUTPUT"],
        'INPUT_FIELDS':[],'OVERLAY_FIELDS':[],
        'OVERLAY_FIELDS_PREFIX':'',
        'OUTPUT':cwd+"/plugin/intersectclip.shp"})

    vshedCoord ={}
    #####################find grid wise max raster value
    shapefile1 = intersect["OUTPUT"]
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shapefile1, 0)
    layer = dataSource.GetLayer()
    d = defaultdict(list)
    id1 =[]
    roadrail1 = []
    for feature in layer:
        id = feature.GetField("id")
        id = float(id)
        id = int(id)
        id1.append(str(id))
        geom = str(feature.GetGeometryRef())
        geom = geom.replace("MULTIPOINT (","")
        geom = geom.replace(")","")
        vshedCoord[str(id)] = str(geom)
        i1 = path3+f'vs_{id}.geojson'
        roadrail1.append(i1)
                    
    print('id',id1) 
    
    m = processing.run("native:mergevectorlayers", 
        {'LAYERS':roadrail1,
        'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
        'OUTPUT':cwd+f"/geojson/{svpath}/vieshed.geojson"})

    mergeviewshed = processing.run("native:fixgeometries",
                    {'INPUT':m['OUTPUT'],
                    'OUTPUT':cwd+f"/geojson/{svpath}/mergevieshed.geojson"})

    ###################### merge 5 line
    linepath = cwd+f"/geojson/{svpath}"
    roadrail2 = []
    for file in os.listdir(linepath):
        if file.startswith("line") and file.endswith(".geojson"):
            fpath = os.path.join(linepath, file)
            roadrail2.append(fpath)
            
    mergeline = processing.run("native:mergevectorlayers", 
        {'LAYERS':roadrail2,
        'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
        'OUTPUT':cwd+f"/geojson/{svpath}/mergeLine.geojson"})
        
    layer.ResetReading()

    #=======================VISIBILITI ANALYSIS=====================================
    rtInvshed = processing.run("native:intersection", 
                {'INPUT':mergeline['OUTPUT'],
                'OVERLAY':mergeviewshed['OUTPUT'],
                'INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'',
                'OUTPUT':cwd+'/plugin/rtInVshed.shp'})

    ####################all route length find inside viewshed
    rlen = processing.run("native:fieldcalculator", 
            {'INPUT':rtInvshed['OUTPUT'],
            'FIELD_NAME':'len1',
            'FIELD_TYPE':0,
            'FIELD_LENGTH':0,
            'FIELD_PRECISION':0,
            'FORMULA':'round($length,2)',#
            'OUTPUT':cwd+'/plugin/routeVieshed.shp'
            })

    ##### for how many lines layer inside perticular viewshed layer      
    shapefile1 = rlen['OUTPUT']
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shapefile1, 0)
    layer = dataSource.GetLayer()
    d = defaultdict(list)
    dlen = defaultdict(list)

    for feature in layer:
        l = feature.GetField("layer")#line
        vs = feature.GetField("layer_2")#vieshed name
        ln = feature.GetField("len1")#length of line
        d[vs].append(l)
        dlen[vs].append(ln)

    d1 = dict(d)
    dlen1 = dict(dlen)

    d2 = {}
    lenroute = {}
    sumrouteVshed = {}
    ########### sum of all lines inside perticular vieshed
    for i in d1:
        v = d1[i]
        rl = dlen[i]    
        sumrouteVshed[i]= sum(rl)

        res = []
        [res.append(x) for x in v if x not in res]
        d2[i]= res
        lenroute[i]= len(res)

    #### max (num)route inside particular viewshed (priority wise) 
    sorted_d = dict( sorted(lenroute.items(), key=operator.itemgetter(1),reverse=True))##first n viewshed include maximum route
    
    names = set(sorted_d.values())
    d3 = {}
    for n in names:
        d3[n] = [k for k in sorted_d.keys() if sorted_d[k] == n]

    d33 = dict(sorted(d3.items(), reverse=True))

    l = {4,2}####if you see only this route covor points
    l ={key: d33[key] for key in d33.keys() & l}

    d3 = dict(list(d33.items())[:norouteSee])####sort dictionary route wise(5,4,3 route)
    vshedname =[]
    for i in d3:
        vnmlist = d3[i]
        sumlenmain =[sumrouteVshed[i]for i in vnmlist]
        sumlen =[sumrouteVshed[i]for i in vnmlist]    
        sumlen.sort(reverse=True)
        sumlen = sumlen[:mxPntRtWise]
        x = [sumlenmain.index(i)for i in sumlen]
        y = [vnmlist[i]for i in x]
        c = [vshedname.append(i)for i in y]  

    visvshed = vshedname
    print(visvshed)
    log1.write('final coordinates::'+str(visvshed)+'\n')

    iii = 0
    vis = QgsVectorLayer("Point?crs=EPSG:4326", "visibility Analysis", "memory")

    for i in visvshed:
        try:
            #print(i)
            shutil.copy(cwd+f'/vis_viewshed/output/vshedGeojson/{i}.geojson', cwd+f'/geojson/{svpath}/maxpointvshed/')#move folder
            
            kk = i.split("_")
            #print(kk[1])

            maxCoord =vshedCoord[kk[1]]
            ll = sumrouteVshed[i]
            ll = round(ll,1)

            y = maxCoord.split(' ')
            noofrout = lenroute[i]
            print(maxCoord," len :",ll,'no of route',noofrout)

            f = QgsFeature()#
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(y[0]), float(y[1]))))
            pr = vis.dataProvider()

            #Add Attribute
            vis.startEditing()
            pr.addAttributes([QgsField("id", QVariant.String),QgsField("vid", QVariant.String),QgsField("length", QVariant.String),QgsField("num_route", QVariant.String),QgsField("label", QVariant.String),QgsField("elevation", QVariant.String)])

            p = QgsPointXY(float(y[0]), float(y[1]))
            rasterLyr = QgsRasterLayer(cwd+"/40_R_DEM1.tif","Sat Image")
            qry = rasterLyr.dataProvider().identify(p,QgsRaster.IdentifyFormatValue)
            qry.isValid()
            r2 = qry.results()
            print(r2[1])

            label1 = 'route:'+str(noofrout)+',len:'+str(ll)+'(m) ,Ele:'+str(r2[1])
            log1.write('visibility analysis::'+str(label1)+'\n')
            attvalAdd = [str(gd),str(kk[1]),str(ll),str(noofrout),str(label1),str(r2[1])]
            f.setAttributes(attvalAdd)
            vis.triggerRepaint()

            pr.addFeature(f)
            vis.updateExtents() 
            vis.updateFields() 
            vis.triggerRepaint()
            vis.commitChanges()
            
            iii = iii +1
        except Exception as e:
            print(e)
    
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "GeoJSON"
    save_options.fileEncoding = "UTF-8"
    transform_context = QgsProject.instance().transformContext()
    error = QgsVectorFileWriter.writeAsVectorFormatV2(vis,cwd+f"/geojson/{svpath}/ktf.geojson",transform_context,save_options)

    ###save all output into VsAnalysis text file
    with open(cwd+"/VsAnalysis.txt","w") as f:
        f.write(str(d2)+'\n\n')
        f.write(str(sorted_d)+'\n\n') 
        f.write(str(dlen1)) 
        f.write(str(sumrouteVshed)+'\n\n') 
        f.write(str(vshedCoord)+'\n\n') 
        f.write(str(d1)) 

    print(f'Generated max visibility analysis point in {time.time() - start} (second)')
    log1.write(f'Generated max visibility analysis point in {time.time() - start} (second)'+'\n')
    log1.close()

def delayLine():
    dis = '5000'

    print("delayline dis:",dis)
    dis = int(dis)
    dis = str(dis/111000)
    offsetLine = processing.run("native:arrayoffsetlines", 
                {
                'INPUT':linepath,
                'COUNT':3,#no of line
                'OFFSET':dis,#distance
                'SEGMENTS':8,'JOIN_STYLE':0,'MITER_LIMIT':2,
                'OUTPUT':cwd+f'/visPoint/delayLines.shp'})
                
    ##convert Geojson
    reader = shapefile.Reader(offsetLine['OUTPUT'])
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []

    for sr in reader.shapeRecords():
        try:
            atr = dict(zip(field_names, sr.record))
            if atr['instance'] ==1:
                atr['color'] = "red"
                atr['name2'] = "delayLine1"
            elif atr['instance'] ==2:
                atr['color'] = "green"
                atr['name2'] = "delayLine2"
            elif atr['instance'] ==3:
                atr['color'] = "blue"
                atr['name2'] = "delayLine3"

            geom = sr.shape.__geo_interface__
            buffer.append(dict(type="Feature", \
            geometry=geom, properties=atr))

        except Exception as e:
            print(e)
            
    geojson1 = open(cwd+"/geojson/delayLines.geojson", "w")
    geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
    geojson1.close()

    ####all visibility point inside selected corridor

    mjson =cwd+'/geojson'
    s1 ='mobility_'
    gpath =[]
    mxpnt =[]
    try:
        for root, dirs, files in os.walk(grd):
            for file in files:
                if file.endswith(".geojson") and file.startswith("Mobility_Grid"):
                    f1 = os.path.join(root, file)
                    corrNo = re.findall('\d+', f1 )
                    corrNo = corrNo[0]
                    f2 = mjson+'/'+s1+corrNo
                    gpath.append(f2)
                    
        for kk in gpath:            
            for root, dirs, files in os.walk(kk):
                for file in files:
                    if file.endswith(".geojson") and file.startswith("ktf"):
                        f1 = os.path.join(root, file)
                        mxpnt.append(f1)

        m =processing.run("native:mergevectorlayers", 
                        {'LAYERS':mxpnt,
                        'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                        'OUTPUT':cwd+'/geojson/points.geojson'})
                        
        r2 = processing.run("native:deleteduplicategeometries", 
                            {'INPUT':m['OUTPUT'],
                                'OUTPUT':cwd+'/geojson/ktf.geojson'})

        print("delayline and merge max point generated:::")
    except Exception as e:
        print(e)

def kbf():

    id = uuid.uuid4()
    result = processing.run("native:difference", 
        {
            'INPUT':procCorr,
            'OVERLAY':cwd+'/kbf/Greater_then_10_buffer.shp',
            'OUTPUT':cwd+f'/kbf/{id}_KBF.shp'})
    ##convert Geojson
    reader = shapefile.Reader(result['OUTPUT'])
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []

    for sr in reader.shapeRecords():
        try:
            atr = dict(zip(field_names, sr.record))

            atr['name2'] = "kbf"
            geom = sr.shape.__geo_interface__
            buffer.append(dict(type="Feature", \
            geometry=geom, properties=atr))

        except Exception as e:
            print(e)

    geojson1 = open(cwd+f"/geojson/{svpath}/kbf.geojson", "w")
    geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
    geojson1.close()

if __name__ == "__main__":
    shortest_path()
    visibilityAnalysis()
    delayLine()
    kbf()
    
