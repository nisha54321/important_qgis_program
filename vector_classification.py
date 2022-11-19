# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .vector_classification_dialog import VectorClassificationDialog
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
import requests

class VectorClassification:
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
            'VectorClassification_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Vector Classification')

        
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('VectorClassification', message)


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
            self.action = QAction(QIcon(icon_path),"VectorClassification", self.iface.mainWindow())
            self.action.setObjectName( 'VectorClassification' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"VectorClassification", self.iface.mainWindow())
            self.action.setObjectName( 'VectorClassification' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "VectorClassification":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = VectorClassificationDialog()
            
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+os.sep+'BISAG-N_MeitY.jpg').scaledToWidth(120))
        
        layer_canvas = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        self.dlg.comboBox.addItems(layer_canvas)
        
        def attributes():
            self.layer11 = QgsProject.instance().mapLayersByName(self.dlg.comboBox.currentText())[0]
            fieldname = [field.name() for field in self.layer11.fields()]
            self.dlg.comboBox_2.addItems(fieldname)
            self.dlg.comboBox_2.setDuplicatesEnabled(False)
        
        def selectinput():
            self.layer1, _filter = QFileDialog.getOpenFileName(self.dlg, "Select existing layer for input  ","", ' *.shp *.gpkg *.geojson')
            self.layer11 = QgsVectorLayer(self.layer1, "input layer", "ogr")
            self.dlg.comboBox.insertItem(0, "input layer")
            self.dlg.comboBox.setCurrentText("input layer")
            
            fieldname = [field.name() for field in self.layer11.fields()]
            self.dlg.comboBox_2.addItems(fieldname)
            

            QgsProject.instance().addMapLayer(self.layer11)
            
        def classify():
            ls = QgsProject.instance().layerStore()
            r_layer = ls.mapLayersByName(self.dlg.comboBox.currentText())[0]

            ficon = r_layer.fields().indexFromName(self.dlg.comboBox_2.currentText())
            icon1 = r_layer.dataProvider().uniqueValues(ficon)
            icon12 = list(icon1)
            icon12.sort()
            categories = []

            for value in icon12:
                symbol = QgsSymbol.defaultSymbol(r_layer.geometryType())
                category = QgsRendererCategory(value, symbol, str(value))
                categories.append(category)
                
            renderer = QgsCategorizedSymbolRenderer(self.dlg.comboBox_2.currentText(), categories)
            if renderer is not None:
                r_layer.setRenderer(renderer)    
            r_layer.triggerRepaint()
            
            ##create style sld using pyqgis:
            name = r_layer.name()
            pathqml = f'{plugin_dir}'+os.sep+str(name)+'.qml'  
            pathsld = f'{plugin_dir}'+os.sep+str(name)+'.sld'  
            r_layer.saveNamedStyle(pathqml)
            r_layer.saveSldStyle(pathsld)
            
            
            resource_id = self.dlg.comboBox.currentText()#store name
            auth = ("admin", "geoserver")
            workspace1 = 'bisag'
            print(workspace1,"workspace1")

            url = "http://localhost:8080/geoserver/rest/workspaces/"+workspace1+"/datastores/" + resource_id + "/external.shp"
            data = "file:////"+r_layer.dataProvider().dataSourceUri()

            response = requests.put(url, data=data, auth=auth)
            print(response.text)

            print("success to publish:")
            
            # ##apply style('workd)
            
            # params = (
            #     ('name', '2'),
            # )

            # x = '/home/bisag/Desktop/style/'
            # with open(f'{x}6B4D.sld', 'r') as f:
            #         style = f.read()  
                        
            # resp = requests.post(url = 'http://localhost:8080/geoserver/rest/styles', params=params, data=style, auth=('admin', 'geoserver'), headers={'Content-type': 'application/vnd.ogc.sld+xml'})
            # print(resp.status_code,resp)


            # headers = {'Content-Type': 'application/xml'}
            # headers={'Content-type': 'application/vnd.ogc.sld+xml'}

            # xmlStyle = '''
            #                 <layer>
            #                     <styles>
            #                         <name>2</name> 
            #                         <workspace>demo</workspace>
            #                     </styles>
            #                 </layer>
            #             '''
            # styleURL = 'http://localhost:8080/geoserver/rest/layers/demo:6B4D'
            # headers = {'Content-type': 'text/xml', 'Accept': 'text/xml'}

            # styleRequest = requests.put(styleURL, auth=('admin', 'geoserver'), data=xmlStyle, headers=headers)
            # print(styleRequest.status_code)
    

           
            
        self.dlg.pushButton_select.clicked.connect(selectinput)
        self.dlg.pushButton.clicked.connect(classify)
        
        
        self.dlg.pushButton_select_2.clicked.connect(attributes)
        self.dlg.pushButton_select_2.setIcon(QIcon(f'{plugin_dir}{os.sep}refresh.png'))
        #self.dlg.pushButton_select_2.setStyleSheet(f"background-image : url({plugin_dir}{os.sep}refresh.png);")

        
        
        self.dlg.pushButton_select.setToolTip('brows layer')
        self.dlg.pushButton.setToolTip('classify')
        
        
        self.dlg.pushButton_select.setStyleSheet("color: green;")
        self.dlg.pushButton.setStyleSheet("color: green;")
        
        
        self.dlg.label.setStyleSheet("color: brown;")
        self.dlg.label_2.setStyleSheet("color: brown;")
        self.dlg.label_4.setStyleSheet("color: brown;")
        
        self.dlg.label_7.setStyleSheet("color: purple;")
        self.dlg.label_3.setStyleSheet("color: purple;")

        self.dlg.show()
        self.dlg.exec_()
        
