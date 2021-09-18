
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

from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsVectorLayerTemporalProperties
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
from qgis.utils import iface
from osgeo import ogr
from json import dumps

import shapefile
import json

class Location_Object:

    iii = 0 
    rb_icon = ""
    abcounter = 0
    vpoly = ""
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
        #icon_path = ':/plugins/location_object/icon.png'
        icon_path = '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/location_object/army1.jpeg'

        self.add_action(
            icon_path,
            text=self.tr(u'ViewShed Object'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ViewShed Object'),
                action)
            self.iface.removeToolBarIcon(action)


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

        self.dlg.label_logo.setPixmap(QtGui.QPixmap("/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/location_object/bisag_n.png").scaledToWidth(120))
  
        self.dlg.label_rad.setText("2. radius")
        svgpath = "/home/bisag/Documents/svgimg/"
        img_path = '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/location_object/'
        json_file = open(img_path +"data.json","r")
        data = json.load(json_file)        
        def select_rb(radioBtn):
            radioButton = radioBtn.sender()

            if radioButton.isChecked():
                self.jrad = str(radioButton.radius1)
                rad = radioButton.radius1 
                self.i_rad = rad

                self.rb_icon = radioButton.icon
                self.icon_path = radioButton.img

                txt = str("2. "+self.rb_icon +" radius :" )
                self.dlg.label_rad.setText(txt)

                setval = self.dlg.spinBox_rad.setValue(radioButton.radius1)
            
        if(self.abcounter == 0):
            for key,value in data.items():
            
                icon = value["icon"]
                img = value["img"]
                radius1 = value["radius"]

                self.jicon.append(icon)
                self.jimg.append(img)

                #create radio button
                radioBtn=QRadioButton(icon)

                radioBtn.icon = icon
                radioBtn.radius1 = radius1
                radioBtn.img = img

                radioBtn.toggled.connect(lambda:select_rb(radioBtn))

                #self.dlg.verticalLayout_rb.addWidget(radioBtn)

                #create label of icon image
                label = QLabel()
                label.img = img
                label.setPixmap(QtGui.QPixmap(label.img).scaledToWidth(26))

                #self.dlg.verticalLayout_iconImg.addWidget(label)


            self.abcounter = 1 

        notbounshp = "/home/bisag/Documents/1DEM/polygonNew.shp"
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
                    print(record)
                    w.record(record)
                    w.shape(shaperec.shape)
            w.close()

        
        def spinboxRad():
             
            range = self.dlg.spinBox_rad.setRange(50, 5000)

            getval = self.dlg.spinBox_rad.value()
            #getval = getval/1000
            self.r = float(getval)

        self.dlg.spinBox_rad.valueChanged.connect(spinboxRad)
        self.dlg.spinBox_rad.setRange(50, 500)
        
        #add raster file
        path_to_tif = "/home/bisag/Documents/1DEM/asterDem.tif"
        rlayer = QgsRasterLayer(path_to_tif, "Raster")
        if not rlayer.isValid():
            print("Layer failed to load!")
        
        QgsProject.instance().addMapLayer(rlayer)
        
        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            
            x = coorx
            y = coory
            print(coorx,coory)

            getval = self.dlg.spinBox_rad.value()

            self.r = float(getval)
            print(self.r)
            xy = str(coorx) +","+str(coory) + " [EPSG:4326]"


            dempath = '/home/bisag/Documents/1DEM/asterDem.tif'
            visImgOp = "/home/bisag/Documents/1DEM/visibilityanalysis.tif"
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

            pr.addFeature(f)
            vl.updateExtents() 
            vl.updateFields() 

            QgsVectorFileWriter.writeAsVectorFormat(vl, "/home/bisag/Documents/1DEM/viewpoint.shp", "UTF-8", vl.crs() , "ESRI Shapefile")

            #QgsProject.instance().addMapLayer(vl)

            polygonshp = "/home/bisag/Documents/1DEM/polygon.shp"
            processing.run("gdal:polygonize", {'INPUT':visImgOp,
                            'BAND':1,
                            'FIELD':'DN',
                            'EIGHT_CONNECTEDNESS':False,
                            'EXTRA':'',
                            'OUTPUT':polygonshp})

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
            geojson = open("/home/bisag/Documents/1DEM/geojson/mygeo.geojson", "w")
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
            #SHP TO GeoJSON                                                               
            #QgsVectorFileWriter.writeAsVectorFormat(input_shp,"/home/bisag/Documents/1DEM/geojson/qgispolygon","UTF-8",input_shp.crs(),"GeoJSON")

        canvas = iface.mapCanvas() 
        pointTool = QgsMapToolEmitPoint(canvas)

        pointTool.canvasClicked.connect( display_point )

        canvas.setMapTool( pointTool )

    
        
        
        self.dlg.show()
        result = self.dlg.exec_()
        json_file.close()
        if result:
            pass
