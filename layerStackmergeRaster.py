# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5 import QtWidgets, QtGui

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .vector_layer_dialog import VectorlayerDialog
import os.path
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
#from qgis import processing
from qgis.core import *
#from processing.core.Processing import Processing
#
#from qgis import processing
import processing
from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsPointXY,
    QgsRaster,
    QgsRasterShader,
    QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer,
    QgsSingleBandColorDataRenderer,
    QgsSingleBandGrayRenderer,
)

class Vectorlayer:
    """QGIS Plugin Implementation."""
    iii = 0
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
            'Vectorlayer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&merge Raster')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
       
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Vectorlayer', message)


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
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        plugin_dir = os.path.dirname(__file__)
        icon_path = plugin_dir+'/'+'bisag_n.png'
        #icon_path = ':/plugins/vector_layer/icon.png'

        # self.add_action(
        #     icon_path,
        #     text=self.tr(u'vector data'),
        #     callback=self.run,
        #     parent=self.iface.mainWindow())

        self.menu = self.iface.mainWindow().findChild( QMenu, '&Algorithm' )

        if not self.menu:
            self.menu = QMenu( '&Algorithm', self.iface.mainWindow().menuBar() )
            self.menu.setObjectName( '&Algorithm' )
            actions = self.iface.mainWindow().menuBar().actions()
            lastAction = actions[-1]
            self.iface.mainWindow().menuBar().insertMenu( lastAction, self.menu )
            self.action = QAction(QIcon(icon_path),"layer stack", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"layer stack", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        # if(self.iii == 0):
        #     self.action = QAction(QIcon(icon_path),"merge Raster", self.iface.mainWindow())
        #     self.iii = 1

        # self.action.triggered.connect(self.run)
        # self.menu.addAction(self.action)


        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&merge Raster'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
       
        if self.first_start == True:
            self.first_start = False
            self.dlg = VectorlayerDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        def select():
            self.filename, _filter = QFileDialog.getOpenFileNames(self.dlg, "Select   input file ","", '*.tif *.shp *jp2')
            self.dlg.label_title_selectfilename.setWordWrap(True)
            self.dlg.label_title_selectfilename.setText(str(self.filename))

        self.dlg.pushButton_select.clicked.connect(select)

        def mergeImage():
            print(self.filename)
            processing.run("gdal:merge", {
                'INPUT':self.filename,
                'PCT':False,
                'SEPARATE':True,
                'NODATA_INPUT':None,
                'NODATA_OUTPUT':None,
                'OPTIONS':'',
                'EXTRA':'',
                'OUTPUT':plugin_dir+'/layerStack.tif'})

            rlayer = QgsRasterLayer(plugin_dir+'/layerStack.tif', "layer Stack")
            QgsProject.instance().addMapLayer(rlayer)


        self.dlg.pushButton_merge.clicked.connect(mergeImage)  
        self.dlg.pushButton_merge.setStyleSheet("color: blue;font-size: 12pt; ") 
        self.dlg.label_title.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_merge.setToolTip('click')
        
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
