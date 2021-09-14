# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .zonal_statistics_dialog import ZonalStatisticsDialog
import os.path
import os.path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
#from qgis import processing
from qgis.core import *
import processing
#
#from qgis import processing
#import processing
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,QgsRasterLayer,QgsVectorLayer,
    QgsPathResolver
)
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QCheckBox, QListView, QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QCheckBox

class ZonalStatistics:
    """QGIS Plugin Implementation."""
    filename = ''
    selectBand = []
    indexItem = []
    filename_v = ''
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
            'ZonalStatistics_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Zonal Statistics')

       
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ZonalStatistics', message)


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

        # icon_path = ':/plugins/zonal_statistics/icon.png'
        # self.add_action(
        #     icon_path,
        #     text=self.tr(u'Zonal Statistics'),
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
            self.action = QAction(QIcon(icon_path),"Zonal statistics", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"Zonal statistics", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        self.first_start = True

        # will be set False in run()
        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Zonal Statistics'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = ZonalStatisticsDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))
        def select():
            self.filename, _filter = QFileDialog.getOpenFileName(self.dlg, "Select   input file ","", '*.tif *jp2')
            self.dlg.label_title_selectfilename.setWordWrap(True)
            self.dlg.label_title_selectfilename.setText(str(self.filename))

            print(self.filename)
            rlayer = QgsRasterLayer(self.filename, "multiband image")
            total_band = rlayer.bandCount()

            print(total_band)
            band1 =["Band "+str(i+1) for i in range(5)]

            print(band1)
            statastic = ["Count","Sum","Mean","Median","St. dev.","Min","Max ","Range","Minority","Majority (mode)","Variety","Variance","All"]
            # index = [0,1,2,3,4,5,6,7,8,9,10,11,12]
            # z = list(zip(index,statastic))

            self.dlg.comboBox.addItems(band1)


            def checkState(chb):
                chb1 = chb.sender()

                if chb1.isChecked():
                    selectItem = chb1.text()
                    index = statastic.index(selectItem)
                    self.indexItem.append(index)
                    self.selectBand.append(selectItem)
                    print(selectItem)
                    print(index)

            banditems =[]
            for item in statastic:
                #create checkbox button
                self.checkbox=QCheckBox(item)
                self.checkbox.toggled.connect(lambda:checkState(self.checkbox))

                self.dlg.verticalLayout.addWidget(self.checkbox)

        def selectbtn():
            self.dlg.label_setband.setWordWrap(True)
            self.dlg.label_setband.setText(str(self.selectBand))

        self.dlg.pushButton_select_2.clicked.connect(selectbtn)

        self.dlg.pushButton_select.clicked.connect(select)

        def selectVector():
            self.filename_v, _filter = QFileDialog.getOpenFileName(self.dlg, "Select   input file ","", '*.shp *gpkg')
            self.dlg.label_title_selectfilename_2.setWordWrap(True)
            self.dlg.label_title_selectfilename_2.setText(str(self.filename_v))
            print(self.filename_v)

        self.dlg.pushButton_select_3.clicked.connect(selectVector)
        def algo():
            print("run :")
            rband = self.dlg.comboBox.currentIndex()+1

            print(rband)
            print(self.indexItem)
            processing.run("qgis:zonalstatistics",
                            {'INPUT_RASTER':self.filename,
                            'RASTER_BAND':rband,
                            'INPUT_VECTOR':self.filename_v,
                            'COLUMN_PREFIX':'zonal_',
                            'STATS':self.indexItem})
            
            vlayer = QgsVectorLayer(self.filename_v, "polygon", "ogr")

            fname = []
            for field in vlayer.fields():
                fname.append(field.name())
            #    print(field.name())
                
            #mylist = iter(fname)
            features = vlayer.getFeatures()
            y = []
            for feature in features:
                for i in range(len(fname)):
                    #print(feature[fname[i]])
                    print(fname[i]," : ",feature[fname[i]])
                    x = str(fname[i])+" : "+str(feature[fname[i]])+"  "
                    x = str(x)
                    x = x.replace("(","").replace(")","")
                    y.append(x)
            self.dlg.textEdit.setPlainText(str(y))


        self.dlg.pushButton_zonal.clicked.connect(algo)

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            
            pass
