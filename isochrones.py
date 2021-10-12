# -*- coding: utf-8 -*-
###create boundry from go to source to destination according to time
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis.core import Qgis
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .iso_chrones_dialog import IsoChronesDialog
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
from time import strftime, time
from time import gmtime
from PyQt5.QtGui import QColor

class IsoChrones:
    filename = ''
    rlayer = ''
    x = 0.0
    y = 0.0
    def __init__(self, iface):
        
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'IsoChrones_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Iso Chrones')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('IsoChrones', message)


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
        icon_path = plugin_dir+'/'+'bisag_n.png'        
        
        self.menu = self.iface.mainWindow().findChild( QMenu, '&Algorithm' )

        if not self.menu:
            self.menu = QMenu( '&Algorithm', self.iface.mainWindow().menuBar() )
            self.menu.setObjectName( '&Algorithm' )
            actions = self.iface.mainWindow().menuBar().actions()
            lastAction = actions[-1]
            self.iface.mainWindow().menuBar().insertMenu( lastAction, self.menu )
            self.action = QAction(QIcon(icon_path),"Iso Chrones", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"Iso Chrones", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        # will be set False in run()
        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Iso Chrones'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = IsoChronesDialog()
        getCrs = self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        print(getCrs)
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        def select():
            self.filename, _filter = QFileDialog.getOpenFileName(self.dlg, "Select   input file ","", '*.shp *.gpkg')
            self.dlg.label_title_sd.setWordWrap(True)
            self.dlg.label_title_sd.setText(self.filename)

            self.rlayer = QgsVectorLayer(self.filename, "network layer")
            QgsProject.instance().addMapLayer(self.rlayer)

        self.dlg.pushButton_select.clicked.connect(select)

        list1 = ["Shortest", "Fastest"]
        self.dlg.comboBox.addItems(list1)

        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            print(coorx, coory)
            self.x = coorx
            self.y = str(coorx)+','+str(coory)+' ['+str(getCrs)+']'

            vl = QgsVectorLayer("Point?crs="+str(getCrs), "points", "memory")
            vl.renderer().symbol().setColor(QColor("green"))
    
            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx, coory)))
            pr = vl.dataProvider()
            #add attTbl
            
            vl.startEditing()
            
            vl.triggerRepaint()

            pr.addFeature(f)
            vl.updateExtents() 
            vl.updateFields() 
            vl.commitChanges()
            QgsProject.instance().addMapLayers([vl])

            #self.iface.actionPan().trigger()
    
            
        canvas = self.iface.mapCanvas()
        pointTool = QgsMapToolEmitPoint(canvas)
        pointTool.canvasClicked.connect( display_point )
        canvas.setMapTool( pointTool )

        def methodPath():
            ct = self.dlg.comboBox.currentText()
            time1 = self.dlg.lineEdit.text()
            self.dlg.pushButton.show()
            if ct == "Shortest":
                self.dlg.label_3.setText("3. Distance :")
                self.dlg.label_3.show()
                self.dlg.lineEdit.show()
                #print("shortest:")
                self.dlg.label_5.show()
                self.dlg.label_6.show()
                self.dlg.lineEdit_2.show()

            else:
                self.dlg.label_3.setText("3. Time (Second):")
                self.dlg.label_3.show()
                self.dlg.lineEdit.show()
                self.dlg.label_5.show()
                self.dlg.label_6.show()

                self.dlg.lineEdit_2.show()
                #print("Fastest:")
            self.iface.messageBar().pushMessage("PLEASE SELECT ANY POINT IN MAPCANVAS", level=Qgis.Info)

        self.dlg.pushButton_2.clicked.connect(methodPath)

        def findisochrones():
            method = self.dlg.comboBox.currentIndex()
            sp = self.dlg.lineEdit_2.text()
            tmyaDis = self.dlg.lineEdit.text()


            if os.path.exists(plugin_dir+'/interpolation.tif'):
                os.remove(plugin_dir+'/interpolation.tif')
            if os.path.exists(plugin_dir+'/isochrones.shp'):
                os.remove(plugin_dir+'/isochrones.shp')

            print(method,sp,tmyaDis,self.filename,self.y)

            processing.run("qneat3:isoareaaspolygonsfrompoint", 
                {'INPUT':self.filename,
                'START_POINT':self.y,
                'MAX_DIST':tmyaDis,
                'INTERVAL':10,
                'CELL_SIZE':10,
                'STRATEGY':method,
                'ENTRY_COST_CALCULATION_METHOD':0,
                'DIRECTION_FIELD':'',
                'VALUE_FORWARD':'',
                'VALUE_BACKWARD':'',
                'VALUE_BOTH':'',
                'DEFAULT_DIRECTION':2,
                'SPEED_FIELD':'',
                'DEFAULT_SPEED':sp,
                'TOLERANCE':0,
                'OUTPUT_INTERPOLATION':plugin_dir+'/interpolation.tif',
                'OUTPUT_POLYGONS':plugin_dir+'/isochrones.shp'})

            # processing.run("native:serviceareafrompoint",
            #          {'INPUT':self.filename,
            #          'STRATEGY':method,
            #          'DIRECTION_FIELD':'',
            #          'VALUE_FORWARD':'',
            #          'VALUE_BACKWARD':'',
            #          'VALUE_BOTH':'',
            #          'DEFAULT_DIRECTION':2,
            #          'SPEED_FIELD':'',
            #          'DEFAULT_SPEED':sp,
            #          'TOLERANCE':0,
            #          'START_POINT':self.y,
            #          'TRAVEL_COST2':tmyaDis,
            #          'INCLUDE_BOUNDS':False,
            #          'OUTPUT_LINES':plugin_dir+'IsochroneLine.shp'})

            rlayer = QgsRasterLayer(plugin_dir+'/interpolation.tif', "isochrones")
            QgsProject.instance().addMapLayer(rlayer)

            # processing.run("native:convexhull", 
            #                 {'INPUT':plugin_dir+'IsochroneLine.shp',
            #                 'OUTPUT':plugin_dir+'Isochrones.shp'})

            processing.run("native:dissolve", {'INPUT':plugin_dir+'/isochrones.shp',
                                                'FIELD':[],
                                                'OUTPUT':plugin_dir+'/IsochroneBoundry.shp'})
            
            rlayer = QgsVectorLayer(plugin_dir+'/IsochroneBoundry.shp', "polygon ")
            QgsProject.instance().addMapLayer(rlayer)


        self.dlg.pushButton.clicked.connect(findisochrones)
        self.dlg.pushButton.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_2.setStyleSheet("color: blue;font-size: 12pt; ") 

        self.dlg.label_2.setStyleSheet("color: brown;font-size: 12pt; ") 

        self.dlg.pushButton.setToolTip('click')

        self.dlg.label_3.hide()
        self.dlg.lineEdit.hide()

        self.dlg.label_5.hide()
        self.dlg.lineEdit_2.hide()
        self.dlg.label_6.hide()
        self.dlg.pushButton.hide()

        self.dlg.show()
        result = self.dlg.exec_()
        
