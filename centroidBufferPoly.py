from osgeo import gdal
from osgeo import ogr
from osgeo import osr
shapefile = '/home/bisag/Documents/gpszone/Kalianpur Box/Export_Output.shp'
drv =ogr.GetDriverByName('ESRI Shapefile')
dataSet = drv.Open(shapefile)
layer = dataSet.GetLayer(0)

sr = osr.SpatialReference()   # create spatial reference object
sr.ImportFromEPSG(4326)       # set it to EPSG:4326
outfile = drv.CreateDataSource('/home/bisag/Documents/gpszone/centroidBuffer.shp') # create new shapefile
outlayer = outfile.CreateLayer('centroidbuffers', geom_type=ogr.wkbPolygon, srs=sr)  # create new layer in the shapefile 
 
nameField = ogr.FieldDefn('zoneName', ogr.OFTString)        # create new field of type string called Name to store the country names
outlayer.CreateField(nameField)                         # add this new field to the output layer
nameField = ogr.FieldDefn('srid', ogr.OFTInteger) # create new field of type integer called Population to store the population numbers
outlayer.CreateField(nameField)                         # add this new field to the output layer
 
featureDefn = outlayer.GetLayerDefn()  # get field definitions

for feature in layer:                                              # loop through selected features
    ingeom = feature.GetGeometryRef()                              # get geometry of feature from the input layer
    outgeom = ingeom.Centroid().Buffer(1.0)                        # buffer centroid of ingeom
 
    outFeature = ogr.Feature(featureDefn)                          # create a new feature
    outFeature.SetGeometry(outgeom)                                # set its geometry to outgeom
    outFeature.SetField('zoneName', feature.GetField('tbl_srs_de'))          # set the feature's Name field to the NAME value of the input feature
    outFeature.SetField('srid', feature.GetField('srid')) # set the feature's Population field to the POP2005 value of the input feature 
    outlayer.CreateFeature(outFeature)                             # finally add the new output feature to outlayer
    outFeature = None
 
#layer.ResetReading()
outfile = None         # close output file
