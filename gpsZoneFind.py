import os
from pyproj import Transformer
from osgeo import ogr

shapefile = "/home/bisag/Documents/gpszone/Kalianpur Box/Export_Output.shp"
driver = ogr.GetDriverByName("ESRI Shapefile")
dataSource = driver.Open(shapefile, 0)
layer = dataSource.GetLayer()

field_names = [field.name for field in layer.schema]

#field value (zone)
zoneval = []
for feature in layer:
    fieldval = feature.GetField("tbl_srs_de")
    zoneval.append(fieldval)

layer.ResetReading()

wkt = 'POINT (76.4796285088895 12.120900853889957)'  # WKT polygon string for a rectangular area
geom = ogr.CreateGeometryFromWkt(wkt) 
layer.SetSpatialFilter(geom)

zone_name1 = ''
srid = ''
for feature in layer:
    zone_name1 = feature.GetField('tbl_srs_de')
    srid = feature.GetField('srid')
    
print(zone_name1)
print(srid)

layer.ResetReading()

for zonename in zoneval:
    if zonename ==zone_name1:
        transformer = Transformer.from_crs(srid, 4326)
        print(transformer)




