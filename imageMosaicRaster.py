# -*- coding: utf-8 -*-
##multiple tiles will be merge(chhatisgadh Bodla 8 bit unsiged bit)
import gdal

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .image_mosaic_dialog import ImageMosaicDialog
import os.path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis import processing
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,QgsRasterLayer,
    QgsPathResolver
)
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QCheckBox, QListView, QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QCheckBox
from qgis import processing
class ImageMosaic:
    """QGIS Plugin Implementation."""

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
            'ImageMosaic_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Image Mosaic')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ImageMosaic', message)


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
            self.action = QAction(QIcon(icon_path),"Image Mosaic", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"Image Mosaic", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        # will be set False in run()
        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Image Mosaic'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):        
        if self.first_start == True:
            self.first_start = False
            self.dlg = ImageMosaicDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        def select():
            self.filename, _filter = QFileDialog.getOpenFileNames(self.dlg, "Select   input file ","", '*.tif *.shp *.jp2')
            self.dlg.label_title_selectfilename.setWordWrap(True)
            self.dlg.label_title_selectfilename.setText(str(self.filename))

        self.dlg.pushButton_select.clicked.connect(select)
        #                #'DATA_TYPE':5,

        def mosaic():
            dataset = gdal.Open(self.filename[0])
            dic = {"6":"Float32","7":"Float64","1":"Byte","3":"Int16","5":"Int32","2":"UInt16","4":"UInt32","8":"CInt16","9":"CInt32","10":"CFloat32","11":"CFloat64"}
            dic1 = {"5":"Float32","6":"Float64","0":"Byte","1":"Int16","4":"Int32","2":"UInt16","3":"UInt32","7":"CInt16","8":"CInt32","9":"CFloat32","10":"CFloat64"}

            band = dataset.GetRasterBand(1)

            x = band.DataType
            print(x)
            print(dic[str(x)])
            type1 = dic[str(x)]
            key1 = list(dic1.keys())[list(dic1.values()).index(type1)]
            print(key1)
            print(self.filename)
            op = plugin_dir+'/imageMosaic.tif'
            if os.path.exists(op):
                os.remove(op)
            processing.run("gdal:merge", 
                {
                'INPUT':self.filename,
                'PCT':False,
                'SEPARATE':False,
                'NODATA_INPUT':None,
                'NODATA_OUTPUT':None,
                'OPTIONS':'',
                'EXTRA':'',
                'DATA_TYPE':key1,
                'OUTPUT':op
                })

            rlayer = QgsRasterLayer(op, "imageMosaic")
            QgsProject.instance().addMapLayer(rlayer)
        self.dlg.pushButton.clicked.connect(mosaic)
        print("success::")

            
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
