vectorLyr = QgsVectorLayer('/home/bisag/Documents/1LAYERS/point/sld_cookbook_point.shp', 'Museums', "ogr")
vpr = vectorLyr.dataProvider()
n_features = vectorLyr.featureCount() #added line

s_d_coord = [(175.83,13.67),(56.84,83.94)]
f = QgsFeature()

for i in s_d_coord:
    pnt = QgsGeometry.fromPointXY(QgsPointXY(i[0],i[1])) 
    f.setGeometry(pnt)
    vpr.addFeatures([f])

vectorLyr.updateExtents()
QgsProject.instance().addMapLayer(vectorLyr)
