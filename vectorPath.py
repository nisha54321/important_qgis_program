import os,time
from qgis import processing
from geojson import Point,Feature, FeatureCollection, dump

cwd = r"C:\Users\Administrator\Music\webmobility"

obstacle_layer = r'D:\\test\\1.shp'
nooftank = 5
neighbors = 20
latlongBfr = 0.05#2000 meter

output_folder = os.path.join(cwd,'output')
geo_path = os.path.join(cwd,'geojson1')
file_path = os.path.join(output_folder,'lat_long_list.geojson')

l = [output_folder,geo_path]
for delfol in l:
    for root, dirs, files in os.walk(delfol):
        for file in files:
            os.remove(os.path.join(root, file))

lat_long_list = open(cwd+f"{os.sep}lat_long_list.txt",'r')
content = lat_long_list.read()
content = content.split(",")
xy = [float(content[0].strip()),float(content[1].strip()),float(content[2].strip()),float(content[3].strip())]
lat_long_list.close()

point = Point((float(content[0].strip()),float(content[1].strip())))
point1 = Point((float(content[2].strip()),float(content[3].strip())))
features = []
features.append(Feature(geometry=point,properties={"id": 1}))
features.append(Feature(geometry=point1,properties={"id": 2}))
feature_collection = FeatureCollection(features)
with open(file_path, 'w') as f:
   dump(feature_collection, f)

poinrbuffer = processing.run("native:buffer", {### buffer of point layer
                    'INPUT':file_path,
                    'DISTANCE':latlongBfr,
                    'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,
                    'OUTPUT':output_folder+f'{os.sep}latlongbuffer.geojson'})

START_POINT =f'{xy[-4]},{xy[-3]} [EPSG:4326]'
END_POINT =f'{xy[-2]},{xy[-1]} [EPSG:4326]'

start = time.time()

wktfix = processing.run("native:fixgeometries", 
        {'INPUT':obstacle_layer,
        'OUTPUT':output_folder+f'{os.sep}wktfix.shp'})             

auto_incr_obstcle = processing.run("native:addautoincrementalfield",
               {'INPUT':wktfix['OUTPUT'],
                'FIELD_NAME':'AUTO',                               
                'START':1,
                'GROUP_FIELDS':[],'SORT_EXPRESSION':'','SORT_ASCENDING':True,'SORT_NULLS_FIRST':False,
                'OUTPUT':output_folder+f'{os.sep}wktfixAuto.shp'})

s_path = processing.run("native:shortestline", 
            {'SOURCE':auto_incr_obstcle['OUTPUT'],
            'DESTINATION':auto_incr_obstcle['OUTPUT'],
            'METHOD':0,
            'NEIGHBORS':20,
            'DISTANCE':None,
            'OUTPUT':output_folder+f'{os.sep}path_network1.shp'})
###########################################
layer2 = QgsVectorLayer(s_path['OUTPUT'], "path_network1", "ogr")
#QgsProject.instance().addMapLayer(layer2)

selectloc =processing.run("native:selectbylocation", 
    {'INPUT':layer2,
    'PREDICATE':[7],#cross
    'INTERSECT':auto_incr_obstcle['OUTPUT'],
    'METHOD':0})

with edit(layer2):##delete selected feature
    layer2.deleteSelectedFeatures()
    
wktfix1 = processing.run("native:fixgeometries", 
        {'INPUT':layer2,
        'OUTPUT':output_folder+f'{os.sep}selectFix.shp'})
        
linesub = processing.run("native:linesubstring",
            {
            'INPUT':wktfix1['OUTPUT'],
            'START_DISTANCE':QgsProperty.fromExpression('"distance" /2'),
            'END_DISTANCE':1,
            'OUTPUT':output_folder+f'{os.sep}linesub1.shp'})
            
specificVertex = processing.run("native:extractspecificvertices",
    {
    'INPUT':linesub['OUTPUT'],
    'VERTICES':'0',
    'OUTPUT':output_folder+f'{os.sep}point1.shp'})
    
removeDup = processing.run("native:deleteduplicategeometries",
            {'INPUT':specificVertex['OUTPUT'],
            'OUTPUT':output_folder+f'{os.sep}removeDupPoint.shp'})
            
auto_incr_point = processing.run("native:addautoincrementalfield",
               {'INPUT':removeDup['OUTPUT'],
                'FIELD_NAME':'AUTO1',                               
                'START':1,
                'GROUP_FIELDS':[],'SORT_EXPRESSION':'','SORT_ASCENDING':True,'SORT_NULLS_FIRST':False,
                'OUTPUT':output_folder+f'{os.sep}pointAutoInc.shp'})
