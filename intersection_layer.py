# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .intersection_layer_dialog import IntersectionLayerDialog
import os.path

from PyQt5 import QtGui
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,
    QgsPointXY,QgsPoint,QgsProcessingFeatureSourceDefinition ,QgsFeatureRequest,QgsVectorFileWriter,
    QgsMarkerSymbol,QgsCategorizedSymbolRenderer,QgsRendererCategory,QgsSymbol,
    QgsVectorLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField ,QgsWkbTypes,QgsSnappingConfig)
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis.gui import  QgsMapToolEmitPoint
import pandas as pd
import re
from PyQt5.QtCore import *
from qgis import processing
import datetime

class IntersectionLayer:
    xy = []
    coord = []
    x = 0.0
    y = 0.0
    c = 1
    iii = 0
    layer1 = ''
    layer2 = ''
    layer11 = ''
    layer22 = ''
    layer1type = ''
    layer2type = ''

    vl = ''
    filename = ''
    roiname = ''
    r_layer = ''
    save = ''
    lyr_list = []
    lastlayertime = ''
    lstId = 0
    addlayerpath = []
    fn = ''
    csv = ''
    layeris = ''
    field_name = []
    flag = 0
    editfid = []
    

    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'IntersectionLayer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Intersection Layer')

        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('IntersectionLayer', message)


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
            self.action = QAction(QIcon(icon_path),"IntersectionLayer", self.iface.mainWindow())
            self.action.setObjectName( 'IntersectionLayer' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"IntersectionLayer", self.iface.mainWindow())
            self.action.setObjectName( 'IntersectionLayer' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "IntersectionLayer":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = IntersectionLayerDialog()
        
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+os.sep+'BISAG-N_MeitY.jpg').scaledToWidth(120))
        
        ##add canvas layer to dropdown
        output_format = ['point','line']
        layer_canvas = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        self.dlg.comboBox.addItems(layer_canvas)
        self.dlg.comboBox_2.addItems(layer_canvas)
        self.dlg.comboBox_3.addItems(output_format)
        
        
        def selectinput():
            self.flag =0
            self.layer1, _filter = QFileDialog.getOpenFileName(self.dlg, "Select existing layer for input  ","", ' *.shp *.gpkg *.geojson')
            self.layer11 = QgsVectorLayer(self.layer1, "input layer", "ogr")
            self.dlg.comboBox.insertItem(0, "input layer")
            self.dlg.comboBox.setCurrentText("input layer")
            
            self.layer1type=QgsWkbTypes.displayString(int(self.layer11.wkbType()))
            print(self.layer1type)

            QgsProject.instance().addMapLayer(self.layer11)

            
        def selectoverlay():
            self.flag =0
            self.layer2, _filter = QFileDialog.getOpenFileName(self.dlg, "Select existing layer for overlay  ","", ' *.shp *.gpkg *.geojson')
            self.layer22 = QgsVectorLayer(self.layer2, "overlay layer", "ogr")
            self.dlg.comboBox_2.insertItem(0, "overlay layer")
            self.dlg.comboBox_2.setCurrentText("overlay layer")
            
            
            
            self.layer2type=QgsWkbTypes.displayString(int(self.layer22.wkbType()))
            print(self.layer2type)
            
            QgsProject.instance().addMapLayer(self.layer22)
            
        def EditSecondLayer():
                self.layer22 = QgsProject.instance().mapLayersByName(self.dlg.comboBox_2.currentText())[0]
                self.iface.setActiveLayer(self.layer22)
        
                self.layer22.startEditing()
                new_conf = QgsSnappingConfig(QgsProject.instance().snappingConfig())
                new_conf.setEnabled(True)
                QgsProject.instance().setSnappingConfig(new_conf)
                QgsProject.instance().setTopologicalEditing(True)
                self.iface.actionVertexTool().trigger()
                self.iface.actionAddFeature().trigger()

                
                def select(featureAdded):
                    self.layer22.select(featureAdded)

                self.layer22.featureAdded.connect(select)
                
                self.flag = 1
                
        def selectFeat():
            self.layer22 = QgsProject.instance().mapLayersByName(self.dlg.comboBox_2.currentText())[0]
            self.iface.setActiveLayer(self.layer22)
            self.iface.actionSelect().trigger()

            self.flag = 1
            
        def segmentEdit():
            self.layer22 = QgsProject.instance().mapLayersByName(self.dlg.comboBox_2.currentText())[0]
            self.layer22.startEditing()
            self.iface.setActiveLayer(self.layer22)
            self.iface.actionVertexTool().trigger()

            self.flag = 1
            
                
        def findintersect(layer1type,layer2type,layer11,layer22):
            case1 = ['MultiPolygon','Polygon']
            case2 = ['MultiLineString','LineString']
            
            if layer1type in case1 and layer2type in case2:
                print('poly-line') 
                
                if self.flag == 1:
                    res1 = processing.run("native:intersection", 
                                {'INPUT':QgsProcessingFeatureSourceDefinition(layer22.dataProvider().dataSourceUri(), selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                                    'OVERLAY':layer11,
                                    'INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'',
                                    'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'poly_line_result.shp'})
                    
                else:
                    res1 = processing.run("native:intersection", 
                                {'INPUT':layer22,
                                    'OVERLAY':layer11,
                                    'INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'',
                                    'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'poly_line_result.shp'})
                
                line1 = QgsVectorLayer(res1['OUTPUT'], "bridge", "ogr")
                
                
                ###extract line to point (line to point)
                
                res2 =processing.run("native:extractvertices",
                               {'INPUT':res1['OUTPUT'],
                                'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'poly_line_point_result.shp'})
                
                point1 = QgsVectorLayer(res2['OUTPUT'], "point", "ogr")
                
                
                output_formt1 = self.dlg.comboBox_3.currentText()
                
                if output_formt1 == 'point':
                    QgsProject.instance().addMapLayer(point1)
                else:
                    QgsProject.instance().addMapLayer(line1)
            
            elif layer1type in case1 and layer2type in case1:
                print('poly-poly')
                if self.flag == 1:
                    res1 = processing.run("native:intersection", 
                                {'INPUT':QgsProcessingFeatureSourceDefinition(layer22.dataProvider().dataSourceUri(), selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                                    'OVERLAY':layer11,
                                    'INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'',
                                    'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'poly_poly_result.shp'})
                    
                else:
                    res1 = processing.run("native:intersection", 
                                {'INPUT':layer22,
                                    'OVERLAY':layer11,
                                    'INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'',
                                    'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'poly_poly_result.shp'})
                
                res11 = QgsVectorLayer(res1['OUTPUT'], "corridor", "ogr")
                QgsProject.instance().addMapLayer(res11)
            
            elif layer1type in case2 and layer2type in case2:
                print('line-line')
                if self.flag == 1:
                    res1 = processing.run("native:lineintersections",
                                {'INPUT':QgsProcessingFeatureSourceDefinition(layer22.dataProvider().dataSourceUri(), selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                                    'INTERSECT':layer11,
                                    'INPUT_FIELDS':[],'INTERSECT_FIELDS':[],'INTERSECT_FIELDS_PREFIX':'',
                                    'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'line_line_result.shp'})
                    
                else:
                
                    res1 = processing.run("native:lineintersections",
                                {'INPUT':layer22,
                                    'INTERSECT':layer11,
                                    'INPUT_FIELDS':[],'INTERSECT_FIELDS':[],'INTERSECT_FIELDS_PREFIX':'',
                                    'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'line_line_result.shp'})
                
                line1 = QgsVectorLayer(res1['OUTPUT'], "bridge", "ogr")
                res2 =processing.run("native:extractvertices",
                               {'INPUT':res1['OUTPUT'],
                                'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'line_line_point_result.shp'})
                
                point1 = QgsVectorLayer(res2['OUTPUT'], "point", "ogr")
                
                output_formt1 = self.dlg.comboBox_3.currentText()
                
                if output_formt1 == 'point':
                    QgsProject.instance().addMapLayer(point1)
                else:
                    QgsProject.instance().addMapLayer(line1)
                
                
            elif layer1type in case2 and layer2type in case1:
                print('line-poly')
                
                if self.flag == 1:
                    res1 = processing.run("native:intersection", 
                                {'INPUT':layer11,
                                    'OVERLAY':QgsProcessingFeatureSourceDefinition(layer22.dataProvider().dataSourceUri(), selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                                    'INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'',
                                    'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'line_poly_result.shp'})
                    
                else:
                    res1 = processing.run("native:intersection", 
                                {'INPUT':layer11,
                                    'OVERLAY':layer22,
                                    'INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'',
                                    'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'line_poly_result.shp'})
                
                line1 = QgsVectorLayer(res1['OUTPUT'], "bridge", "ogr")
                
                res2 =processing.run("native:extractvertices",
                               {'INPUT':res1['OUTPUT'],
                                'OUTPUT':plugin_dir+os.sep+'output'+os.sep+'line_poly_point_result.shp'})
                
                point1 = QgsVectorLayer(res2['OUTPUT'], "point", "ogr")
                
                output_formt1 = self.dlg.comboBox_3.currentText()
                
                if output_formt1 == 'point':
                    QgsProject.instance().addMapLayer(point1)
                else:
                    QgsProject.instance().addMapLayer(line1)
            else:
                print('invalid layer:')
            
            
        def intersection(): 
            ##add all layer of panel to dropdown
            layer_canvas = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
            #self.dlg.comboBox.addItems(layer_canvas)
            self.dlg.comboBox_2.addItems(layer_canvas)
            
            if self.layer22.isEditable():
                buffer = self.layer22.editBuffer()
                #print(buffer.changedGeometries())

                changed_geom =  buffer.changedGeometries().keys() #list of feature ID
                self.editfid = list(changed_geom)
                print(list(changed_geom))

                print(self.editfid) 
                self.layer22.select(self.editfid)
                #self.layer22.commitChanges()   
                print(self.editfid) 
                   
            if self.dlg.comboBox.currentText() and self.dlg.comboBox_2.currentText():
                print('dropdown')
                
                self.layer11 = QgsProject.instance().mapLayersByName(self.dlg.comboBox.currentText())[0]
                self.layer22 = QgsProject.instance().mapLayersByName(self.dlg.comboBox_2.currentText())[0]

                selectedLayerIndex =self.dlg.comboBox.currentIndex()##input
                self.layer1type=QgsWkbTypes.displayString(int(self.layer11.wkbType()))
                
                selectedLayerIndex1 =self.dlg.comboBox_2.currentIndex()###overlay layer
                
                self.layer2type=QgsWkbTypes.displayString(int(self.layer22.wkbType()))
                
                print('index:\n',selectedLayerIndex,selectedLayerIndex1)
                print('layer:\n',self.layer11,self.layer22)
                print('type:\n',self.layer1type,self.layer2type)
                
                findintersect(self.layer1type,self.layer2type,self.layer11,self.layer22)#function call
            
            else:
                print('selected layer:')
                findintersect(self.layer1type,self.layer2type,self.layer11,self.layer22)#function call
                 
        
        self.dlg.pushButton_select.clicked.connect(selectinput)
        self.dlg.pushButton_select_2.clicked.connect(selectoverlay)
        self.dlg.pushButton.clicked.connect(intersection)  
        self.dlg.pushButton_edit.clicked.connect(EditSecondLayer)
        self.dlg.pushButton_selectfeature.clicked.connect(selectFeat)
        self.dlg.pushButton_selectfeature_2.clicked.connect(segmentEdit)
        
        self.dlg.pushButton_select.setToolTip('brows layer')
        self.dlg.pushButton_select_2.setToolTip('brows layer')
        self.dlg.pushButton.setToolTip('click')
        self.dlg.pushButton_edit.setToolTip('click')
        self.dlg.pushButton_selectfeature.setToolTip('click')
        self.dlg.pushButton_selectfeature_2.setToolTip('click')
        
        self.dlg.pushButton_select.setStyleSheet("color: green;")
        self.dlg.pushButton_select_2.setStyleSheet("color: green;")
        self.dlg.pushButton.setStyleSheet("color: green;")
        self.dlg.pushButton_edit.setStyleSheet("color: blue;")
        self.dlg.pushButton_selectfeature.setStyleSheet("color: green;")
        self.dlg.pushButton_selectfeature_2.setStyleSheet("color: green;")
        
        
        self.dlg.label.setStyleSheet("color: brown;")
        self.dlg.label_2.setStyleSheet("color: brown;")
        self.dlg.label_4.setStyleSheet("color: brown;")
        
        self.dlg.label_7.setStyleSheet("color: purple;")
        self.dlg.label_3.setStyleSheet("color: purple;")
        

        self.dlg.show()
        self.dlg.exec_()
       
