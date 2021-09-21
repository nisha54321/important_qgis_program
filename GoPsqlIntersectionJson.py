from osgeo import ogr
from osgeo import gdal
import os
output_folder = os.getcwd()


gdal.SetConfigOption('CPL_DEBUG','ON')

# def testLoad(serverDS, table, sourceFile):
#     ogr.RegisterAll()
#     shapeDS = ogr.Open(sourceFile)
#     sourceLayer = shapeDS.GetLayerByIndex(0)
#     options = []
#     name = serverDS.CopyLayer(sourceLayer,table,options).GetName()
#     return name

def testLoad(serverDS, table, sourceFile):
    ogr.RegisterAll()
    shapeDS = ogr.Open(sourceFile)
    sourceLayer = shapeDS.GetLayerByIndex(0)
    options = []
    newLayer = serverDS.CreateLayer(table,sourceLayer.GetSpatialRef(),ogr.wkbUnknown,options)
    for x in range(sourceLayer.GetLayerDefn().GetFieldCount()):
        newLayer.CreateField(sourceLayer.GetLayerDefn().GetFieldDefn(x))

    newLayer.StartTransaction()
    for x in range(sourceLayer.GetFeatureCount()):
        newFeature = sourceLayer.GetNextFeature()
        newFeature.SetFID(-1)
        newLayer.CreateFeature(newFeature)
        if x % 128 == 0:
            newLayer.CommitTransaction()
            newLayer.StartTransaction()
    newLayer.CommitTransaction()
    return newLayer.GetName()



if __name__ == '__main__':
    ##go to postgres (inside folder all shp file)
    serverName = 'localhost'
    database = 'postgres'
    port = '5432'
    usr = 'postgres'
    pw = 'postgres'
    connectionString = "PG:dbname='%s' host='%s' port='%s' user='%s'password='%s'" % (database,serverName,port,usr,pw)
    ogrds = ogr.Open(connectionString)

    fileList = os.listdir(output_folder)
    #shp2pgsql -s 4326 barmer_Road public.badmer_roads | psql -h localhost -d project -U postgres  2> output.txt

    #print(fileList)
    fileEndsWith = '.shp'

    for file in fileList:
        if file.endswith(fileEndsWith):
            table = file[:-4]

            output = output_folder+"/"+file
            print(output, "    ", table)

            ##call function

            name = testLoad(ogrds,table,output)

    print("success postgres")

    ####find intersection of file 
    import os.path
    import sys
    path1 = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '.', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/postgisQueryBuilder/extlibs', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis2web', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms', '/home/bisag/Documents/qgisCode']

    for i in path1:
        sys.path.append(i)

    from qgis import processing
    import shapefile
    from json import dumps

    output_folder = os.getcwd()

    output_shapefile= output_folder+'/intersection.shp'


    from qgis import processing
    processing.run("native:lineintersections",

            {'INPUT':output_folder+'/IND_rails.shp',
            'INTERSECT':output_folder+'/IND_roads.shp',
            'INPUT_FIELDS':[],
            'INTERSECT_FIELDS':[],
            'INTERSECT_FIELDS_PREFIX':'',
            'OUTPUT':output_shapefile})

    #convert intersection file to geojson using python

    reader = shapefile.Reader(output_shapefile)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []

    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", \
        geometry=geom, properties=atr)) 

    # write the GeoJSON file
    geojson = open(output_folder+"/intersection.geojson", "w")
    geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
    geojson.close()
    print("success::")
    #ogrds.DeleteLayer(table)






# output_folder1 = os.getcwd()

# fileList = os.listdir(output_folder1)
# #print(fileList)
# fileEndsWith = '.shp'

# for file in fileList:

#     if file.endswith(fileEndsWith):
#         output = output_folder1+"/"+file
#         print(output)
#         connection = "host=localhost port=5432 dbname=project user=postgres password=postgres"
#         schema = "public"
#         command = 'ogr2ogr -f "PostgreSQL" PG:"%s" -lco SCHEMA=%s "%s" -overwrite -progress -lco OVERWRITE=YES' % (connection, schema, output)

#         #command = r'start cmd /K ogr2ogr -f "PostgreSQL" PG:"%s" -lco SCHEMA=%s "%s" -overwrite -progress -lco OVERWRITE=YES' % (connection, schema, output)
#         #print(command)
#         os.system(command)
