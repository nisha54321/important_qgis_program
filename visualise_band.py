# -*- coding: utf-8 -*-
##show any single band of multiband raster iamge
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .visualise_band_dialog import VisualiseBandDialog
import os.path
from qgis import processing
from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsPointXY,
    QgsRaster,
    QgsRasterShader,QgsMarkerSymbol,QgsContrastEnhancement,QgsRasterBandStats,
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

class VisualiseBand:
    """QGIS Plugin Implementation."""
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
            'VisualiseBand_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Visualise Band')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('VisualiseBand', message)


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
            self.action = QAction(QIcon(icon_path),"VisualiseBand", self.iface.mainWindow())
            self.action.setObjectName( 'VisualiseBand' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"VisualiseBand", self.iface.mainWindow())
            self.action.setObjectName( 'VisualiseBand' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "VisualiseBand":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
    
        if self.first_start == True:
            self.first_start = False
            self.dlg = VisualiseBandDialog()

        getCrs = self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        print(getCrs)
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        def select():
            self.filename, _filter = QFileDialog.getOpenFileName(self.dlg, "Select   input file ","", '*.tif *.jp2')
            self.dlg.label_title_sd.setWordWrap(True)
            self.dlg.label_title_sd.setText(self.filename)

            rlayer = QgsRasterLayer(self.filename, "layerstack")
            QgsProject.instance().addMapLayer(rlayer)

            nb = rlayer.bandCount()

            for i in range(nb):
                cb = "Band "+str(i+1)
                self.dlg.comboBox.addItem(cb)

        self.dlg.pushButton_select.clicked.connect(select)

        def showband():
            index = self.dlg.comboBox.currentIndex()
            print(index)

            layer=self.iface.activeLayer()

            myGrayRenderer = QgsSingleBandGrayRenderer(layer.dataProvider(), index+1)

            layer.setRenderer(myGrayRenderer)

            renderer = layer.renderer()
            provider = layer.dataProvider()

            layer_extent = layer.extent()
            uses_band = renderer.usesBands()
            print(uses_band)
            myType = renderer.dataType(uses_band[0])

            stats = provider.bandStatistics(uses_band[0], 
                                            QgsRasterBandStats.All, 
                                            layer_extent, 
                                            0)

            myEnhancement = QgsContrastEnhancement(myType)

            contrast_enhancement = QgsContrastEnhancement.StretchToMinimumMaximum

            myEnhancement.setContrastEnhancementAlgorithm(contrast_enhancement,True)
            myEnhancement.setMinimumValue(stats.minimumValue)
            myEnhancement.setMaximumValue(stats.maximumValue)

            layer.renderer().setContrastEnhancement(myEnhancement)
            layer.triggerRepaint()

        self.dlg.pushButton.clicked.connect(showband)

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
