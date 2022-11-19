from json import dumps
import sys
import shapefile

new_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python3.6/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms', '/home/bisag/.local/lib/python3.6/site-packages/IPython/extensions', '/home/bisag/Music/basic_qgis']

for i in new_path:
    sys.path.append(i)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import (QgsApplication,QgsVectorLayer)
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

gid = []###for save layer
for feat in temp.getFeatures():
    gid.append(feat['gid'])
    
gd = str(gid[0])
svpath = 'mobility_'+gd
print("save path: ",svpath)

def kbf():
    import uuid##hello

    id = uuid.uuid4()
    result = processing.run("native:difference", 
        {
            'INPUT':procCorr,
            'OVERLAY':cwd+'/kbf/Greater_then_10_buffer.shp',
            'OUTPUT':cwd+f'/kbf/{id}_KBF.shp'})
    ##convert Geojson
    reader = shapefile.Reader(result['OUTPUT'])
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []

    for sr in reader.shapeRecords():
        try:
            atr = dict(zip(field_names, sr.record))

            atr['name2'] = "kbf"
            geom = sr.shape.__geo_interface__
            buffer.append(dict(type="Feature", \
            geometry=geom, properties=atr))
        except:
            pass
    geojson1 = open(cwd+f"/geojson/{svpath}/kbf.geojson", "w")
    geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
    geojson1.close()
    
if __name__ == "__main__":
    kbf()
