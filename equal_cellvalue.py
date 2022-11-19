# -*- coding: utf-8 -*-
##find the equal cell value find of raster image
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .equal_cellvalue_dialog import EqualCellvalueDialog
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

class EqualCellvalue:
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
            'EqualCellvalue_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Equal Cellvalue')

       
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('EqualCellvalue', message)


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
            self.action = QAction(QIcon(icon_path),"EqualCellvalue", self.iface.mainWindow())
            self.action.setObjectName( 'EqualCellvalue' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"EqualCellvalue", self.iface.mainWindow())
            self.action.setObjectName( 'EqualCellvalue' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "EqualCellvalue":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = EqualCellvalueDialog()

        getCrs = self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        print(getCrs)
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        def select():
            self.filename, _filter = QFileDialog.getOpenFileName(self.dlg, "Select   input file ","", '*.tif *.jp2')
            self.dlg.label_title_sd.setWordWrap(True)
            self.dlg.label_title_sd.setText(self.filename)

            self.rlayer = QgsRasterLayer(self.filename, "layerstack")
            QgsProject.instance().addMapLayer(self.rlayer)

            nb = self.rlayer.bandCount()

            for i in range(nb):
                cb = "Band "+str(i+1)
                self.dlg.comboBox.addItem(cb)

        self.dlg.pushButton_select.clicked.connect(select)


        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            print(coorx, coory)
            
            self.x = coorx
            self.y = coory
            
        canvas = self.iface.mapCanvas()
        pointTool = QgsMapToolEmitPoint(canvas)
        pointTool.canvasClicked.connect( display_point )
        canvas.setMapTool( pointTool )


        def sameCell():
            index = self.dlg.comboBox.currentIndex()
            print(index+1)

            p = QgsPointXY(self.x,self.y)
            qry = self.rlayer.dataProvider().identify(p,QgsRaster.IdentifyFormatValue)
            qry.isValid()
            r2 = qry.results()
            bandselect = r2[index+1]
            print(bandselect)
            #exp = '"layer Stack@3" = 1562.0'
            exp = '"'+'layerStack@'+str(index+1)+'"'+' = '+str(bandselect)
            print(exp)
            op = plugin_dir+'/sameCell.tif'
            ##value 0 and 1
            processing.run("qgis:rastercalculator", 
                            {'EXPRESSION':exp,
                            'LAYERS':[self.filename],
                            'CELLSIZE':0,
                            'EXTENT':None,
                            'CRS':None,
                            'OUTPUT':op})

            rlayer = QgsRasterLayer(op, "sameCell")
            QgsProject.instance().addMapLayer(rlayer)
            ##value 0 and selected value
            exp = '"'+'sameCell@1'+'"'+'*'+str(bandselect)

            
            print(exp)
            op = plugin_dir+'/sameCellvalue.tif'
            processing.run("qgis:rastercalculator", 
                            {'EXPRESSION':exp,
                            'LAYERS':[self.filename],
                            'CELLSIZE':0,
                            'EXTENT':None,
                            'CRS':None,
                            'OUTPUT':op})
            rlayer = QgsRasterLayer(op, "sameCellvalue")
            QgsProject.instance().addMapLayer(rlayer)

            exp = '"'+'layerStack@'+str(index+1)+'"'+'>'+str(1500)
            print(exp)
            op = plugin_dir+'/sameCell1500.tif'
            processing.run("qgis:rastercalculator", 
                            {'EXPRESSION':exp,
                            'LAYERS':[self.filename],
                            'CELLSIZE':0,
                            'EXTENT':None,
                            'CRS':None,
                            'OUTPUT':op})

            rlayer = QgsRasterLayer(op, "sameCell1500")
            QgsProject.instance().addMapLayer(rlayer)
            
            exp = '"'+'sameCell1500@1'+'"'+'*'+'"'+'layerStack@'+str(index+1)+'"'
            print(exp)
            op = plugin_dir+'/sameCell1500_layerstack.tif'
            processing.run("qgis:rastercalculator", 
                            {'EXPRESSION':exp,
                            'LAYERS':[self.filename],
                            'CELLSIZE':0,
                            'EXTENT':None,
                            'CRS':None,
                            'OUTPUT':op})

            rlayer = QgsRasterLayer(op, "sameCell1500_layerstack")
            QgsProject.instance().addMapLayer(rlayer)
    
        self.dlg.pushButton.clicked.connect(sameCell)
        self.dlg.pushButton.setStyleSheet("color: blue;font-size: 12pt; ") 
        self.dlg.pushButton.setToolTip('click')

        #self.dlg.label_title.setStyleSheet("color: brown;font-size: 12pt; ") 

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
