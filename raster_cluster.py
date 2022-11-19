# - *- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
import os.path
from PyQt5.QtCore import *

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .raster_cluster_dialog import RasterClusterDialog
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
import numpy as np
from sklearn import cluster
from osgeo import gdal, gdal_array
import matplotlib.pyplot as plt

class RasterCluster:
    filename = ''

    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RasterCluster_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&RasterCluster')

      
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('RasterCluster', message)


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
            self.action = QAction(QIcon(icon_path),"RasterCluster", self.iface.mainWindow())
            self.action.setObjectName( 'RasterCluster' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"RasterCluster", self.iface.mainWindow())
            self.action.setObjectName( 'RasterCluster' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "RasterCluster":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)



    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = RasterClusterDialog()
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

        self.dlg.pushButton_2.clicked.connect(select)

        def cluster1():
            # component = self.dlg.lineEdit.text()
            # print(component," :",self.filename)
            # gdal.UseExceptions()
            # gdal.AllRegister()

            # raster = self.filename
            # img_ds = gdal.Open(raster, gdal.GA_ReadOnly)

            # img = np.zeros((img_ds.RasterYSize, img_ds.RasterXSize, img_ds.RasterCount),
            #             gdal_array.GDALTypeCodeToNumericTypeCode(img_ds.GetRasterBand(1).DataType))

            # for b in range(img.shape[2]):
            #     img[:, :, b] = img_ds.GetRasterBand(b + 1).ReadAsArray()

            # new_shape = (img.shape[0] * img.shape[1], img.shape[2])

            # X = img[:, :, :img_ds.RasterCount].reshape(new_shape)

            # # k_means = cluster.KMeans(n_clusters=8)###MiniBatchKMeans
            # n = int(component)
            # MB_KMeans = cluster.KMeans(n_clusters=n)
            # MB_KMeans.fit(X)

            # X_cluster = MB_KMeans.labels_

            # X_cluster = X_cluster.reshape(img[:, :, 0].shape)

            # ##save image into disk

            # ds = gdal.Open(raster)
            # band = ds.GetRasterBand(1)
            # arr = band.ReadAsArray()
            # [cols, rows] = arr.shape

            # driver = gdal.GetDriverByName("GTiff")

            # op = plugin_dir+"/kmeanL_S.tif"
            # if os.path.exists(op):
            #     os.remove(op)

            # outDataRaster = driver.Create(op, rows, cols, 1, gdal.GDT_Byte)
            # outDataRaster.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
            # outDataRaster.SetProjection(ds.GetProjection())##sets same projection as input

            # outDataRaster.GetRasterBand(1).WriteArray(X_cluster)

            # outDataRaster.FlushCache() ## remove from memory
            # del outDataRaster ## delete the data (not the actual geotiff)
            # print("save::")

            # rlayer = QgsRasterLayer(op, "Clustering")
            # QgsProject.instance().addMapLayer(rlayer)

            #saga algorithm (kmean clustering with grid)

            component = self.dlg.lineEdit.text()
            print(component," :",self.filename)

            op = plugin_dir+'/kmean.sdat'

            if os.path.exists(op):
                os.remove(op)

            from qgis import processing
            processing.run("saga:kmeansclusteringforgrids",
                {'GRIDS':[self.filename],
                'METHOD':1,
                'NCLUSTER':str(component),
                'MAXITER':0,
                'NORMALISE':False,
                'OLDVERSION':False,
                'UPDATEVIEW':True,
                'CLUSTER':op,
                'STATISTICS':plugin_dir+'/static.shp'})

            rlayer = QgsRasterLayer(op, "Clustering image")
            QgsProject.instance().addMapLayer(rlayer)

        self.dlg.pushButton.clicked.connect(cluster1)

        self.dlg.pushButton.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton.setToolTip('click')
        
        self.dlg.label.setStyleSheet("color: brown;font-size: 12pt; ") 
        self.dlg.label_2.setStyleSheet("color: blue;font-size: 12pt; ") 

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