points = QgsVectorLayer(auto_incr_point['OUTPUT'], "points", "ogr")
##add source and destination to layer
vpr = points.dataProvider()
n_features = points.featureCount() #added line

s_d_coord = [(xy[0],xy[1]),(xy[2],xy[3])]
f = QgsFeature()

for i in s_d_coord:
    pnt = QgsGeometry.fromPointXY(QgsPointXY(i[0],i[1])) 
    f.setGeometry(pnt)
    vpr.addFeatures([f])

points.updateExtents()
points.triggerRepaint()
points.commitChanges()
QgsProject.instance().addMapLayer(points)                 
shortestpath = processing.run("native:shortestline", 
            {'SOURCE':auto_incr_point['OUTPUT'],
            'DESTINATION':auto_incr_point['OUTPUT'],
            'METHOD':0,
            'NEIGHBORS':neighbors,#change
            'DISTANCE':None,
            'OUTPUT':output_folder+f'{os.sep}path_network2.shp'})


wktfix4 = processing.run("native:fixgeometries", 
        {'INPUT':shortestpath['OUTPUT'],
        'OUTPUT':output_folder+f'{os.sep}path_networkFix2.shp'}) 

###################################
list_path = []
listbuffer_path = []
layer = QgsVectorLayer(wktfix4['OUTPUT'], "path_network2", "ogr")
QgsProject.instance().addMapLayer(layer)

def tankRun(op_path,intersect_path,PREDICATE,bufferpath,diffrencepath):
    
    processing.run("native:selectbylocation", 
        {'INPUT':layer,
        'PREDICATE':PREDICATE,#
        'INTERSECT':intersect_path,
        'METHOD':0})
    
    with edit(layer):##delete selected feature
        layer.deleteSelectedFeatures()
    
    res =processing.run("native:shortestpathpointtopoint",
        {'INPUT':layer,
        'STRATEGY':0,
        'DIRECTION_FIELD':'',
        'VALUE_FORWARD':'',
        'VALUE_BACKWARD':'',
        'VALUE_BOTH':'',
        'DEFAULT_DIRECTION':2,
        'SPEED_FIELD':'',
        'DEFAULT_SPEED':50,
        'TOLERANCE':0,
        'START_POINT':START_POINT,
        'END_POINT':END_POINT,
        'OUTPUT':op_path}) 
    
    path2 = QgsVectorLayer(res['OUTPUT'], "path2", "ogr")
    QgsProject.instance().addMapLayer(path2) 
    
    list_path.append(res['OUTPUT'])
    ###buffer create 
    bfr = processing.run("native:buffer",
        {'INPUT':res['OUTPUT'],
        'DISTANCE':0.005,#1000 meter buffer (500 both side)
        'SEGMENTS':5,
        'END_CAP_STYLE':0,
        'JOIN_STYLE':0,
        'MITER_LIMIT':2,'DISSOLVE':False,
        'OUTPUT':bufferpath})
    listbuffer_path.append(bfr['OUTPUT'])
    
    ###diffrence
    diffrent = processing.run("native:difference", 
        {'INPUT':bfr['OUTPUT'],
        'OVERLAY':poinrbuffer['OUTPUT'],
        'OUTPUT':diffrencepath})
    
    ##delete network in buffer 
    processing.run("native:selectbylocation", 
        {'INPUT':layer,
        'PREDICATE':[0,7],#intersect,cross
        'INTERSECT':diffrent['OUTPUT'],
        'METHOD':0})
    
    with edit(layer):##delete selected feature
        layer.deleteSelectedFeatures()
    
##start
for n in range(nooftank):
    if n ==0:#first route
        PREDICATE = [7]#cross
        intersect_path1 = auto_incr_obstcle['OUTPUT']
        #bfr_path1 = geo_path+f'{os.sep}buffer_{n+1}.geojson'
    else:#another route
        PREDICATE = [3,5,6]#overlap,are within,equal
        intersect_path1 =list_path[-1]
        #bfr_path1 =listbuffer_path[-1]
        
    print(intersect_path1)
        
    tankRun(geo_path+f'{os.sep}line_{n+1}.geojson',intersect_path1,PREDICATE,geo_path+f'{os.sep}buffer_{n+1}.geojson',output_folder+f'{os.sep}diffrent_{n+1}.shp')##call function

print(f'Generated tankrun in {time.time() - start} (second)')