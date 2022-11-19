# -*- coding: utf-8 -*-
from qgis.core import QgsVectorFileWriter

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, QtGui
from qgis.core import Qgis
import subprocess
from datetime import datetime, timedelta
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *
from .single_path_dialog import SinglePathDialog
import os.path
from qgis import processing
from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsPointXY,
    QgsRaster,
    QgsRasterShader,
    QgsColorRampShader,QgsLayerTreeLayer,
    QgsSingleBandPseudoColorRenderer,QgsVectorLayerTemporalProperties,QgsCoordinateReferenceSystem,QgsSvgMarkerSymbolLayer,QgsVectorFileWriter,
    QgsSingleBandColorDataRenderer,QgsTextFormat,
    QgsSingleBandGrayRenderer,QgsVectorLayer, QgsPoint, QgsVectorLayer, QgsFeature, QgsGeometry, QgsVectorFileWriter, QgsField, QgsPalLayerSettings, QgsVectorLayerSimpleLabeling
)
from qgis.gui import QgsMapToolIdentifyFeature, QgsMapToolEmitPoint
from PyQt5 import QtWidgets 
from PyQt5 import QtGui
from qgis.PyQt.QtWidgets import QAction
import re, os.path
from qgis.PyQt.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QWidget, QVBoxLayout, QAction, QLabel, QLineEdit, QMessageBox, QFileDialog, QFrame, QDockWidget, QProgressBar, QProgressDialog, QToolTip
from datetime import timedelta, datetime
from time import strftime
from time import gmtime
import time
from osgeo import ogr
from osgeo import osr

