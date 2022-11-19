# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *
from .dem_hillshade_dialog import DemHillshadeDialog
import os.path
from PyQt5 import QtGui
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,
    QgsPointXY,QgsPoint,QgsProcessingFeatureSourceDefinition ,QgsRasterLayer,QgsVectorFileWriter,
    QgsMarkerSymbol,QgsCategorizedSymbolRenderer,QgsRendererCategory,QgsSymbol,
    QgsVectorLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField )
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis.gui import  QgsMapToolEmitPoint
import pandas as pd
import re
from PyQt5.QtCore import *
from qgis import processing

class DemHillshade:
    layer = ''

    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DemHillshade_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Dem_Hillshade')

       
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('DemHillshade', message)


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
            self.action = QAction(QIcon(icon_path),"DemHillshade", self.iface.mainWindow())
            self.action.setObjectName( 'DemHillshade' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"DemHillshade", self.iface.mainWindow())
            self.action.setObjectName( 'DemHillshade' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "DemHillshade":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = DemHillshadeDialog()
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+os.sep+'BISAG-N_MeitY.jpg').scaledToWidth(120))
            
        def select():
            self.layer, _filter = QFileDialog.getOpenFileName(self.dlg, "Select raster file  ","", '*.jp2 *.tif')
            rasterLayer = QgsRasterLayer(self.layer, 'raster data')
            QgsProject.instance().addMapLayer(rasterLayer)
            
        self.dlg.pushButton_select.clicked.connect(select)   
        
        def hillshade():
            Z_FACTOR = self.dlg.lineEdit.text()
            AZIMUTH = self.dlg.lineEdit_2.text()
            V_ANGLE = self.dlg.lineEdit_3.text()
            
            res = processing.run("native:hillshade", 
                           {
                            'INPUT':self.layer,
                            'Z_FACTOR':Z_FACTOR,
                            'AZIMUTH':AZIMUTH,
                            'V_ANGLE':V_ANGLE,
                            'OUTPUT':plugin_dir+f'{os.sep}hillshade.tif'})
            
            rasterLayer = QgsRasterLayer(res['OUTPUT'], 'hillshade')
            
            QgsProject.instance().addMapLayer(rasterLayer)
            
        self.dlg.pushButton.clicked.connect(hillshade)   
        

        self.dlg.show()
        result = self.dlg.exec_()
        