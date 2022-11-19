# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .route_buffer_dialog import RouteBufferDialog
import os.path
import os.path
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis.gui import QgsMapToolEmitPoint
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,QgsRasterLayer,QgsPoint,QgsFeature,QgsVectorFileWriter,QgsPointXY,QgsField,QgsPalLayerSettings,QgsVectorLayerSimpleLabeling,
    QgsPathResolver,QgsVectorLayer,QgsGeometry,QgsTextFormat
)
from qgis.core import ( QgsApplication,QgsProject,QgsVectorLayer, QgsVectorLayer,QgsCoordinateReferenceSystem,QgsProcessingFeatureSourceDefinition,QgsFeatureRequest)
from osgeo import ogr, osr
from json import dumps
import sys
import shapefile
import time
from qgis.core import *

from qgis import processing
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QCheckBox, QListView, QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QCheckBox
import shutil

class RouteBuffer:
    iii = 0
    vl =''
    xy1 = []
    xy = []
    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RouteBuffer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Route Buffer')

        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('RouteBuffer', message)


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
            self.action = QAction(QIcon(icon_path),"RouteBuffer", self.iface.mainWindow())
            self.action.setObjectName( 'RouteBuffer' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"RouteBuffer", self.iface.mainWindow())
            self.action.setObjectName( 'RouteBuffer' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "RouteBuffer":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):

        if self.first_start == True:
            self.first_start = False
            self.dlg = RouteBufferDialog()
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))
        
        if(self.iii == 0):
            # self.iface.actionSelect().trigger()############enable select tools
            
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
            
        self.dlg.pushButton.clicked.connect(mobility)  

        def click1():
            pointTool.canvasClicked.connect( display_point1 )
            canvas.setMapTool( pointTool )

        self.dlg.pushButton_2.clicked.connect(click1)  

        self.dlg.show()
        self.dlg.exec_()
        