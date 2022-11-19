# -*- coding: utf-8 -*-
##layer stack plugin
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5 import QtWidgets, QtGui

from .resources import *
from .vector_layer_dialog import VectorlayerDialog
import os.path
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis import processing

from qgis.core import (
    QgsRasterLayer,QgsVectorFileWriter,QgsRasterFileWriter,
    QgsProject,
    QgsPointXY,
    QgsRaster,
    QgsRasterShader,
    QgsColorRampShader,QgsRasterPipe,
    QgsSingleBandPseudoColorRenderer,
    QgsSingleBandColorDataRenderer,
    QgsSingleBandGrayRenderer,
)

class Vectorlayer:
    iii = 0
    filename = ''
    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Vectorlayer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&merge Raster')

        self.first_start = None

    def tr(self, message):
       
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
            self.action = QAction(QIcon(icon_path),"Vectorlayer", self.iface.mainWindow())
            self.action.setObjectName( 'Vectorlayer' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"Vectorlayer", self.iface.mainWindow())
            self.action.setObjectName( 'Vectorlayer' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "Vectorlayer":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


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

        op = plugin_dir+'/layerStack.tif'
        if os.path.exists(op):
            os.remove(op)

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
                'OUTPUT':op})

            rlayer = QgsRasterLayer(plugin_dir+'/layerStack.tif', "layerStack")
            QgsProject.instance().addMapLayer(rlayer)

            if os.path.exists("/home/bisag/Documents/demo_plugins/layerStack.tif"):
                os.remove("/home/bisag/Documents/demo_plugins/layerStack.tif")

            file_name = '/home/bisag/Documents/demo_plugins/' + rlayer.name() + '.tif'
            file_writer = QgsRasterFileWriter(file_name)
            pipe = QgsRasterPipe()
            provider = rlayer.dataProvider()

            if not pipe.set(provider.clone()):
                print("Cannot set pipe provider")
            file_writer.writeRaster(pipe,provider.xSize(),provider.ySize(),provider.extent(),provider.crs())

        self.dlg.pushButton_merge.clicked.connect(mergeImage)  
        self.dlg.pushButton_merge.setStyleSheet("color: blue;font-size: 12pt; ") 
        self.dlg.label_title.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_merge.setToolTip('click')
        
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            
            pass
