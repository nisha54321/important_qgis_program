# -*- coding: utf-8 -*-

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

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
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

        # icon_path = ':/plugins/equal_cellvalue/icon.png'
        # self.add_action(
        #     icon_path,
        #     text=self.tr(u'Equal Cellvalue for raster'),
        #     callback=self.run,
        #     parent=self.iface.mainWindow())
        plugin_dir = os.path.dirname(__file__)
        icon_path = plugin_dir+'/'+'bisag_n.png'        
        
        self.menu = self.iface.mainWindow().findChild( QMenu, '&Algorithm' )

        if not self.menu:
            self.menu = QMenu( '&Algorithm', self.iface.mainWindow().menuBar() )
            self.menu.setObjectName( '&Algorithm' )
            actions = self.iface.mainWindow().menuBar().actions()
            lastAction = actions[-1]
            self.iface.mainWindow().menuBar().insertMenu( lastAction, self.menu )
            self.action = QAction(QIcon(icon_path),"Equal Cellvalue", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"Equal Cellvalue", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        # will be set False in run()
        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Equal Cellvalue'),
                action)
            self.iface.removeToolBarIcon(action)


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

        rasterLyr = QgsRasterLayer("/home/bisag/Documents/demo_plugins/layer Stack.tif","Sat Image")

        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            print(coorx, coory)
            
            self.x = coorx
            self.y = coory
            # p = QgsPointXY(x,y)
            # qry = rasterLyr.dataProvider().identify(p,QgsRaster.IdentifyFormatValue)
            # qry.isValid()
            # r2 = qry.results()
            # bandselect = r2[3]
            # print(bandselect)
            # lyr = '/home/bisag/Documents/demo_plugins/layer Stack.tif'
            # #exp = '"layer Stack@3" = 1562.0'
            # exp = '"'+'layer Stack@3'+'"'+' = '+str(bandselect)
            # print(exp)
            # processing.run("qgis:rastercalculator", 
            #                 {'EXPRESSION':exp,
            #                 'LAYERS':[lyr],
            #                 'CELLSIZE':0,
            #                 'EXTENT':None,
            #                 'CRS':None,
            #                 'OUTPUT':'/home/bisag/Documents/demo_plugins/sameCellvalue.tif'})

            # rlayer = QgsRasterLayer('/home/bisag/Documents/demo_plugins/sameCellvalue.tif', "same cell value")
            # #QgsProject.instance().addMapLayer(rlayer)
            
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
            lyr = '/home/bisag/Documents/demo_plugins/layer Stack.tif'
            #exp = '"layer Stack@3" = 1562.0'
            exp = '"'+'layer Stack@'+str(index+1)+'"'+' = '+str(bandselect)
            print(exp)
            processing.run("qgis:rastercalculator", 
                            {'EXPRESSION':exp,
                            'LAYERS':[self.filename],
                            'CELLSIZE':0,
                            'EXTENT':None,
                            'CRS':None,
                            'OUTPUT':'/home/bisag/Documents/demo_plugins/sameCellvalue.tif'})

            rlayer = QgsRasterLayer('/home/bisag/Documents/demo_plugins/sameCellvalue.tif', "same cell value")
            QgsProject.instance().addMapLayer(rlayer)
            
    
        self.dlg.pushButton.clicked.connect(sameCell)


        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