import os
from collections import defaultdict
from itertools import chain
import operator
import shapefile
from json import dumps
class SinglePath:
    xy = []
    iii = 0
    vl = ''
    rlayer = ''
    iii = 0
    vl =''
    xy1 = []
    xy = []
    vlayer1 = ''
    mbselect = ''
    sel1 = []
    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SinglePath_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Single Path')

        self.first_start = None

    def tr(self, message):
        
        return QCoreApplication.translate('SinglePath', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):

        plugin_dir = os.path.dirname(__file__)
        icon_path = plugin_dir+'/'+'army5.jpeg'      
        self.add_action(
            icon_path,
            text=self.tr(u'Single Path'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Single Path'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):

        if self.first_start == True:
            self.first_start = False
            self.dlg = SinglePathDialog()
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        #remove all files
        mypath1 = plugin_dir+"/shapefile/"
        mypath2 = plugin_dir+"/buffer/"
        mypath3 = plugin_dir+"/output/"
        mypath4 =plugin_dir+"/distance/"

        l = [mypath1,mypath2,mypath3,mypath4]
        for delfol in l:
            #print(delfol)
            for root, dirs, files in os.walk(delfol):
                for file in files:
                    os.remove(os.path.join(root, file))

        mypath11 = plugin_dir+"/geojson/"
        for root, dirs, files in os.walk(mypath11):
                for file in files:
                    if file.endswith(".geojson"):
                        os.remove(os.path.join(root, file))
                        
        plugin_dir = os.path.dirname(__file__)

        if(self.iii == 0):            
            self.vl = QgsVectorLayer("Point?crs=EPSG:4326", "markpoint", "memory")
            self.vlayer1 = QgsVectorLayer(plugin_dir+'/grid.shp', "select Grid", "ogr")
            QgsProject.instance().addMapLayer(self.vlayer1)
            self.iii = 1

        #set active layer grid
        self.vlayer1.removeSelection()###remove selection
        self.iface.actionSelect().trigger()############enable select tools

        sg = QgsProject.instance().mapLayersByName('select Grid')[0]
        self.iface.setActiveLayer(sg)
        
        x11= "source", "destination"
        y = list(x11*15)
        point_label = iter(y)

        def display_point1( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            
            self.xy.append(coorx)
            self.xy.append(coory)
            self.vl.renderer().symbol().setColor(QColor("blue"))
            self.vl.renderer().symbol().setSize(4)

            self.vl.triggerRepaint()

            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx, coory)))
            pr = self.vl.dataProvider()

            #Add Attribute
            self.vl.startEditing()
            pr.addAttributes([QgsField("point_label", QVariant.String)])

            x = next(point_label)
            attvalAdd = [x]
            f.setAttributes(attvalAdd)
            self.vl.triggerRepaint()

            pr.addFeature(f)
            self.vl.updateExtents() 
            self.vl.updateFields() 
            QgsProject.instance().addMapLayers([self.vl])

            #set label
            layer_settings  = QgsPalLayerSettings()
            layer_settings.fieldName = "point_label"
            layer_settings.placement = 2
            layer_settings.enabled = True

            text_format = QgsTextFormat()
            text_format.setFont(QFont("MS Shell Dlg 2"))
            text_format.setSize(10.0)
            text_format.setColor(QColor("red"))
            text_format.setFont(QFont("MS Shell Dlg 2",10,QFont.Bold))
            layer_settings.setFormat(text_format)

            layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
            self.vl.setLabelsEnabled(True)
            self.vl.setLabeling(layer_settings)
            self.vl.triggerRepaint()
            self.vl.startEditing()
            self.vl.triggerRepaint()
            self.vl.commitChanges()

            if len(self.xy)==4 or len(self.xy)==8 or len(self.xy)==12 or len(self.xy)==16 or len(self.xy)==20:
                self.iface.actionPan().trigger()

        canvas = self.iface.mapCanvas()   
        pointTool = QgsMapToolEmitPoint(canvas)
        
        def click1():
                pointTool.canvasClicked.connect( display_point1 )
                canvas.setMapTool( pointTool )

        self.dlg.pushButton_click.clicked.connect(click1)  
        
        def mobility():

            extractFet = processing.run("native:saveselectedfeatures", 
                        {'INPUT':plugin_dir+'/grid.shp',
                        'OUTPUT':plugin_dir+'/selectFeat.shp'})

            temp = QgsVectorLayer(extractFet["OUTPUT"], "selectSaveGrid", "ogr")

            single_symbol_renderer = temp.renderer()####holo (outerline black symbology)
            symbol = single_symbol_renderer.symbol()
            symbol.setColor(QColor("transparent"))
            symbol.symbolLayer(0).setStrokeColor(QColor("black"))   # change the stroke colour (Fails)
            symbol.symbolLayer(0).setStrokeWidth(1)   # change the stroke colour (Fails)

            temp.triggerRepaint()
            temp.commitChanges()
            QgsProject.instance().addMapLayer(temp)

            QgsProject.instance().layerTreeRoot().findLayer(temp.id()).setItemVisibilityChecked(False)

            ex = temp.extent()
            xmax = str(ex.xMaximum())
            ymax = str(ex.yMaximum())
            xmin = str(ex.xMinimum())
            ymin = str(ex.yMinimum())
            ex1 = xmax+','+xmin+','+ymax+','+ymin+' [EPSG:4326]'
            #print(ex1)
            
            ####clip dataset:

            wktfix = processing.run("native:fixgeometries",
                         {'INPUT':plugin_dir+'/mobility_wkt1.geojson',
                         'OUTPUT':plugin_dir+'/new/mobility_wkt1.geojson'})

            clip1 = processing.run("native:clip",
                            {'INPUT':wktfix['OUTPUT'],
                            'OVERLAY':temp,
                            'OUTPUT':plugin_dir+'/new/clip.shp'})
    
            res3 = processing.run("native:multiparttosingleparts", 
                            {'INPUT':plugin_dir+'/mobility_wkt1.geojson',
                            'OUTPUT':plugin_dir+'/mulSignle_wkt1.geojson'})

            temp1 = QgsVectorLayer(clip1['OUTPUT'], "clip", "ogr")
            ###sym clip
            single_symbol_renderer = temp1.renderer()
            symbol = single_symbol_renderer.symbol()
            symbol.setColor(QColor("black"))
            symbol.symbolLayer(0).setStrokeColor(QColor("black"))   # change the stroke colour (Fails)

            temp1.triggerRepaint()
            temp1.commitChanges()
            # QgsProject.instance().addMapLayer(temp1)
            # QgsProject.instance().layerTreeRoot().findLayer(temp1.id()).setItemVisibilityChecked(False)

            # print(ex1)
            temp1.triggerRepaint()

            res3 = processing.run("native:rasterize",
                     {'EXTENT':ex1,
                        'EXTENT_BUFFER':0,
                        'TILE_SIZE':1024,
                        'MAP_UNITS_PER_PIXEL':0.00009,
                        'MAKE_BACKGROUND_TRANSPARENT':False,
                        'MAP_THEME':None,
                        'LAYERS':[temp1,temp],
                        'OUTPUT':plugin_dir+'/output/convertMapRaster.tif'})

            
            res4 = processing.run("gdal:cliprasterbyextent", 
                        {'INPUT':res3['OUTPUT'],
                        'PROJWIN':ex1,
                        'NODATA':None,
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'EXTRA':'',
                        'OUTPUT':plugin_dir+'/output/convertMapRasterClip.tif'})

            rasterize = QgsRasterLayer(res4['OUTPUT'], "rasterize")
            # QgsProject.instance().addMapLayer(rasterize)
            # QgsProject.instance().layerTreeRoot().findLayer(rasterize.id()).setItemVisibilityChecked(False)

            processing.run("gdal:rearrange_bands",
                        {'INPUT':res4['OUTPUT'],
                        'BANDS':[1],
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'OUTPUT':plugin_dir+'/output/singleband.tif'})
                        
            reclass = processing.run("native:reclassifybytable",
                        {'INPUT_RASTER':plugin_dir+'/output/singleband.tif',
                        'RASTER_BAND':1,
                        'TABLE':[0,38,1,38,255,2],
                        'NO_DATA':-9999,
                        'RANGE_BOUNDARIES':0,
                        'NODATA_FOR_MISSING':False,
                        'DATA_TYPE':5,
                        'OUTPUT':plugin_dir+'/recassify.tif'})

            rasterize = QgsRasterLayer(reclass['OUTPUT'], "reclass")
            QgsProject.instance().addMapLayer(rasterize)


            print("succees:")
            
        self.dlg.pushButton_obs.clicked.connect(mobility)  
            
        
        #buffer create 
        def buffer():
            bufferSize = self.dlg.lineEdit.text()
            bufferSize = (float(bufferSize)/111111)/2
            out_buffer_path = plugin_dir+'/layer/buffer.shp'#0.0027027027

            processing.run("native:buffer", {'INPUT':plugin_dir+'/layer/linestring.shp',
                        'DISTANCE':bufferSize,
                        'SEGMENTS':5,
                        'END_CAP_STYLE':0,
                        'JOIN_STYLE':0,
                        'MITER_LIMIT':2,
                        'DISSOLVE':False,
                        'OUTPUT':out_buffer_path})

            vlayer = QgsVectorLayer(out_buffer_path, "Buffer", "ogr")
            if not vlayer.isValid():
                print("Layer failed to load!")
            else:
                QgsProject.instance().addMapLayer(vlayer)

        self.dlg.label_path.show()
        self.dlg.pushButton_path.show()
        
        self.dlg.label_info.show()
        self.iface.messageBar().pushMessage("Please Select grid...", level=Qgis.Info)

        x = "Source,Destination,"
        y = x *10
        z = y.split(",")

        point_label = iter(z)
        

        def line1():
            ####which mobility corridor selected id fetch and save path inside geojson in mobility1,2,3 etc folder
            selection = self.vlayer1.selectedFeatures()
            for feat in selection:
                id1 = int(feat['id'])
                #self.mbselect+=str(id1)
                self.mbselect=str(id1)
                self.sel1.append(str(id1))

            print("selected mobility corridor :",self.mbselect)
            self.iface.actionPan().trigger()############activate pan mode 

            op3 = plugin_dir+'/geojson/mobility_{}'.format(str(self.mbselect))
            for root, dirs, files in os.walk(op3):
                for file in files:
                    os.remove(os.path.join(root, file))
            print('save file :',op3)

            start = time.time()
            
    
            print(self.xy)
    
            os.system(f"python3 {plugin_dir}/shortest_path.py {self.xy[-4]} {self.xy[-3]} {self.xy[-2]} {self.xy[-1]}")#####3change shortest_path.py (input = plugin_dir+'/recassify1.tif')

            f = open(plugin_dir+"/path.txt", "r")
            x = f.read()
            f.close()

            wkt = x.split("\n")
            wkt = [i for i in wkt if i]#remove empty string

            spatialref = osr.SpatialReference()
            spatialref.ImportFromProj4('+proj=longlat +datum=WGS84 +no_defs')

            driver = ogr.GetDriverByName("ESRI Shapefile")
            c= 1
            mergeclip =[]
            for wktval in wkt:

                ###################convert shp
                input_folder = plugin_dir+"/shapefile/line{}.shp".format(str(c))

                dstfile = driver.CreateDataSource(input_folder)
                dstlayer = dstfile.CreateLayer("line", spatialref, geom_type=ogr.wkbLineString)
                fielddef = ogr.FieldDefn("ID", ogr.OFTInteger)
                fielddef.SetWidth(10)
                dstlayer.CreateField(fielddef)
                poly = ogr.CreateGeometryFromWkt(wktval)
                feature = ogr.Feature(dstlayer.GetLayerDefn())
                feature.SetGeometry(poly)
                feature.SetField("ID", 0)
                dstlayer.CreateFeature(feature)
                feature.Destroy()
                dstfile.Destroy()

                try:
                    from pyproj import Geod
                    from shapely import wkt

                    #in meter
                    line =wkt.loads(wktval)
                    geod = Geod(ellps="WGS84")

                    len1 = geod.geometry_length(line)

                    print("length is (meter):",len1)
                except Exception as e:
                    pass

                ##convert shape to geojson
                reader = shapefile.Reader(input_folder)
                fields = reader.fields[1:]
                field_names = [field[0] for field in fields]
                line = []

                for sr in reader.shapeRecords():
                    atr = dict(zip(field_names, sr.record))
                    try:
                        geom = sr.shape.__geo_interface__
                        line.append(dict(type="Feature", geometry=geom, properties=atr))
                    except:
                        pass 
                for sr in reader.shapeRecords():
                    atr = dict(zip(field_names, sr.record))
                    try:
                        geom = sr.shape.__geo_interface__
                        if geom['type'] == 'LineString':
                            atr['length_meter'] = round(len1, 2)

                        line.append(dict(type="Feature", \
                        geometry=geom, properties=atr)) 
                    except:
                        pass

                # write the GeoJSON file
                #op = plugin_dir+'/geojson'
                op = plugin_dir+'/geojson'
                geojson11 = open(op+"/mobility_{}/line{}.geojson".format(str(self.mbselect),str(c)), "w")
                geojson11.write(dumps({"type": "FeatureCollection", "features": line}, indent=2) + "\n")
                geojson11.close()

                temp = QgsVectorLayer(op+"/mobility_{}/line{}.geojson".format(str(self.mbselect),str(c)), f"line{c}_corridor{self.mbselect}", "ogr")
                QtGui.QColor(255, 0, 0)
                single_symbol_renderer = temp.renderer()
                symbol = single_symbol_renderer.symbol()
                symbol.setWidth(1.08)

                #add maptips(mouse hover)
                expression = """[%  @layer_name  %]"""
                temp.setMapTipTemplate(expression)
                QgsProject.instance().addMapLayer(temp)#

                #buffer1()#find the buffer of shortest path(500 meter)
                processing.run("native:buffer", 
                            {'INPUT':input_folder,
                            'DISTANCE':0.0021,
                            'SEGMENTS':5,
                            'END_CAP_STYLE':0,
                            'JOIN_STYLE':0,
                            'MITER_LIMIT':2,
                            'DISSOLVE':False,
                            'OUTPUT':plugin_dir+"/buffer"+'/buffer{}.shp'.format(str(c))})

                


        #self.dlg.pushButton_animation.clicked.connect(animation)  
        self.dlg.pushButton_animation.setStyleSheet("color: green;font-size: 12pt; ") 

        #self.dlg.pushButton_cesium.clicked.connect(cesium)  
        self.dlg.pushButton_cesium.setStyleSheet("color: blue;font-size: 12pt; ") 

        #self.dlg.pushButton_slope.clicked.connect(slope1)  
        #self.dlg.pushButton_reclassify.clicked.connect(reclassifytable) 
        self.dlg.pushButton_path.clicked.connect(line1) 
        #self.dlg.pushButton_path_2.clicked.connect(elevation_profile)  
        self.dlg.pushButton_path_2.setStyleSheet("color: Maroon;font-size: 12pt; ") 
        # self.dlg.pushButton_slope.setStyleSheet("color: green;font-size: 12pt; ") 

        # self.dlg.pushButton_reclassify.setStyleSheet("color: green;font-size: 12pt; ") 
        # self.dlg.pushButton_reclassify.setToolTip('click')

        self.dlg.pushButton_path.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_path.setToolTip('click for Find Shortest Path')
        self.dlg.label_title.setStyleSheet("color: Indigo; font-size: 13pt;") 
        #self.dlg.label_slope.setStyleSheet("color: brown; ") 
        #self.dlg.label_reclassify.setStyleSheet("color: brown; ") 
        self.dlg.label_path.setStyleSheet("color: brown; ") 
        self.dlg.label_info.setStyleSheet("color: Navy; ") 
        self.dlg.label.setStyleSheet("color: brown; ") 

        self.dlg.pushButton_cesium.setToolTip('click for Show Shortest path in 3D')
        self.dlg.pushButton_path_2.setToolTip('click for Show elevation profile')
        self.dlg.pushButton_animation.setToolTip('click for show Route Animation')
        self.dlg.pushButton_cesium.hide()
        self.dlg.pushButton_path_2.hide()
        self.dlg.pushButton_animation.hide()

        self.dlg.show()
        result = self.dlg.exec_()
        
