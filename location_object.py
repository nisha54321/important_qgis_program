
# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QCheckBox, QListView, QMessageBox, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtWidgets 
from qgis.gui import QgsMapToolEmitPoint

from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import QgsVectorLayer,QgsProject, QgsGeometry, QgsFeature, QgsSymbol, QgsSingleSymbolRenderer, QgsDataSourceUri
import psycopg2

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

from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsVectorLayerTemporalProperties, QgsRasterLayer, QgsVectorFileWriter,QgsPointXY, QgsField,QgsPieDiagram,QgsDiagramSettings,QgsLinearlyInterpolatedDiagramRenderer,QgsDiagramLayerSettings
from PyQt5.QtCore import QFileInfo
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .location_object_dialog import Location_ObjectDialog
import os.path
import os.path

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qgis.PyQt.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QWidget,QButtonGroup, QVBoxLayout, QAction, QLabel, QLineEdit, QMessageBox, QFileDialog, QFrame, QDockWidget, QProgressBar, QProgressDialog, QToolTip
from PyQt5.QtGui import QKeySequence, QIcon

from PyQt5.QtCore import QSettings, QSize, QPoint, QVariant, QFileInfo, QTimer, pyqtSignal, QObject, QItemSelectionModel, QTranslator, qVersion, QCoreApplication
from datetime import timedelta, datetime
from time import strftime
from time import gmtime
from qgis.utils import iface
from qgis.core import *
from qgis.utils import *
from PyQt5.QtGui import QImage, QColor, QPixmap
from osgeo import ogr
from json import dumps

import shapefile
import json

