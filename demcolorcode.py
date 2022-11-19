# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *
from .demcolorcode_dialog import DemColorcodeDialog
import os.path
from PyQt5 import QtGui
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,
    QgsPointXY,QgsPoint,QgsProcessingFeatureSourceDefinition ,QgsRasterLayer,QgsVectorFileWriter,
    QgsMarkerSymbol,QgsCategorizedSymbolRenderer,QgsRendererCategory,QgsSymbol,QgsRasterBandStats,QgsStyle,QgsColorRampShader,QgsRasterShader,QgsSingleBandPseudoColorRenderer,
    QgsVectorLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField )
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis.gui import  QgsMapToolEmitPoint
import pandas as pd
import re
from PyQt5.QtCore import *
from qgis import processing
from qgis.PyQt.QtGui import QColor

class DemColorcode:
    layer = ''
    rasterLayer = ''

    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DemColorcode_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Dem Colorcode')

       
        self.first_start = None

    def tr(self, message):
        
        return QCoreApplication.translate('DemColorcode', message)


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
            self.action = QAction(QIcon(icon_path),"DemColorcode", self.iface.mainWindow())
            self.action.setObjectName( 'DemColorcode' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"DemColorcode", self.iface.mainWindow())
            self.action.setObjectName( 'DemColorcode' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "DemColorcode":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = DemColorcodeDialog()
            
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+os.sep+'BISAG-N_MeitY.jpg').scaledToWidth(120))
            
        def select():
            self.layer, _filter = QFileDialog.getOpenFileName(self.dlg, "Select raster file  ","", '*.jp2 *.tif')
            self.rasterLayer = QgsRasterLayer(self.layer, 'raster data')
            QgsProject.instance().addMapLayer(self.rasterLayer)
            
        self.dlg.pushButton_select.clicked.connect(select)   
        def colorCode():
            import re
            number_classes = self.dlg.lineEdit.text()
            number_classes = int(number_classes)

            layer = self.rasterLayer
            renderer = layer.renderer()
            provider = layer.dataProvider()

            band = renderer.usesBands()#

            min = provider.bandStatistics(band[0], QgsRasterBandStats.All).minimumValue
            max = provider.bandStatistics(band[0], QgsRasterBandStats.All).maximumValue

            print ("min: {:.1f}, max: {:.1f}".format(min, max))

            myStyle = QgsStyle().defaultStyle()

            ramp_names = myStyle.colorRampNames()

            dict = {}

            for i, name in enumerate(ramp_names):
                dict[ramp_names[i]] = i 
            print(dict)
            #print ('RdYlGn ramp is number:', dict['RdYlGn'])

            ramp = myStyle.colorRamp('RdYlGn')  #RdYlGn ramp
            print (ramp_names[dict['RdYlGn']])

            rp = ramp.properties()
            print (rp)

            #To set an interpolated color RdYlGn ramp shader with five classes

            interval = (max - min)/(number_classes -1 )
            print ("class interval: ", interval)

            #classes
            sum = min
            classes = []

            for i in range(number_classes):
                tmp = int(round(sum, 0))
                #print ('class {:d}: {:d}'.format(i+1, tmp))
                classes.append(tmp)
                sum += interval

            #print ("classes: ", classes)

            c1 = [ int(element) for element in rp['color1'].split(',') ]
            stops = [ element for element in re.split('[,;:]', rp['stops']) ]
            c2 = [ int(element) for element in rp['color2'].split(',') ]

            color_list = [ QgsColorRampShader.ColorRampItem(classes[0], QColor(c1[0],c1[1],c1[2], c1[3])),
                        QgsColorRampShader.ColorRampItem(classes[1], QColor(int(stops[1]),int(stops[2]),int(stops[3]),int(stops[4]))),
                        QgsColorRampShader.ColorRampItem(classes[2], QColor(int(stops[6]),int(stops[7]),int(stops[8]),int(stops[9])))
                            ]
            color_list = []
            color_name  =[QColor(146, 0, 255, 1),QColor(125, 0, 255, 127),QColor(127, 0, 255, 127),QColor(0, 125, 255, 127),QColor(0, 34, 255, 127),QColor(0, 255, 0, 127),QColor(0, 0, 255, 127),QColor(255, 34, 255, 127),QColor(120, 130, 125, 127),QColor(10, 10, 10, 127),QColor(255, 78, 255, 127)]
            color_name = [QColor('#d7191c'),QColor('#e44a33'),QColor('#f17c4a'),QColor("#fdae61"),QColor('#ffe4a0'),QColor('#ffffbf'),QColor('#e3f4b6'),QColor('#c7e9ad'),QColor('#abdda4'),QColor('#80bfac'),QColor('#56a1b3'),QColor('#2b83ba'),
            QColor(''),QColor('#82423d'),QColor('#235ea1')]
            i = 0
            for class1 in classes:
                
                val =QgsColorRampShader.ColorRampItem(class1, color_name[i])
                color_list.append(val)
                i = i+1
                
            myRasterShader = QgsRasterShader()
            myColorRamp = QgsColorRampShader()

            myColorRamp.setColorRampItemList(color_list)
            #myColorRamp.setColorRampType(QgsColorRampShader.DISCRETE)
            myRasterShader.setRasterShaderFunction(myColorRamp)

            myPseudoRenderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1,  myRasterShader)

            layer.setRenderer(myPseudoRenderer)

            layer.triggerRepaint()
            
            QgsProject.instance().addMapLayer(layer)
            
        self.dlg.pushButton.clicked.connect(colorCode)   
        
        self.dlg.show()
        result = self.dlg.exec_()
        