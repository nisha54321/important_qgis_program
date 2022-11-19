import os,time
from qgis import processing

cwd = r"/home/bisag/Music/webMobility"

output_folder = os.path.join(cwd,'output')
geo_path = os.path.join(cwd,'geojson1')

lat_long_list = open(cwd+"/lat_long_list.txt",'r')
content = lat_long_list.read()
content = content.split(",")
xy = [float(content[0].strip()),float(content[1].strip()),float(content[2].strip()),float(content[3].strip())]
lat_long_list.close()

START_POINT =f'{xy[-4]},{xy[-3]} [EPSG:4326]'
END_POINT =f'{xy[-2]},{xy[-1]} [EPSG:4326]'

layer = '/home/bisag/Documents/sumit11/1.shp'

start = time.time()
wktfix = processing.run("native:fixgeometries", 
        {'INPUT':layer,
        'OUTPUT':output_folder+f'{os.sep}wktfix.shp'})             

auto_incr = processing.run("native:addautoincrementalfield",
               {'INPUT':wktfix['OUTPUT'],
                'FIELD_NAME':'AUTO',                               
                'START':1,
                'GROUP_FIELDS':[],'SORT_EXPRESSION':'','SORT_ASCENDING':True,'SORT_NULLS_FIRST':False,
                'OUTPUT':output_folder+f'{os.sep}wktfixAuto.shp'})

s_path = processing.run("native:shortestline", 
            {'SOURCE':auto_incr['OUTPUT'],
            'DESTINATION':auto_incr['OUTPUT'],
            'METHOD':0,
            'NEIGHBORS':10,
            'DISTANCE':None,
            'OUTPUT':output_folder+f'{os.sep}s_path.shp'})
            
layer = QgsVectorLayer(s_path['OUTPUT'], "s_path", "ogr")
QgsProject.instance().addMapLayer(layer)

selectloc =processing.run("native:selectbylocation", 
    {'INPUT':layer,
    'PREDICATE':[7],#cross
    'INTERSECT':auto_incr['OUTPUT'],
    'METHOD':0})

with edit(layer):##delete selected feature
    layer.deleteSelectedFeatures()
    
wktfix1 = processing.run("native:fixgeometries", 
        {'INPUT':layer,
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
            
auto_incr2 = processing.run("native:addautoincrementalfield",
               {'INPUT':removeDup['OUTPUT'],
                'FIELD_NAME':'AUTO1',                               
                'START':1,
                'GROUP_FIELDS':[],'SORT_EXPRESSION':'','SORT_ASCENDING':True,'SORT_NULLS_FIRST':False,
                'OUTPUT':output_folder+f'{os.sep}pointAutoInc.shp'})
                
shortestpath = processing.run("native:shortestline", 
            {'SOURCE':auto_incr2['OUTPUT'],
            'DESTINATION':auto_incr2['OUTPUT'],
            'METHOD':0,
            'NEIGHBORS':5,
            'DISTANCE':None,
            'OUTPUT':output_folder+f'{os.sep}shortestpath.shp'})
            
wktfix4 = processing.run("native:fixgeometries", 
        {'INPUT':shortestpath['OUTPUT'],
        'OUTPUT':output_folder+f'{os.sep}shortestpathFix.shp'}) 
###############################

vlayer = QgsVectorLayer(wktfix4['OUTPUT'], "s_path4", "ogr")
QgsProject.instance().addMapLayer(vlayer)

select3 = processing.run("native:selectbylocation",
        {'INPUT':vlayer,
        'PREDICATE':[7],
        'INTERSECT':auto_incr['OUTPUT'],
        'METHOD':0})
with edit(vlayer):##delete selected feature
    vlayer.deleteSelectedFeatures()
        
res =processing.run("native:shortestpathpointtopoint",
    {'INPUT':vlayer,
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
    'OUTPUT':output_folder+f'{os.sep}path1.shp'}) 
    
vlayer1 = QgsVectorLayer(res['OUTPUT'], "s_path3", "ogr")
QgsProject.instance().addMapLayer(vlayer1)   

select5 = processing.run("native:selectbylocation",
                {'INPUT':vlayer1,
                'PREDICATE':[3,5,6],
                'INTERSECT':vlayer,
                'METHOD':0})
with edit(vlayer1):##delete selected feature
    vlayer1.deleteSelectedFeatures()
            
s_path3 = processing.run("native:shortestpathpointtopoint",
                {'INPUT':vlayer1,
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
                'OUTPUT':output_folder+f'{os.sep}path2.shp'}) 
vlayer2 = QgsVectorLayer(s_path3['OUTPUT'], "path2", "ogr")
QgsProject.instance().addMapLayer(vlayer2) 

print(f'Generated tankrun in {time.time() - start} (second)')