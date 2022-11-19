# -*- coding: utf-8 -*-
###find ndvi
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .raster_calculator_dialog import Raster_CalculatorDialog
import os.path
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,QgsRasterLayer,
    QgsPathResolver
)
from qgis import processing
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from qgis.analysis import  *


class Raster_Calculator:
    """QGIS Plugin Implementation."""
    filename = ''
    layers = ''
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
            'Raster_Calculator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Raster Calculator')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
       
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Raster_Calculator', message)


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
            self.action = QAction(QIcon(icon_path),"Raster_Calculator", self.iface.mainWindow())
            self.action.setObjectName( 'Raster_Calculator' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"Raster_Calculator", self.iface.mainWindow())
            self.action.setObjectName( 'Raster_Calculator' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "Raster_Calculator":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):

        if self.first_start == True:
            self.first_start = False
            self.dlg = Raster_CalculatorDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        ##brows layer
        def select():
            self.filename, _filter = QFileDialog.getOpenFileNames(self.dlg, "Select   input file ","", '*.tif *.shp *jp2')

            for pathlayer in self.filename:
                l2 = str(pathlayer).split("/")[-1][:-4]
                rlayer = QgsRasterLayer(pathlayer, l2)
                QgsProject.instance().addMapLayer(rlayer)

            self.layers = QgsProject.instance().layerTreeRoot().children()
            layers_name = [layer.name() for layer in self.layers]

            layers_name1 = []
            for i in layers_name:
                i = i +"@1"
                layers_name1.append(i)
            print(layers_name1)

            self.dlg.comboBox_red.addItems(layers_name1)
            self.dlg.comboBox_nir.addItems(layers_name1)

        self.dlg.pushButton_select.clicked.connect(select)
        
        entries = []
        entries1 = []
        def calculate():

            selectedLayerIndex = self.dlg.comboBox_nir.currentIndex()
            selectedLayer_nir = self.layers[selectedLayerIndex].layer().name()+"@1"
            selectedLayer_nir_name = self.layers[selectedLayerIndex].layer().name()
            

            selectedLayerIndex = self.dlg.comboBox_red.currentIndex()
            selectedLayer_red = self.layers[selectedLayerIndex].layer().name()+"@1"
            selectedLayer_lyr = self.layers[selectedLayerIndex].layer().name()

            exp = '('+'"'+selectedLayer_nir+'"'+'-'+'"'+ selectedLayer_red+'"'+')/('+'"'+selectedLayer_nir+'"'+'+'+'"'+ selectedLayer_red+'"'+')'

            self.dlg.label_title_pd.setWordWrap(True)
            self.dlg.label_title_pd.setText(exp)
            
            # print(selectedLayer_red, selectedLayer_nir)
            print("selectedLayer_lyr:    ",selectedLayer_lyr)
            print("selectedLayer_red:  ", selectedLayer_red)
            print("selectedLayer_nir :  ", selectedLayer_nir)

            print(exp)
            
            #print(rlayer.bandCount())
            lyr = '/home/bisag/Documents/demo_plugins/Image Module/Layer stack/IMG_DATA/'+selectedLayer_lyr+'.jp2'
            print(lyr)
            processing.run("qgis:rastercalculator", 
                            {'EXPRESSION':exp,
                            'LAYERS':[lyr],
                            'CELLSIZE':0,
                            'EXTENT':None,
                            'CRS':None,
                            'OUTPUT':plugin_dir+'/raster_calculator_test.tif'})
            
            rlayer = QgsRasterLayer(plugin_dir+'/raster_calculator_test.tif', "Raster_calculation Image")
            QgsProject.instance().addMapLayer(rlayer)
            
        self.dlg.pushButton_run.clicked.connect(calculate)

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            
            pass
## {'EXPRESSION':'('+selectedLayer_red+'-'+ selectedLayer_nir +')' +'/'+'('+selectedLayer_red+'+'+ selectedLayer_nir+')',

