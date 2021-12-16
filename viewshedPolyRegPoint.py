from qgis import processing

from osgeo import ogr

shapefile = "/home/bisag/Documents/Viewshed/layer/polygonNew.shp"
driver = ogr.GetDriverByName("ESRI Shapefile")
dataSource = driver.Open(shapefile, 0)
layer = dataSource.GetLayer()
x_min1, x_max1, y_min1, y_max1 = layer.GetExtent()
#print(x_min1, x_max1, y_min1, y_max1)
extend = str(x_min1)+", "+str(x_max1)+", "+str(y_min1)+", "+str(y_max1)+" [EPSG:4326]"

processing.run("qgis:regularpoints",
            {'EXTENT':extend,
            'SPACING':0.0001,
            'INSET':0,
            'RANDOMIZE':False,
            'IS_SPACING':True,
            'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT':'/home/bisag/Documents/point10.shp'})
            
processing.run("native:intersection",
        {'INPUT':'/home/bisag/Documents/point10.shp',
        'OVERLAY':'/home/bisag/Documents/Viewshed/layer/polygonNew.shp',
        'INPUT_FIELDS':[],
        'OVERLAY_FIELDS':[],
        'OVERLAY_FIELDS_PREFIX':'',
        'OUTPUT':'/home/bisag/Documents/finalpoint10.shp'})

#lyr1 = QgsVectorLayer("/home/bisag/Documents/viewshed.shp", "polyhon", "ogr")
#QgsProject.instance().addMapLayer(lyr1)
#
lyr = QgsVectorLayer("/home/bisag/Documents/finalpoint10.shp", "point_10m", "ogr")
QgsProject.instance().addMapLayer(lyr)


#MULTIPOINT (71.516638888889 20.9073277777778)
#rasterLyr = QgsRasterLayer("/home/bisag/Documents/view.tif","Sat Image")

for feature in lyr.getFeatures():
    geom = feature.geometry()
    g = geom.asWkt()
    g = g.replace("MultiPoint ((","")
    g = g.replace(")","")
    g = g.split(" ")
    g = [float(i)for i in g]
    
p = QgsPointXY(g[0] ,g[1])

qry = rasterLyr.dataProvider().identify(p,QgsRaster.IdentifyFormatValue)
qry.isValid()
r2 = qry.results()
#    print(r2)
print(r2[1])

print(g)
