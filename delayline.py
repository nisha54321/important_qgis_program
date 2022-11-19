from json import dumps
import sys
import shapefile
import re
import os

new_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python3.6/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms', '/home/bisag/.local/lib/python3.6/site-packages/IPython/extensions']

for i in new_path:
    sys.path.append(i)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import (QgsApplication,QgsCoordinateReferenceSystem)
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
procCorr = grd+"/Mobility_Grid_Selected.geojson"

dis = '5000'

path3 = cwd+'/vis_viewshed/output/vshedGeojson/'
linepath = cwd+'/geojson/LINE.geojson'

def delayLine():
    linepath = cwd+'/geojson/LINE.geojson'

    dis = '5000'

    dis = int(dis)
    dis = str(dis/111000)
    linepath = cwd+'/geojson/LINE.geojson'

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
            else:
                atr['color'] = "black"
                atr['name2'] = "actualboundry"

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
                    if file.startswith("Mobility_Grid_Selected"):
                            continue
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
                                'OUTPUT':cwd+'/geojson/mergektf.geojson'})

        print("delayline and merge max point generated:::")
    except Exception as e:
        print(e)

    
if __name__ == "__main__":
    delayLine()