#         import psycopg2

#         connection = psycopg2.connect(user="postgres", password="postgres", host="localhost", database="project")

#         cursor = connection.cursor()

#         distance = "0.008"

#         mc = iface.mapCanvas()
#         lyr = iface.activeLayer()

#         mapTool = QgsMapToolIdentifyFeature(mc)
#         mapTool.setLayer(lyr)
#         mc.setMapTool(mapTool) 
#         def onFeatureIdentified(feature):
#             source = str(feature.attributes()[0])
#             print(source) 
#             #cursor.execute("CREATE  OR REPLACE VIEW view AS SELECT di.seq, di.id1, di.id2, di.cost, pt.id, pt.geom FROM pgr_drivingdistance('SELECT id,source,target, st_length(geom) as cost FROM network',%s,%s,FALSE)di(seq, id1, id2, cost)JOIN network_nodes pt ON di.id1 = pt.id;", (source, distance))



#         mapTool.featureIdentified.connect(onFeatureIdentified)    
#         cursor.execute("CREATE  OR REPLACE VIEW view AS SELECT di.seq, di.id1, di.id2, di.cost, pt.id, pt.geom FROM pgr_drivingdistance('SELECT id,source,target, st_length(geom) as cost FROM network',1845,0.005,FALSE)di(seq, id1, id2, cost)JOIN network_nodes pt ON di.id1 = pt.id;")
#         connection.commit()

#         cursor.close()

#         connection.close()
        if result:
            pass
