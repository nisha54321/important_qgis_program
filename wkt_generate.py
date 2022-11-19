# -*- coding: utf-8 -*-
import sys
from turtle import onclick
sys.path.append('/home/bisag/.local/lib/python3.6/site-packages/')
path = ['/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms']

for i in path:
    sys.path.append(i)

from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QCheckBox, QListView, QMessageBox, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtWidgets 
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import QgsVectorLayer,QgsProject,QgsRasterLayer, QgsGeometry, QgsFeature, QgsSymbol, QgsSingleSymbolRenderer, QgsDataSourceUri, QgsPointXY, QgsPoint, QgsVectorFileWriter
from osgeo import ogr
import shapefile
from qgis.PyQt.QtWidgets import QAction
import psycopg2
import sys 
#import traceback
import logging
import math    
from random import randrange
from qgis import processing
import os
import time
from qgis.gui import QgsMapToolIdentifyFeature
import re, os.path
from osgeo import ogr

from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsVectorLayerTemporalProperties
from PyQt5.QtCore import QFileInfo
# Initialize Qt resources from file resources.py

import os.path

from PyQt5 import QtWidgets, QtGui

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .wkt_generate_dialog import WktGenerateDialog
import os.path
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog


class WktGenerate:
    x = 0.0
    y = 0.0 
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'WktGenerate_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&River volumn')

       
        self.first_start = None

    def tr(self, message):

        return QCoreApplication.translate('WktGenerate', message)


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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):

        plugin_dir = os.path.dirname(__file__)
        icon_path = plugin_dir+os.sep+'BISAG-N_MeitY.jpg'
        
        self.menu = self.iface.mainWindow().findChild( QMenu, '&Algorithm' )

        if not self.menu:
            self.menu = QMenu( '&Algorithm', self.iface.mainWindow().menuBar() )
            self.menu.setObjectName( '&Algorithm' )
            actions = self.iface.mainWindow().menuBar().actions()
            lastAction = actions[-1]
            self.iface.mainWindow().menuBar().insertMenu( lastAction, self.menu )
            self.action = QAction(QIcon(icon_path),"River volumn", self.iface.mainWindow())
            self.action.setObjectName( 'River volumn' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"River volumn", self.iface.mainWindow())
            self.action.setObjectName( 'River volumn' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "River volumn":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
       
        if self.first_start == True:
            self.first_start = False
            self.dlg = WktGenerateDialog()
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        xy = []
        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            print(coorx, coory)
            self.x = coorx
            self.y = coory
            xy.append(coorx)
            xy.append(coory)
            
            
        canvas = self.iface.mapCanvas()   
        pointTool = QgsMapToolEmitPoint(canvas)
        pointTool.canvasClicked.connect( display_point )
        canvas.setMapTool( pointTool )

        def point1():
            #draw point
    
            vl = QgsVectorLayer("Point?crs=EPSG:4326", "Point", "memory")

            vl.renderer().symbol().setSize(3.5)
            vl.renderer().symbol().setColor(QColor("green"))
            vl.triggerRepaint()

            f = QgsFeature()
            print(self.x, self.y)
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.x,self.y)))
            pr = vl.dataProvider()

            pr.addFeature(f)
            vl.updateExtents() 
            vl.updateFields() 
            QgsProject.instance().addMapLayers([vl])
            
            #save point 
            sp = plugin_dir+"/narmada_contour/layer/point.shp"
            QgsVectorFileWriter.writeAsVectorFormat(vl, sp, "UTF-8", vl.crs() , "ESRI Shapefile")

            #convert wkt
            myfile = ogr.Open(sp)#input Shapefile

            myshape = myfile.GetLayer(0)
            feature = myshape.GetFeature(0)
            myfeature = feature.ExportToJson()
            import json

            myfeature = json.loads(myfeature)
            import geodaisy.converters as convert
            wkt_str = convert.geojson_to_wkt(myfeature['geometry'])
            outfile = open(plugin_dir+"/narmada_contour/wkt/point.txt",'w')#output WKT file
            outfile.write(wkt_str)
            outfile.close()

        def line1():
            start_point = QgsPoint(xy[-4], xy[-3])
            end_point = QgsPoint(xy[-2], xy[-1])
            print(xy)
            
            #draw line
            v_layer = QgsVectorLayer('LineString?crs=epsg:4326', 'line', 'memory')
            pr = v_layer.dataProvider()
            seg = QgsFeature()
            seg.setGeometry(QgsGeometry.fromPolyline([start_point, end_point]))
            pr.addFeatures([ seg ])
            QgsProject.instance().addMapLayers([v_layer])

            
            QgsVectorFileWriter.writeAsVectorFormat(v_layer, plugin_dir+"/narmada_contour/layer/line.shp", "UTF-8", v_layer.crs() , "ESRI Shapefile")
            myfile = ogr.Open(plugin_dir+"/narmada_contour/layer/line.shp")#input Shapefile

            myshape = myfile.GetLayer(0)
            feature = myshape.GetFeature(0)
            myfeature = feature.ExportToJson()
            import json

            myfeature = json.loads(myfeature)
            import geodaisy.converters as convert
            wkt_str = convert.geojson_to_wkt(myfeature['geometry'])
            outfile = open(plugin_dir+"/narmada_contour/wkt/line.txt",'w')#output WKT file
            outfile.write(wkt_str)
            outfile.close()

        def lines():
            processing.run("native:extractbylocation", {'INPUT':plugin_dir+'/narmada_contour/Narmada_Contour.shp',
                                        'PREDICATE':[0],
                                        'INTERSECT':plugin_dir+'/narmada_contour/layer/line.shp',
                                    'OUTPUT':plugin_dir+'/narmada_contour/layer/lines.shp'})

            layer = QgsVectorLayer(plugin_dir+"/narmada_contour/layer/lines.shp", "lines", "ogr")
            QgsProject.instance().addMapLayer(layer)

            input = ogr.Open(plugin_dir+"/narmada_contour/layer/lines.shp")

            layer_in = input.GetLayer()
            layer_in.ResetReading()
            feature_in = layer_in.GetNextFeature()
            outfile = open(plugin_dir+"/narmada_contour/wkt/lines.txt","w")
            while feature_in is not None:
                geom = feature_in.GetGeometryRef()
                geom_name = geom.GetGeometryName()
                print(geom_name)
                wkt = geom.ExportToWkt()
                outfile.write(wkt + '\n')
                feature_in = layer_in.GetNextFeature()

        def volumn():
            output_file = plugin_dir+"/narmada_contour/layer/"

            alg_name = 'native:mergevectorlayers'
            params = {'LAYERS': [output_file+"lines.shp",output_file+"line.shp"],'OUTPUT': output_file+"merged.shp"}
            res = processing.run(alg_name, params)

            alg_name = 'qgis:polygonize'
            params = {'INPUT': output_file+"merged.shp",'OUTPUT': output_file+"polygonized.shp"}
            res = processing.run(alg_name, params)

            alg_name = 'native:extractbylocation'
            params = {'INPUT': output_file+"polygonized.shp",'PREDICATE':0,'INTERSECT': output_file+"point.shp",'OUTPUT': output_file+"extract.shp"}
            res = processing.run(alg_name, params)

            alg_name = 'native:dissolve'
            params = {'INPUT':  output_file+"extract.shp",'OUTPUT':  output_file+"extractmergeddissolved.shp"}
            res = processing.run(alg_name, params)

            alg_name = 'gdal:cliprasterbymasklayer'
            inputrasterfilename = plugin_dir+'/narmada_contour/Narmada_UTM.tif'
            
            outputraster = output_file + "clip.tif"
            if os.path.exists(outputraster):
                os.remove(outputraster)
            params = {'INPUT': inputrasterfilename,'MASK': output_file+"extractmergeddissolved.shp",'ALPHA_BAND': False,'CROP_TO_CUTLINE': True,'KEEP_RESOLUTION': True, 'DATA_TYPE':1 ,'OUTPUT': outputraster}
            res = processing.run(alg_name, params)

            #This has been added later
            filename = output_file + 'qgis.log'

            def write_log_message(message, tag, level):
                with open(filename, 'a') as logfile:
                    logfile.write('{tag}({level}): {message}'.format(tag=tag, level=level, message=message))

            QgsApplication.messageLog().messageReceived.connect(write_log_message)

            alg_name = 'native:rastersurfacevolume'
            params = {'INPUT': outputraster,'BAND':1,'METHOD': 1 ,'LEVEL': 120.0}
            res = processing.run(alg_name, params)

            v_layer = QgsVectorLayer(output_file+"extractmergeddissolved.shp","extractlayer","ogr")
            QgsProject.instance().addMapLayers([v_layer])

            v_layer = QgsRasterLayer(outputraster)
            QgsProject.instance().addMapLayers([v_layer])


        self.dlg.pushButton.clicked.connect(volumn)
        self.dlg.pushButton_point.clicked.connect(point1)
        self.dlg.pushButton_line.clicked.connect(line1)
        self.dlg.pushButton_lines.clicked.connect(lines)

        self.dlg.pushButton_line.setStyleSheet("color: red;font-size: 12pt; ") 
        self.dlg.pushButton_line.setToolTip('click')
        self.dlg.pushButton_lines.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_lines.setToolTip('click')
        self.dlg.pushButton_point.setStyleSheet("color: blue;font-size: 12pt; ") 
        self.dlg.pushButton_point.setToolTip('click')

        self.dlg.pushButton.setStyleSheet("color: brown;font-size: 12pt; ") 
        self.dlg.pushButton.setToolTip('click')
        
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