class Location_Object:

    iii = 0 
    rb_icon = ""
    abcounter = 0
    vpoly = ""
    raster = ''
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Location_Object_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&ViewShed Object')

        self.first_start = None

    def tr(self, message):
        
        return QCoreApplication.translate('ViewShed Object', message)


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
        icon_path = plugin_dir+os.sep+'BISAG-N_MeitY.jpg'
        
        self.menu = self.iface.mainWindow().findChild( QMenu, '&Algorithm' )

        if not self.menu:
            self.menu = QMenu( '&Algorithm', self.iface.mainWindow().menuBar() )
            self.menu.setObjectName( '&Algorithm' )
            actions = self.iface.mainWindow().menuBar().actions()
            lastAction = actions[-1]
            self.iface.mainWindow().menuBar().insertMenu( lastAction, self.menu )
            self.action = QAction(QIcon(icon_path),"ViewShed Object", self.iface.mainWindow())
            self.action.setObjectName( 'ViewShed Object' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"ViewShed Object", self.iface.mainWindow())
            self.action.setObjectName( 'ViewShed Object' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "ViewShed Object":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)



    def run(self):
        
        self.jrad = ''
        self.radiusvalue = ''
        self.x = 0
        self.y = 0
        self.i_rad = 0
        self.icon_path = ''
        self.jicon = []
        self.jimg = []

        if self.first_start == True:
            self.first_start = False
            self.dlg = Location_ObjectDialog() 
        cwd = os.getcwd()
        print(cwd)

        plugin_dir = os.path.dirname(__file__)

        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+"/bisag_n.png").scaledToWidth(120))
  
        #self.dlg.label_rad.setText("2. radius")
        
        notbounshp = plugin_dir+"/goArea.shp"
        if os.path.exists(notbounshp):
            os.remove(notbounshp)
        #edit shape file
        def shape_publish(file_name):

            r = shapefile.Reader(file_name)

            outlist = []

            for shaperec in r.iterShapeRecords():
                outlist.append(shaperec)
            shapeType =  r.shapeType
            rFields = list(r.fields)
            r = None
            ##to be sure we delete the existing shapefile
            if os.path.exists(file_name):
                pass
                # os.remove(file_name)
            else:
                print("file does not exist"+ file_name)

            ##to be sure we delete the existing dbf file
            dbf_file = file_name.replace(".shp",".dbf")
            if os.path.exists(dbf_file):
                pass
                # os.remove(dbf_file)
            else:
                print("file does not exist" + dbf_file)
            ##to be sure we delete the existing shx file
            shx_file = file_name.replace(".shp", ".shx")
            if os.path.exists(shx_file):
                pass
                # os.remove(shx_file)
            else:
                print("file does not exist" + shx_file)
            
            w = shapefile.Writer(notbounshp,shapeType)

            w.fields = rFields
            #print(outlist)
            for shaperec in outlist:
                record = shaperec.record[0]
                if record == 1:
                    #print(record)
                    w.record(record)
                    w.shape(shaperec.shape)
            w.close()

        
        def spinboxRad():
            getval = self.dlg.spinBox_rad.value()
            #getval = getval/1000
            self.r = float(getval)

        self.dlg.spinBox_rad.valueChanged.connect(spinboxRad)
        self.dlg.spinBox_rad.setRange(500, 5000)
        self.dlg.spinBox_rad.setSingleStep(100)

        
        #add raster file
        path_to_tif = plugin_dir+"/asterDem.tif"
        rlayer = QgsRasterLayer(path_to_tif, "Raster")
        if not rlayer.isValid():
            print("Layer failed to load!")
        
        QgsProject.instance().addMapLayer(rlayer)
        xycoor =[]
        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            

            xycoor.append(coorx)
            xycoor.append(coory)

            print(coorx,coory)

            getval = self.dlg.spinBox_rad.value()

            self.r = float(getval)
            print(self.r)
            xy = str(coorx) +","+str(coory) + " [EPSG:4326]"


            dempath = plugin_dir+'/asterDem.tif'
            visImgOp = plugin_dir+"/visibilityanalysis.tif"
            processing.run("grass7:r.viewshed", {'input':dempath,
                        'coordinates':xy,
                        'observer_elevation':1.75,
                        'target_elevation':0,
                        'max_distance':self.r ,
                        'refraction_coeff':0.14286,
                        'memory':500,
                        '-c':False,
                        '-r':False,
                        '-b':True,
                        '-e':False,
                        'output':visImgOp,
                        'GRASS_REGION_PARAMETER':None,
                        'GRASS_REGION_CELLSIZE_PARAMETER':0,
                        'GRASS_RASTER_FORMAT_OPT':'',
                        'GRASS_RASTER_FORMAT_META':''})

            rlayer = QgsRasterLayer(visImgOp, "visibilityAnalysis")
            self.raster = rlayer
            if not rlayer.isValid():
                print("Layer failed to load!")

            #QgsProject.instance().addMapLayer(rlayer)

            #CREATE VIEW POINT
            vl = QgsVectorLayer("Point?crs=EPSG:4326", "ViewPoint", "memory")

            vl.renderer().symbol().setSize(3.5)
            vl.renderer().symbol().setColor(QColor("blue"))
            vl.triggerRepaint()

            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx,coory)))
            pr = vl.dataProvider()

            #vl.dataProvider().addAttributes([QgsField("go", QVariant.Int),QgsField("nogo", QVariant.Int)])
            vl.updateFields()
            pr.addFeature(f)
            vl.updateExtents() 
            vl.updateFields() 

            QgsVectorFileWriter.writeAsVectorFormat(vl, plugin_dir+"/viewpoint.shp", "UTF-8", vl.crs() , "ESRI Shapefile")

            #QgsProject.instance().addMapLayer(vl)

            polygonshp = plugin_dir+"/polygon.shp"
            if os.path.exists(polygonshp):
                os.remove(polygonshp)
            processing.run("gdal:polygonize", {'INPUT':visImgOp,
                            'BAND':1,
                            'FIELD':'DN',
                            'EIGHT_CONNECTEDNESS':False,
                            'EXTRA':'',
                            'OUTPUT':polygonshp})

            vlayer = QgsVectorLayer(polygonshp, "go_nogoArea", "ogr")
            #QgsProject.instance().layerTreeRoot().findLayer(vlayer.id()).setItemVisibilityChecked(False)

            QgsProject.instance().addMapLayer(vlayer)


            #remove boundry of polygon shape file
            shape_publish(polygonshp)

            #convert geojson using python
            reader = shapefile.Reader(notbounshp)
            fields = reader.fields[1:]
            field_names = [field[0] for field in fields]
            buffer = []

            for sr in reader.shapeRecords():
                atr = dict(zip(field_names, sr.record))
                geom = sr.shape.__geo_interface__
                buffer.append(dict(type="Feature", \
                geometry=geom, properties=atr)) 
            
            # write the GeoJSON file
            geojson = open(plugin_dir+"/polygon.geojson", "w")
            geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
            geojson.close()

            #using qgis api
            input_shp=QgsVectorLayer(polygonshp,"polygon","ogr")
            input_shp.isValid()
            
            vlayer = QgsVectorLayer(notbounshp, "viewShed", "ogr")
            if not vlayer.isValid():
                print("Layer failed to load!")
            else:
                QgsProject.instance().addMapLayer(vlayer)
            QgsProject.instance().addMapLayer(vl)
           
        canvas = iface.mapCanvas() 
        pointTool = QgsMapToolEmitPoint(canvas)

        pointTool.canvasClicked.connect( display_point )

        canvas.setMapTool( pointTool )
        go1 =[]
        nogo1 = []
        tarea = []
        self.dlg.lineEdit_Wedge.setText('90')
        self.dlg.lineEdit_Azimuth.setText('0')

        def arcShape1():
            rad = self.dlg.spinBox_rad.value()/111111
            #rad = self.dlg.spinBox_rad.value()/100000

            print(rad)
            self.dlg.label_percentage.show()
            Azimuth = self.dlg.lineEdit_Azimuth.text()
            Wedge = self.dlg.lineEdit_Wedge.text()
            print(Azimuth,Wedge)

            ##for create arc shape
            layer = QgsVectorLayer(plugin_dir+"/viewpoint.shp","viewpoint","ogr")
            print("rad,azimuth shape:",rad,Azimuth)
            res = processing.run("native:wedgebuffers",
                 {'INPUT':layer,
                 'AZIMUTH':Azimuth,
                 'WIDTH':Wedge,
                 'OUTER_RADIUS':rad,
                 'INNER_RADIUS':0,
                 'OUTPUT':plugin_dir+"/arcShape.shp"})

            arcShape = QgsVectorLayer(res["OUTPUT"], "arcShape", "ogr")
            QgsProject.instance().addMapLayer(arcShape)

            ##go and nogo
            ip = QgsProject.instance().mapLayersByName('go_nogoArea')[0]
            ##go area
            vlayer = QgsVectorLayer(notbounshp, "viewShed", "ogr")
            


            ##go 
            res222 = processing.run("native:clip", 
                        {'INPUT':vlayer,
                        'OVERLAY':arcShape,
                        'OUTPUT':plugin_dir+"/shapeClipgo.shp"})

            arcShape11 = QgsVectorLayer(res222["OUTPUT"], "goClip", "ogr")
            QgsProject.instance().addMapLayer(arcShape11)

            ###go and nogo
            res22 = processing.run("native:clip", 
                        {'INPUT':ip,
                        'OVERLAY':arcShape,
                        'OUTPUT':plugin_dir+"/shapeClipgo_nogo.shp"})

            arcShape1 = QgsVectorLayer(res22["OUTPUT"], "go_nogoClip", "ogr")
            QgsProject.instance().addMapLayer(arcShape1)
            
            # ##area find
            res1 = processing.run("native:fieldcalculator", 
                        {'INPUT':arcShape1,
                        'FIELD_NAME':'area',
                        'FIELD_TYPE':0,
                        'FIELD_LENGTH':0,
                        'FIELD_PRECISION':0,
                        'FORMULA':'$area',
                        'OUTPUT':plugin_dir+"/shapeClipArea.shp"})
            area = QgsVectorLayer(res1["OUTPUT"], "nogoClip", "ogr")
            QgsProject.instance().addMapLayer(area)

            reader = shapefile.Reader(res1["OUTPUT"])
            fields = reader.fields[1:]
            field_names = [field[0] for field in fields]
            buffer = []

            for sr in reader.shapeRecords():
                atr = dict(zip(field_names, sr.record))
                geom = sr.shape.__geo_interface__
                buffer.append(dict(type="Feature", \
                geometry=geom, properties=atr)) 

            # write the GeoJSON file
            geojson1 = open(plugin_dir+"/clipped.geojson", "w")
            geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
            geojson1.close()
            layer = area

            features = layer.getFeatures()

            nogo = []
            go = []
            for feat in features:
                attr = feat.attributes()[1]
                attr1 = feat.attributes()[0]
                if attr1 == 1:
                    go.append((int(attr)))
                else:
                    nogo.append((int(attr)))
            t = sum(nogo)+sum(go)

            print("nogo",sum(nogo))
            print("go",sum(go))
            print("total",t)
            sg = sum(go)
            go = (sg *100)/t

            nogo = 100 - go
            go1.append(go)
            nogo1.append(nogo)
            print("nogo percentage",nogo)
            print("go percentage",go)
            p = "nogo area percentage  :"+str(nogo)+"\n"+"go area percentage  :"+str(go)

            QgsProject.instance().layerTreeRoot().findLayer(arcShape.id()).setItemVisibilityChecked(False)
            QgsProject.instance().layerTreeRoot().findLayer(arcShape1.id()).setItemVisibilityChecked(False)
            QgsProject.instance().layerTreeRoot().findLayer(area.id()).setItemVisibilityChecked(False)
            #QgsProject.instance().layerTreeRoot().findLayer(vlayer.id()).setItemVisibilityChecked(False)
            ip = QgsProject.instance().mapLayersByName('go_nogoArea')[0]
            viewShed = QgsProject.instance().mapLayersByName('viewShed')[0]
            Raster = QgsProject.instance().mapLayersByName('Raster')[0]

            QgsProject.instance().layerTreeRoot().findLayer(ip.id()).setItemVisibilityChecked(False)
            QgsProject.instance().layerTreeRoot().findLayer(viewShed.id()).setItemVisibilityChecked(False)
            QgsProject.instance().layerTreeRoot().findLayer(Raster.id()).setItemVisibilityChecked(False)



            self.dlg.label_percentage.setText(p)

        self.dlg.pushButton.clicked.connect(arcShape1)

        self.dlg.pushButton.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton.setToolTip('click')

        ##pie chart,
        def pieChart1():

            from matplotlib import pyplot as plt

            data = [nogo1[0], go1[0]]

            label = ['nogo', 'go']

            fig = plt.figure(figsize =(10, 5))
            plt.pie(data,labels=label,autopct='%1.1f%%')

            #plt.legend(title = "percentage")
            plt.title('nogo and go area percentage:')

            plt.show()

        self.dlg.pushButton_pie.clicked.connect(pieChart1)

        self.dlg.pushButton_pie.setStyleSheet("color: blue;font-size: 12pt; ") 
        self.dlg.pushButton_pie.setToolTip('click')
        self.dlg.pushButton_pie.hide()

        self.dlg.label_percentage.setStyleSheet("color: brown; ") 
        self.dlg.label_mapc.setStyleSheet("color: blue; ") 
        self.dlg.label.setStyleSheet("color: brown; ") 
        self.dlg.label_percentage.setStyleSheet("color: brown; ") 
        self.dlg.label_2.setStyleSheet("color: brown; ") 
        self.dlg.label_mapc_2.setStyleSheet("color: brown; ") 
        self.dlg.label_percentage.hide()
        #self.dlg.label_rad.setStyleSheet("color: brown; ") 
        
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass

