# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .pca_raster_dialog import PcaRasterDialog
import os.path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QFileInfo
from osgeo import gdal
from osgeo.gdalconst import *
import numpy
from qgis.core import QgsRasterLayer, QgsProject
from qgis import processing
#<module 'pca_raster.core.config' from '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/pca_raster/core/config.py'>
	
class PcaRaster:
    """QGIS Plugin Implementation."""
    filename = ''
    save = ''
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
            'PcaRaster_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Pca Raster')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PcaRaster', message)


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
            self.action = QAction(QIcon(icon_path),"PcaRaster", self.iface.mainWindow())
            self.action.setObjectName( 'PcaRaster' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"PcaRaster", self.iface.mainWindow())
            self.action.setObjectName( 'PcaRaster' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "PcaRaster":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)




    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = PcaRasterDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        def select():
            self.filename, _filter = QFileDialog.getOpenFileName(self.dlg, "Select   input file ","", '*.tif *.jp2')
            self.dlg.label_title_selectfilename.setWordWrap(True)
            self.dlg.label_title_selectfilename.setText(str(self.filename))

        self.dlg.pushButton_select.clicked.connect(select)

        def savematrix():
            self.save, _filter = QFileDialog.getSaveFileName(self.dlg, 'Save File')
            print(self.save)

        self.dlg.pushButton_select_2.clicked.connect(savematrix)
        
        ##############################=============================pca algorithm

        def pca(inputRasterFileName, outputRasterFileName, outPCBands):
            ob = open(self.save,"w")
            # Open the input raster file
            # register the gdal drivers
            gdal.AllRegister()

            # Open and assign the contents of the raster file to a dataset
            dataset = gdal.Open(inputRasterFileName, GA_ReadOnly)

            # Compute raster correlation matrix    
            bandMean = numpy.empty(dataset.RasterCount)
            for i in range(dataset.RasterCount):
                band = dataset.GetRasterBand(i+1).ReadAsArray(0, 0,
                                                            dataset.RasterXSize,
                                                            dataset.RasterYSize)
                bandMean[i] = numpy.amin(band, axis = None)

            corrMatrix = numpy.empty((dataset.RasterCount, dataset.RasterCount))
            for i in range(dataset.RasterCount):
                band = dataset.GetRasterBand(i+1)
                bandArray = band.ReadAsArray(0, 0,
                                            dataset.RasterXSize,
                                            dataset.RasterYSize).astype(numpy.float).flatten()

                bandArray = bandArray - bandMean[i]
                corrMatrix[i][i] = numpy.corrcoef(bandArray, bandArray)[0][1]

            band = None
            bandArray = None

            for i in range(1, dataset.RasterCount + 1):
                band1 = dataset.GetRasterBand(i)
                bandArray1 = band1.ReadAsArray(0, 0,
                                            dataset.RasterXSize,
                                            dataset.RasterYSize).astype(numpy.float).flatten()
                bandArray1 = bandArray1 - bandMean[i - 1]

                for j in range(i + 1, dataset.RasterCount + 1):
                    band2 = dataset.GetRasterBand(j)
                    bandArray2 = band2.ReadAsArray(0, 0,
                                                dataset.RasterXSize,
                                                dataset.RasterYSize).astype(numpy.float).flatten()

                    bandArray2 = bandArray2 - bandMean[j - 1]

                    corrMatrix[j - 1][i - 1] = corrMatrix[i - 1][j - 1] = numpy.corrcoef(bandArray1, bandArray2)[0][1]

            # Calculate the eigenvalues and the eigenvectors of the covariance
            # matrix and calculate the principal components
            ob.write('corrMatrix=========================================')
            ob.write("\n")

            ob.write(str(corrMatrix))
            ob.write("\n")
            #print(corrMatrix)
            eigenvals, eigenvectors = numpy.linalg.eig(corrMatrix)

            # Just for testing
            #print (eigenvals)
            #print (eigenvectors)

            ob.write('eigenvals===================================')
            ob.write("\n")

            ob.write(str(eigenvals))
            ob.write("\n")
            
            ob.write('eigenvectors====================================')
            ob.write("\n")

            ob.write(str(eigenvectors))
            ob.write("\n")
            # Create a lookup table and sort it according to
            # the index of the eigenvalues table
            # In essence the following code sorts the eigenvals
            indexLookupTable = [i for i in range(dataset.RasterCount)]

            for i in range(dataset.RasterCount):
                for j in range(dataset.RasterCount - 1, i, -1):
                    if eigenvals[indexLookupTable[j]] > eigenvals[indexLookupTable[j - 1]]:
                        temp = indexLookupTable[j]
                        indexLookupTable[j] = indexLookupTable[j - 1]
                        indexLookupTable[j - 1] = temp

            # Calculate and save the resulting dataset
            driver = gdal.GetDriverByName("GTiff")
            outDataset = driver.Create(outputRasterFileName,
                                    dataset.RasterXSize,
                                    dataset.RasterYSize,
                                    outPCBands,
                                    gdal.GDT_Float32)

            for i in range(outPCBands):
                pc = 0
                for j in range(dataset.RasterCount):
                    band = dataset.GetRasterBand(j + 1)
                    bandAdjustArray = band.ReadAsArray(0, 0, dataset.RasterXSize,
                                                    dataset.RasterYSize).astype(numpy.float) - bandMean[j]

                    pc = pc + eigenvectors[j, indexLookupTable[i]] * bandAdjustArray

                pcband = outDataset.GetRasterBand(i + 1)
                pcband.WriteArray(pc)

            # Check if there is geotransformation or geoprojection
            # in the input raster and set them in the resulting dataset
            if dataset.GetGeoTransform() != None:
                outDataset.SetGeoTransform(dataset.GetGeoTransform())

            if dataset.GetProjection() != None:
                outDataset.SetProjection(dataset.GetProjection())


            # write the statistics of the PCA into a file
            # first organize the statistics into lists
            corrBandBand = [['' for i in range(dataset.RasterCount + 1)] for j in range(dataset.RasterCount + 1)]
            corrBandBand[0][0] = "Correlation Matrix"
            for j in range(1, 1 + dataset.RasterCount):
                header = 'Band' + str(j)
                corrBandBand[0][j] = header
            for i in range(1, 1 + dataset.RasterCount):
                vertical = 'Band' + str(i)
                corrBandBand[i][0] = vertical
            for i in range(1, 1 + dataset.RasterCount):
                for j in range(1, 1 + dataset.RasterCount):
                    corrBandBand[i][j] = "%.3f" % corrMatrix[i - 1, j - 1]

            covBandPC = [['' for i in range(dataset.RasterCount + 1)] for j in range(dataset.RasterCount + 1)]
            covBandPC[0][0] = "Cov.Eigenvectors"
            for j in range(1, 1 + dataset.RasterCount):
                header = 'PC' + str(j)
                covBandPC[0][j] = header
            for i in range(1, 1 + dataset.RasterCount):
                vertical = "Band" + str(i)
                covBandPC[i][0] = vertical
            for i in range(1, 1 + dataset.RasterCount):
                for j in range(1, 1 + dataset.RasterCount):
                    covBandPC[i][j] = "%.3f" % eigenvectors[i - 1, indexLookupTable[j - 1]]


            covEigenvalMat = [['' for i in range(dataset.RasterCount + 1)] for j in range(5)]
            covEigenvalMat[0][0] = "Bands"
            covEigenvalMat[1][0] = "Cov.Eigenvalues"
            covEigenvalMat[2][0] = "Sum of Eigenvalues"
            covEigenvalMat[3][0] = "Eigenvalues/Sum"
            covEigenvalMat[4][0] = "Percentages(%)"

            eigvalSum = 0.0
            sum = numpy.sum(eigenvals)
            for i in range(dataset.RasterCount):
                covEigenvalMat[0][i + 1] = "PC" + str(i + 1)
                covEigenvalMat[1][i + 1] = "%.3f" % eigenvals[indexLookupTable[i]]
                eigvalSum = eigvalSum + eigenvals[indexLookupTable[i]]
                covEigenvalMat[2][i + 1] = "%.3f" % eigvalSum
                covEigenvalMat[3][i + 1] = "%.3f" % (eigvalSum / sum)
                covEigenvalMat[4][i + 1] = "%.1f" % (eigvalSum / sum * 100.0)

            # Debug printout
            #print (corrBandBand)
            #print (covBandPC)
            #print (covEigenvalMat)


            ob.write('corrBandBand===========================================')
            ob.write("\n")

            ob.write(str(corrBandBand))
            ob.write("\n")
            
            ob.write('covBandPC===========================================')
            ob.write("\n")

            ob.write(str(covBandPC))
            ob.write("\n")
            
            ob.write('strcovEigenvalMat====================================')
            ob.write("\n")

            ob.write(str(covEigenvalMat))
            ob.write("\n")

            ob.write("\n PCA STATISTICS VALUE=============================")
            ob.write("\n")

            statText = ""
            statFileName = plugin_dir + "/pca_statistics.txt"
            statFile = open(statFileName, "w")

            for i in range(len(corrBandBand)):
                for j in range(len(corrBandBand)): # symmetrical matrix
                    statText = statText + corrBandBand[i][j]
                    if (j < len(corrBandBand[0]) - 1):
                        statText = statText + " "
                statText = statText + "\n"

            statText = statText + "\n"

            for i in range(len(covBandPC)):
                for j in range(len(covBandPC[0])):
                    statText = statText + covBandPC[i][j]
                    if (j < len(covBandPC[0]) - 1):
                        statText = statText + " "
                statText = statText + "\n"

            statText = statText + "\n"

            for i in range(len(covEigenvalMat)):
                for j in range(len(covEigenvalMat[0])):
                    statText = statText + covEigenvalMat[i][j]
                    if (j < len(covEigenvalMat[0]) - 1):
                        statText = statText + " "
                statText = statText + "\n"

            ob.write(statText)
            ob.close()
            dataset = None
            outDataset = None

            # insert the output raster into QGIS interface
            outputRasterFileInfo = QFileInfo(outputRasterFileName)
            baseName = outputRasterFileInfo.baseName()
            rasterLayer = QgsRasterLayer(outputRasterFileName, baseName)
            if not rasterLayer.isValid():
                print("Layer failed to load")
            QgsProject.instance().addMapLayer(rasterLayer)
            
            #ob.close()
        outputRasterFileName = plugin_dir+"/PCA_Raster.tif"

        def pcafind():
            component = int(self.dlg.lineEdit.text())
            print(component)
            print(self.filename)

            ##call pca function
            pca(self.filename, outputRasterFileName, component)

            rlayer = QgsRasterLayer(outputRasterFileName, "PCA_Raster")

            total_band = rlayer.bandCount()

            print(total_band)

            ##rearrang or split band 
            bands = [str(i+1) for i in range(total_band)]
            print(bands)

            for split in bands:
                print([split])
                op = plugin_dir+'/Band_{}_Pca.tif'.format(split)
                print(op)
                processing.run("gdal:rearrange_bands", 
                    {'INPUT':outputRasterFileName,
                    'BANDS':[split],
                    'OPTIONS':'',
                    'DATA_TYPE':0,
                    'OUTPUT':op})
                
                rlayer = QgsRasterLayer(op, "Pca_{}".format(split))
                QgsProject.instance().addMapLayer(rlayer)

        self.dlg.pushButton.clicked.connect(pcafind)  
        self.dlg.pushButton.setStyleSheet("color: blue;font-size: 12pt; ") 
        self.dlg.label_title.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton.setToolTip('click')

        self.dlg.show()

        result = self.dlg.exec_()

        if result:
            pass
    
