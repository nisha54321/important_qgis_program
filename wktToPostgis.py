from osgeo import ogr, osr

database = 'project'
usr = 'postgres'
pw = 'postgres'
table = 'wkt'

wkt = "POINT (71.07946 26.33141)"
point = ogr.CreateGeometryFromWkt(wkt)

connectionString = "PG:dbname='%s' user='%s' password='%s'" % (database,usr,pw)
ogrds = ogr.Open(connectionString)

srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

layer = ogrds.CreateLayer(table, srs, ogr.wkbPoint )#['OVERWRITE=YES']

layerDefn = layer.GetLayerDefn()

feature = ogr.Feature(layerDefn)
feature.SetGeometry(point)

layer.StartTransaction()
layer.CreateFeature(feature)
feature = None
layer.CommitTransaction()