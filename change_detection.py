# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .change_detection_dialog import change_detectionDialog
import os.path
from PyQt5.QtWidgets import *
from qgis.core import QgsRasterLayer
from PyQt5.QtCore import QFileInfo
from qgis.core import QgsProject
from flask import Flask, request
from qgis.core import (QgsFeature,QgsGeometry,QgsPointXY,QgsField,QgsRaster,QgsVectorFileWriter,QgsRasterLayer,QgsApplication,QgsProject,QgsVectorLayer, QgsVectorLayer,QgsCoordinateReferenceSystem,QgsProcessingFeatureSourceDefinition,QgsFeatureRequest)
from PyQt5 import QtWidgets, QtGui

# try:
#     from .myapifile import *
#     from .myapifile import change_detection2
# except Exception as e:
#     print(e)

class change_detection:
    """QGIS Plugin Implementation."""
    src_path,ref_path ='',''

    def __init__(self, iface):
       
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'change_detection_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&change_detection')

        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('change_detection', message)


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
        icon_path = plugin_dir+'/det.jpeg'

        self.add_action(
            icon_path,
            text=self.tr(u'save change detection images'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&change_detection'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = change_detectionDialog()
            self.dlg.show()
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'BISAG-N_MeitY.jpg').scaledToWidth(120))

        def button_clicked1():
            self.src_path,filter = QFileDialog.getOpenFileName(self.dlg, 'Open a raster file', '',
                                                '*.tif')
            layer = QgsRasterLayer(self.src_path, 'source')
            QgsProject.instance().addMapLayer(layer)
            if layer.isValid() is True:
                print("Layer was loaded successfully!")
            else:
                print("Layer failed to load!")

        def button_clicked2():
            self.ref_path,filter = QFileDialog.getOpenFileName(self.dlg, 'Open a raster file', '',
                                                '*.tif')
            layer = QgsRasterLayer(self.ref_path, 'reference')
            QgsProject.instance().addMapLayer(layer)
            if layer.isValid() is True:
                print("Layer was loaded successfully!")
            else:
                print("Layer failed to load!")

        def change_detection1():
            #self.dlg.progressBar.show()
            os.system(f"python3 {plugin_dir}/myapifile.py {self.src_path} {self.ref_path}")#####3change
            
            with open(plugin_dir+'/wkt.txt',"r") as f:
                wkt = f.read()
            
            temp = QgsVectorLayer("Polygon?crs=epsg:4326", "result", "memory")
            QgsProject.instance().addMapLayer(temp)

            temp.startEditing()
            geom = QgsGeometry()
            geom = QgsGeometry.fromWkt(wkt)
            feat = QgsFeature()
            feat.setGeometry(geom)
            temp.dataProvider().addFeatures([feat])
            temp.commitChanges()

        self.dlg.pushButton.clicked.connect(button_clicked1)
        self.dlg.pushButton.setCheckable(True)
        self.dlg.pushButton_4.clicked.connect(button_clicked2)
        self.dlg.pushButton_4.setCheckable(True)
        self.dlg.pushButton_3.clicked.connect(change_detection1)
        self.dlg.pushButton_3.setCheckable(True)
        
        self.dlg.pushButton.setStyleSheet("color: green;") 
        self.dlg.pushButton_4.setStyleSheet("color: green;") 
        self.dlg.pushButton_3.setStyleSheet("color: blue;") 

        self.dlg.label_title.setStyleSheet("color: purple;") 
        self.dlg.label_4.setStyleSheet("color: red;") 

        self.dlg.label.setStyleSheet("color: brown;") 
        self.dlg.label_2.setStyleSheet("color: brown;") 
        

        self.dlg.show()
        self.dlg.exec_()
        