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

from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsVectorLayerTemporalProperties,QgsField,QgsPointXY,QgsPalLayerSettings,QgsVectorLayerSimpleLabeling,QgsSvgMarkerSymbolLayer,QgsMarkerSymbol,QgsCentroidFillSymbolLayer,QgsFillSymbol,QgsSimpleFillSymbolLayer,QgsRendererCategory,QgsCategorizedSymbolRenderer,QgsCategorizedSymbolRenderer
               
from PyQt5.QtCore import QFileInfo
# Initialize Qt resources from file resources.py

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

from .resources import *
from .image_canvas_dialog import Image_CanvasDialog
import os.path
import json

class Image_Canvas:
    iii = 0 
    rb_icon = ""
    abcounter = 0
    vpoly = ""
    renderer = ""
    renderer1 = ""

    plugin_path = os.path.dirname(__file__)
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
    
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Image_Canvas_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Icon_Buffer')
       
        self.first_start = None

    def tr(self, message):   
        return QCoreApplication.translate('Icon_Buffer', message)


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
            self.action = QAction(QIcon(icon_path),"Icon_Buffer", self.iface.mainWindow())
            self.action.setObjectName( 'Icon_Buffer' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"Icon_Buffer", self.iface.mainWindow())
            self.action.setObjectName( 'Icon_Buffer' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "Icon_Buffer":
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
            self.dlg = Image_CanvasDialog()

        self.dlg.label_logo.setPixmap(QtGui.QPixmap(self.plugin_path+"/bisag_n.png").scaledToWidth(120))
  
        self.dlg.label_rad.setText("2. radius")
        #svgpath = "/home/bisag/Documents/svgimg/"
        img_path = self.plugin_path+"/"
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

                self.dlg.verticalLayout_rb.addWidget(radioBtn)

                #create label of icon image
                label = QLabel()
                label.img = img
                label.setPixmap(QtGui.QPixmap(label.img).scaledToWidth(26))

                self.dlg.verticalLayout_iconImg.addWidget(label)


            self.abcounter = 1  
        
        def spinboxRad():
             
            range = self.dlg.spinBox_rad.setRange(50, 500)

            getval = self.dlg.spinBox_rad.value()
            self.r = float(getval)

        self.dlg.spinBox_rad.valueChanged.connect(spinboxRad)
        self.dlg.spinBox_rad.setRange(50, 500)
        
        #get coordinates of mapcanvas
        def display_point( pointTool ): 

            rad = self.i_rad

            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))

            self.x = coorx
            self.y = coory

            if(self.rb_icon == ""):
                print("select any value")
                self.iface.messageBar().pushMessage("please", "select youre choice for icon  ", level=Qgis.Critical)

            
            else :
                f = QgsFeature()
                lname = "Buffer"
                if(self.iii == 0):
                    self.vpoly = QgsVectorLayer("Polygon?crs=EPSG:4326", lname , "memory")
                    self.iii = 1

                symbol1 = QgsSymbol.defaultSymbol(self.vpoly.geometryType())

                symbol = QgsSymbol.defaultSymbol(self.vpoly.geometryType())
                symbol.setColor(QColor("#c97653")) 
                symbol.symbolLayer(0).setBrushStyle(Qt.BrushStyle(Qt.FDiagPattern))
                symbol.symbolLayer(0).setStrokeColor(QColor("#f5c9c9"))

                self.vpoly.triggerRepaint()

                pr = self.vpoly.dataProvider()
                self.vpoly.startEditing()

                pr.addAttributes([QgsField("Icon_name", QVariant.String),QgsField("Img_path",  QVariant.String)])
                self.vpoly.updateFields()

                #add attribute table value
                f = QgsFeature()
                attvalAdd = [self.rb_icon,self.icon_path]
                f.setAttributes(attvalAdd)
                
                self.vpoly.triggerRepaint()

                getval = self.dlg.spinBox_rad.value()

                self.r = float(getval)
                
                self.r = self.r/5000
                print(self.r)
                pr = self.vpoly.dataProvider()

                #add polygon map canvas 
                f.setGeometry( QgsGeometry.fromPointXY(QgsPointXY(self.x, self.y)).buffer(self.r,7))
                pr.deleteAttributes
                self.vpoly.startEditing()
                pr.addFeatures( [f] )
                self.vpoly.commitChanges()
                QgsProject.instance().addMapLayer(self.vpoly)

                #set label
                vlayer = iface.activeLayer()

                #set display of html maptip

                expression = """<img src="file:///[%Img_path%]" width="350" height="250">"""
                vlayer.setMapTipTemplate(expression)

                layer_settings  = QgsPalLayerSettings()
                layer_settings.fieldName = "Icon_name"
                layer_settings.placement = 2
                layer_settings.enabled = True

                layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
                vlayer.setLabelsEnabled(True)
                vlayer.setLabeling(layer_settings)
                vlayer.triggerRepaint()
                QgsProject.instance().addMapLayer(vlayer)
                vlayer.startEditing()

        canvas = self.iface.mapCanvas() 
        pointTool = QgsMapToolEmitPoint(canvas)
        pointTool.canvasClicked.connect( display_point )
        canvas.setMapTool( pointTool )     
        
        def svgshow():
            #add categorozed base image
            ls = QgsProject.instance().layerStore()
            r_layer = ls.mapLayersByName('Buffer')[0]

            fni = r_layer.fields().indexFromName('Img_path')
            unique_ids = r_layer.dataProvider().uniqueValues(fni)

            ficon = r_layer.fields().indexFromName('Icon_name')
            icon1 = r_layer.dataProvider().uniqueValues(ficon)
            icon12 = list(icon1)
            icon12.sort()

            imgs = list(unique_ids)
            imgs.sort()

            ii = 0
            categories = []
            for unique_id in unique_ids:
                symbol1 = QgsSymbol.defaultSymbol(r_layer.geometryType())
                
                svgStyle1 = {
                    "name": str(unique_id),
                    "outline": "#51a333",
                    "size": '20',
                    }  
                #
                symbol_layer = QgsSvgMarkerSymbolLayer.create(svgStyle1)
                svgSymbol = QgsMarkerSymbol()
                svgSymbol.changeSymbolLayer(0, symbol_layer)

                centroid = QgsCentroidFillSymbolLayer()
                centroid.setSubSymbol(svgSymbol)
                selectedSymbol = QgsFillSymbol()
                selectedSymbol.changeSymbolLayer(0, centroid)
                
                lbl = str(icon12[ii])
                category = QgsRendererCategory(unique_id, selectedSymbol, lbl,True)
                categories.append(category)

                #add circle
                layer_style = {}
                layer_style['color'] = '%d, %d, %d' % (randrange(0, 256), randrange(0, 256), randrange(0, 256))
                layer_style['outline'] = '#000000'
                symbolLayer1 = QgsSimpleFillSymbolLayer.create(layer_style)

                if symbolLayer1 is not None:
                    symbol1.changeSymbolLayer(0, symbolLayer1)
                    
                bfrnm = "circle_"+str(ii)
                category1 = QgsRendererCategory(lbl, symbol1, bfrnm, True)
                categories.append(category1)
                
                ii = ii + 1
                
            self.renderer = QgsCategorizedSymbolRenderer('Img_path', categories) #Icon_name ,Img_path

            if self.renderer is not None:
                r_layer.setRenderer(self.renderer) 
            r_layer.triggerRepaint()

        self.dlg.pushButton_imgshow.clicked.connect(svgshow)

        def buffershow():
            #add categorozed buffer circle using
            ls = QgsProject.instance().layerStore()
            r_layer = ls.mapLayersByName('Buffer')[0]

            ficon = r_layer.fields().indexFromName('Icon_name')
            icon1 = r_layer.dataProvider().uniqueValues(ficon)
            icon12 = list(icon1)
            icon12.sort()
            categories = []

            for value in icon12:
                symbol = QgsSymbol.defaultSymbol(r_layer.geometryType())
                category = QgsRendererCategory(value, symbol, str(value))
                categories.append(category)
                
            renderer = QgsCategorizedSymbolRenderer('Icon_name', categories)
            if renderer is not None:
                r_layer.setRenderer(renderer)    
            r_layer.triggerRepaint()


        self.dlg.pushButton_bfrshow.clicked.connect(buffershow)

        self.dlg.label_info.setStyleSheet("color: green; ")
        self.dlg.label_rad.setStyleSheet("color: green;")
        self.dlg.label_mapc.setStyleSheet("color: green;")
        self.dlg.pushButton_imgshow.setStyleSheet("color: brown;font-size: 13pt; ")
        self.dlg.pushButton_bfrshow.setStyleSheet("color: brown;font-size: 13pt; ")

        self.dlg.show()
        
        self.dlg.exec_()
        json_file.close()