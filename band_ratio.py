# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .band_ratio_dialog import BandRatioDialog
import os.path
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,QgsRasterLayer,
    QgsPathResolver
)
#from qgis import processing
#import processing
from qgis.core import *
#from processing.core.Processing import Processing
#
from qgis import processing
#import processing
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QCheckBox, QListView, QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QCheckBox
import shutil
class BandRatio:
    checkbox = ''
    selectedBandImg = []
    cellindex = []
    imgIndex = []
    cellSize =[]
    imgname = []
    iii = 0
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
            'BandRatio_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Band Ratio')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
       
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('BandRatio', message)


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
            self.action = QAction(QIcon(icon_path),"BandRatio", self.iface.mainWindow())
            self.action.setObjectName( 'BandRatio' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"BandRatio", self.iface.mainWindow())
            self.action.setObjectName( 'BandRatio' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "BandRatio":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
       
        if self.first_start == True:
            self.first_start = False
            self.dlg = BandRatioDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        directory1 =plugin_dir +"/layerstack"

        if (self.iii == 0):
            for root, dirs, files in os.walk(directory1):
                for file in files:
                    os.remove(os.path.join(root, file))
            for root, dirs, files in os.walk(plugin_dir+"/resample"):
                for file in files:
                    os.remove(os.path.join(root, file))

            # if not os.path.exists(directory1):
            #     os.mkdir(directory1)
            # shutil.rmtree(directory1)
            # os.mkdir(directory1)

            # os.mkdir(directory1+"/resample")
            # shutil.rmtree(directory1+"/resample")
            # os.mkdir(directory1+"/resample")
            self.iii = 1

        def select():
            self.filename, _filter = QFileDialog.getOpenFileNames(self.dlg, "Select   input file ","", '*.tif *.jp2')
            self.dlg.label_2.show()

            def checkState(chb):
                chb1 = chb.sender()
                    
                if chb1.isChecked():
                    selectItem = chb1.text()
                    self.selectedBandImg.append(selectItem)

                self.dlg.textEdit.show()  
                self.dlg.textEdit.setPlainText(str(self.selectedBandImg)+"\n")
                self.dlg.pushButton_select_2.show()

            
            for i in self.filename:
                n = i.split("/")
                lnameis = n[-1]
                lnameis = os.path.splitext(lnameis)[0]

                #print("layer name : ",n[-1])
                self.imgname.append(lnameis)

                rlayer = QgsRasterLayer(i, str(lnameis))
                QgsProject.instance().addMapLayer(rlayer)

                #get cell size
                pixelSizeX = rlayer.rasterUnitsPerPixelX()
                pixelSizeY = rlayer.rasterUnitsPerPixelY()

                self.cellSize.append(pixelSizeX)
                
                #create checkbox button
                self.checkbox=QCheckBox(str(lnameis))
                self.checkbox.toggled.connect(lambda:checkState(self.checkbox))

                self.dlg.verticalLayout.addWidget(self.checkbox)


        self.dlg.pushButton_select.clicked.connect(select)

        def resambling():
            #layername formating
            nametif = [i+1 for i in range(20)]
            xx = iter(nametif)
            endnametif = next(xx)

            for i in self.selectedBandImg:
                x = self.imgname.index(i)
                self.imgIndex.append(x)
                y = self.cellSize[x]
                self.cellindex.append(y)
                
            ##multiple pair selected then 

            imgSize = {self.imgname[i]: self.cellSize[i] for i in range(len(self.imgname))}

            print(imgSize)
            selectedBandmerge = list(zip(self.selectedBandImg[::2], self.selectedBandImg[1::2]))
            print("selectedBandImg",self.selectedBandImg)
            for i in selectedBandmerge:
                pair = list(i)
                print(list(i))

                iname = pair[0]
                size = imgSize[pair[0]]
                print("size first raster:",size)

                iname1 = pair[1]
                size1 = imgSize[pair[1]]    
                print("size second raster:",size1)

                endnametif = next(xx)
                if size == size1:
                    

                    print("find band ratio=======================")
                    exp = '('+'"'+iname+'@1"'+')*100/('+'"'+iname1+'@1"'+')'
                    print(exp)

                    dir = os.path.dirname(self.filename[0])
                    path11 = self.filename[0]
                    extension = path11[-4:]
                    lyr = dir +"/"+ iname + extension
                    print(lyr)

                    op = plugin_dir+'/layerstack/'+'band_ratio%s.tif'%(endnametif)
                    
                    processing.run("qgis:rastercalculator", 
                                   {'EXPRESSION':exp,
                                   'LAYERS':[lyr],
                                   'CELLSIZE':0,
                                   'EXTENT':None,
                                   'CRS':None,
                                   'OUTPUT':op})
                                    #x1 = '/layerstack/'+'band_ratio%s.tif'%(y)

                    rlayer = QgsRasterLayer(op, "Raster_Band_ratio%s"%(endnametif))
                    QgsProject.instance().addMapLayer(rlayer)
                else:
                    pair = list(i)
                    print("resampling  ::==============")
                    print()
                    print(pair)

                    iname = pair[0]
                    size = imgSize[pair[0]]
                    print(iname)
                    print("size 1:",size)

                    iname1 = pair[1]
                    size1 = imgSize[pair[1]]   
                    print(iname1)
            
                    print("size 2:",size1)

                    max1 = max(size, size1)
                    min1 = min(size, size1)
                    
                    print("maximum",max1)
                    print("minimum",min1)
                    
                    print("image size",imgSize[iname])
                    
                    if (imgSize[iname] ==min1):
                        x = iname
                        print("resampling",x)

                        indx = self.imgname.index(x)
                        res = self.filename[indx]
                        print("resample image : ", res)

                        bandratioConstant = iname1
                        print("band ratio parameter layer",bandratioConstant)
                        
                        ##calulator
                        y = iname1
                        indx1 = self.imgname.index(y)
                        lyr1 = self.filename[indx1]
                        print("band ratio parameter", lyr1)
                        
                        
                    elif (imgSize[iname1] ==min1):
                        x = iname1
                        print("resampling",x)


                        indx = self.imgname.index(x)
                        res = self.filename[indx]
                        print("resample image : ", res)
                        bandratioConstant = iname
                        print("band ratio parameter layer",bandratioConstant)
                        
                        ##calulator
                        y = iname
                        indx1 = self.imgname.index(y)
                        lyr1 = self.filename[indx1]
                        print("band ratio parameter", lyr1)
                        
                    
                    op = plugin_dir+'/resample/'+'Resampling_image%s.tif'%(endnametif)
                    print(res)
                    print(max1)
                    print(op)

                    processing.run("gdal:warpreproject", 
                                   {'INPUT':res,
                                   'SOURCE_CRS':None,
                                   'TARGET_CRS':None,
                                   'RESAMPLING':0,
                                   'NODATA':None,
                                   'TARGET_RESOLUTION':max1,
                                   'OPTIONS':'',
                                   'DATA_TYPE':0,
                                   'TARGET_EXTENT':None,
                                   'TARGET_EXTENT_CRS':None,
                                   'MULTITHREADING':False,
                                   'EXTRA':'',
                                   'OUTPUT':op})
                    rlayer = QgsRasterLayer(op, 'Resampling_image%s.tif'%(endnametif))
                    QgsProject.instance().addMapLayer(rlayer)
                    

                    op = "Resampling_image%s"%(endnametif)
                    
                    ###Find the band ratio image

                    exp = '('+'"'+op+'@1'+'"'+')'+'*100/('+'"'+bandratioConstant+'@1"'+')'
                    print(exp)
                    print(lyr1)
                    # indx = self.cellSize.index(max1)
                    # lyr = self.filename[indx]
                    # print(lyr)

                    op = plugin_dir+'/layerstack/'+'band_ratio%s.tif'%(endnametif)

                    processing.run("qgis:rastercalculator", 
                                   {'EXPRESSION':exp,
                                   'LAYERS':[lyr1],
                                   'CELLSIZE':0,
                                   'EXTENT':None,
                                   'CRS':None,
                                   'OUTPUT':op})
                   
                    rlayer = QgsRasterLayer(op, 'band_ratio%s.tif'%(endnametif))
                    QgsProject.instance().addMapLayer(rlayer)

                self.dlg.pushButton_select_3.show()

            
        self.dlg.pushButton_select_2.clicked.connect(resambling)
        self.dlg.pushButton_select_2.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_select_2.setToolTip('click')

        def layerstack():
            directory = plugin_dir+'/layerstack'
            lyr = []
            for dirpath,_,filenames in os.walk(directory):
                for f in filenames:
                    lyr.append(os.path.abspath(os.path.join(dirpath, f)))
            print("merge layer : ",lyr)

            processing.run("gdal:merge", {
                'INPUT':lyr,
                'PCT':False,
                'SEPARATE':True,
                'NODATA_INPUT':None,
                'NODATA_OUTPUT':None,
                'OPTIONS':'',
                'EXTRA':'',
                'OUTPUT':plugin_dir+'/RastrRatioLayerStack.tif'})

            rlayer = QgsRasterLayer(plugin_dir+'/RastrRatioLayerStack.tif', "Raster Ratio LayerStack ")
            QgsProject.instance().addMapLayer(rlayer)
            
        self.dlg.pushButton_select_3.clicked.connect(layerstack)
        self.dlg.pushButton_select_3.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_select_3.setToolTip('click')

        self.dlg.textEdit.hide()
        self.dlg.pushButton_select_2.hide()
        self.dlg.pushButton_select_3.hide()
        self.dlg.label_2.hide()

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
