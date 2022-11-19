###for multiple sourec and one destination for visibility analysis
import os
import sys
import time
import shutil
from osgeo import ogr
from collections import defaultdict
import operator
new_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python3.6/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms', '/home/bisag/.local/lib/python3.6/site-packages/IPython/extensions']

for i in new_path:
    sys.path.append(i)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os.path
from qgis.core import (QgsFeature,QgsGeometry,QgsPointXY,QgsField,QgsRaster,QgsVectorFileWriter,QgsRasterLayer,QgsApplication,QgsProject,QgsVectorLayer, QgsVectorLayer,QgsCoordinateReferenceSystem)
QgsApplication.setPrefixPath('/usr', True) #for avoiding "Application path not initialized"
qgs = QgsApplication([],False)
qgs.initQgis()
from qgis import processing
from qgis.analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#########
cwd = "/home/bisag/Music/webMobility"
bfrDis = 0.005
grd = cwd+'/geojson/mobility_grid_geojson/'
savePath = cwd+'/geojson/multisource'
procCorr = cwd+'/geojson/allgrid.geojson'
###########

mxPntRtWise = 3 ##var
norouteSee = 3 ###var

path3 = cwd+'/vis_viewshed/output/vshedGeojson/'

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

# gid = []###for save layer
# for feat in temp.getFeatures():
#     gid.append(feat['gid'])
    
# gd = str(gid[0])
svpath = 'multisource'
print("save path: ",svpath)

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
            gd = 1
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
        f.write(str(d2))
        f.write('\n\n')
        f.write(str(sorted_d)) 
        f.write('\n\n')
        f.write(str(dlen1)) 
        f.write('\n\n')
        f.write(str(sumrouteVshed)) 
        f.write('\n\n')
        f.write(str(vshedCoord)) 
        f.write('\n\n')
        f.write(str(d1)) 

    print(f'Generated max visibility analysis point in {time.time() - start} (second)')
    log1.write(f'Generated max visibility analysis point in {time.time() - start} (second)'+'\n')
    log1.close()
if __name__ == "__main__":
    visibilityAnalysis()
    