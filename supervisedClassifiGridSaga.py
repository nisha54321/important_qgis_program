# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Classification_raster_dialog import Classification_RasterDialog
import os.path
from PyQt5.QtCore import *

import os.path
from qgis import processing
from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsPointXY,
    QgsRaster,
    QgsRasterShader,QgsMarkerSymbol,
    QgsColorRampShader,QgsLayerTreeLayer,QgsRendererCategory,QgsSymbol,QgsCategorizedSymbolRenderer,
    QgsSingleBandPseudoColorRenderer,QgsVectorLayerTemporalProperties,QgsCoordinateReferenceSystem,QgsSvgMarkerSymbolLayer,
    QgsSingleBandColorDataRenderer,
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
from PyQt5.QtGui import QColor

class Classification_Raster:
    xy = []
    x = 0.0
    y = 0.0
    c = 1
    iii = 0
    layer = ''
    vl = ''
    filename = ''
    def __init__(self, iface):
        
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Classification_Raster_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Classification Raster')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Classification_Raster', message)


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
        icon_path = plugin_dir+'/'+'roi.png'        
        
        self.menu = self.iface.mainWindow().findChild( QMenu, '&Algorithm' )

        if not self.menu:
            self.menu = QMenu( '&Algorithm', self.iface.mainWindow().menuBar() )
            self.menu.setObjectName( '&Algorithm' )
            actions = self.iface.mainWindow().menuBar().actions()
            lastAction = actions[-1]
            self.iface.mainWindow().menuBar().insertMenu( lastAction, self.menu )
            self.action = QAction(QIcon(icon_path),"Classificatio Raster", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"Classificatio Raster", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        self.first_start = True

        # will be set False in run()
        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Classification Raster'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        if self.first_start == True:
            self.first_start = False
            self.dlg = Classification_RasterDialog()

        getCrs = self.iface.mapCanvas().mapSettings().destinationCrs().authid()

        print(getCrs)
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        if(self.iii == 0):
            self.vl = QgsVectorLayer("Point?crs="+getCrs, "markpoint", "memory")
            self.layer =  QgsVectorLayer("Polygon?crs="+getCrs, 'Train data' , "memory")
            pr = self.layer.dataProvider() 
            poly = QgsFeature()

            #Add Attribute
            self.layer.startEditing()
            pr.addAttributes([QgsField("ID", QVariant.String),QgsField("C_name", QVariant.String)])
            self.layer.updateFields() 

            #vpoi = QgsVectorLayer("Point?crs=EPSG:4326", "vectpoi", "memory") # create memory layer in WGS84
            self.iii = 1

        
        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            print(coorx, coory)
            
            self.x = coorx
            self.y = coory
            
            pnt = QgsPointXY(self.x,self.y)

            self.xy.append(pnt)
        

            symbol = QgsMarkerSymbol.createSimple({'name': 'cross2', 'color': 'red','size':'6'})
            self.vl.renderer().setSymbol(symbol)

            self.vl.triggerRepaint()

            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx, coory)))
            pr = self.vl.dataProvider()
            self.vl.triggerRepaint()

            pr.addFeature(f)
            self.vl.updateExtents() 
            self.vl.updateFields() 
            QgsProject.instance().addMapLayers([self.vl])


        canvas = self.iface.mapCanvas()
        pointTool = QgsMapToolEmitPoint(canvas)
        pointTool.canvasClicked.connect( display_point )
        canvas.setMapTool( pointTool )


        def roi():

            print("roi")
            
            pr = self.layer.dataProvider() 
            poly = QgsFeature()

            self.layer.updateFields()

            poly.setGeometry(QgsGeometry.fromPolygonXY([self.xy]))

            pr.addFeatures([poly])
            self.layer.updateExtents()

            self.layer.commitChanges()

            QgsProject.instance().addMapLayers([self.layer])

            ##show attribute table
            self.iface.showAttributeTable(self.layer)
            self.iface.mainWindow().findChild(QAction, 'mActionToggleEditing').trigger() 

            save_options = QgsVectorFileWriter.SaveVectorOptions()

            ##save roi in shapefile
            save_options.driverName = "ESRI Shapefile"  #save_options.driverName = "GPKG"
            save_options.fileEncoding = "UTF-8"
            transform_context = QgsProject.instance().transformContext()
            error = QgsVectorFileWriter.writeAsVectorFormatV2(self.layer,plugin_dir+"/roiPolygon.shp",
                                                  transform_context,
                                                  save_options)
        
            self.xy.clear()

            self.c = self.c +1

        self.dlg.pushButton_roi.clicked.connect(roi)
        self.dlg.pushButton_roi.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_roi.setToolTip('click')

        self.dlg.label.setStyleSheet("color: brown;font-size: 12pt; ") 
        self.dlg.label_2.setStyleSheet("color: blue;font-size: 12pt; ") 

        def select():
            self.filename, _filter = QFileDialog.getOpenFileName(self.dlg, "Select   input file ","", '*.tif *.jp2')
            self.dlg.label_title_sd.setWordWrap(True)
            self.dlg.label_title_sd.setText(self.filename)

            rlayer = QgsRasterLayer(self.filename, "Grid")
            QgsProject.instance().addMapLayer(rlayer)

        self.dlg.pushButton.clicked.connect(select)

        list1 =["Binary Encoding","Parallelepiped","Minimum Distance","Mahalanobis Distance","Maximum Likelihood"]
        self.dlg.comboBox.addItems(list1)

        def classification():
            #save tarin polygon layer
            self.layer.commitChanges()
            qinst = QgsProject.instance()
            qinst.removeMapLayer(qinst.mapLayersByName("markpoint")[0].id())

            print(self.filename)
            #add categorozed buffer circle using
            ls = QgsProject.instance().layerStore()
            r_layer = ls.mapLayersByName('Train data')[0]

            ficon = r_layer.fields().indexFromName('C_name')
            icon1 = r_layer.dataProvider().uniqueValues(ficon)
            icon12 = list(icon1)
            icon12.sort()
            categories = []

            for value in icon12:
                symbol = QgsSymbol.defaultSymbol(r_layer.geometryType())
                category = QgsRendererCategory(value, symbol, str(value))
                categories.append(category)
                
            renderer = QgsCategorizedSymbolRenderer('C_name', categories)
            if renderer is not None:
                r_layer.setRenderer(renderer)    
            r_layer.triggerRepaint()

            if os.path.exists(plugin_dir+'/classification.sdat'):
                os.remove(plugin_dir+'/classification.sdat')

            if os.path.exists(plugin_dir+'/quality.sdat'):
                os.remove(plugin_dir+'/quality.sdat')
            
            index = self.dlg.comboBox.currentIndex()
            print(self.filename, index)

            wta = []

            for i in range(5):
                wta.append(False)
                
            wta.insert(index, True)
            print(wta)

            ###saga algorithm 
            processing.run("saga:supervisedclassificationforgrids", 
                {'GRIDS':[self.filename],
                'NORMALISE':False,
                'CLASSES':plugin_dir+'/classification.sdat',
                'QUALITY':plugin_dir+'/quality.sdat',
                'TRAINING':r_layer,
                'TRAINING_CLASS':r_layer,
                'FILE_LOAD':'False',
                'FILE_SAVE':'False',
                'METHOD':str(index),
                'THRESHOLD_DIST':0,
                'THRESHOLD_ANGLE':0,
                'THRESHOLD_PROB':0,
                'RELATIVE_PROB':1,
                'WTA_0':wta[0],
                'WTA_1':wta[1],
                'WTA_2':wta[2],
                'WTA_3':wta[3],
                'WTA_4':wta[4],
                'WTA_5':wta[5]})
            print("success: ")

            rlayer1 = QgsRasterLayer(plugin_dir+'/classification.sdat', "classification")
            QgsProject.instance().addMapLayer(rlayer1)
            rlayer2 = QgsRasterLayer(plugin_dir+'/quality.sdat', "quality")
            QgsProject.instance().addMapLayer(rlayer2)
            

        self.dlg.pushButton_roi_2.clicked.connect(classification)
        self.dlg.pushButton_roi_2.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_roi_2.setToolTip('click')


        self.dlg.show()
        result = self.dlg.exec_()
