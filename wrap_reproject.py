# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .wrap_reproject_dialog import WrapReprojectDialog
import os.path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis import processing
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,QgsRasterLayer,
    QgsPathResolver
)

from PyQt5.QtWidgets import QMenu, QAction,QFileDialog

class WrapReproject:
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
            'WrapReproject_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Resampling Image')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('WrapReproject', message)


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
            self.action = QAction(QIcon(icon_path),"WrapReproject", self.iface.mainWindow())
            self.action.setObjectName( 'WrapReproject' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"WrapReproject", self.iface.mainWindow())
            self.action.setObjectName( 'WrapReproject' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "WrapReproject":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
    
        if self.first_start == True:
            self.first_start = False
            self.dlg = WrapReprojectDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))
                
        def select():
            self.filename, _filter = QFileDialog.getOpenFileName(self.dlg, "opent file ","", '*.tif *.shp *.jp2')
            self.dlg.label_title_selectfilename.setWordWrap(True)
            self.dlg.label_title_selectfilename.setText(self.filename)
            

        self.dlg.pushButton_openFile.clicked.connect(select)

        resampling_metod = [" Nearest neighbour","Bilinear","Cubic","Cubic spline","Lanczos windowed sinc","Average","Mode","Maximum","Minimum","Median","First quartile","Third quartile"]
        alg_method  = self.dlg.comboBox.addItems(resampling_metod)


        def reproject():
            datatype = self.dlg.comboBox.currentIndex()

            print("algo method",datatype)


            resolution = self.dlg.lineEdit_esolution.text()

            print(self.filename,"====        filename")
            print(resolution)

            op = plugin_dir+'/Resampling_image.tif'

            if os.path.exists(op):
                os.remove(op)
                
            processing.run("gdal:warpreproject", 
                            {'INPUT':self.filename,
                            'SOURCE_CRS':None,
                            'TARGET_CRS':None,
                            'RESAMPLING':0,
                            'NODATA':None,
                            'TARGET_RESOLUTION':resolution,
                            'OPTIONS':'',
                            'DATA_TYPE':datatype,
                            'TARGET_EXTENT':None,
                            'TARGET_EXTENT_CRS':None,
                            'MULTITHREADING':False,
                            'EXTRA':'',
                            'OUTPUT':op})

            rlayer = QgsRasterLayer(op, "Resampling Image")
            QgsProject.instance().addMapLayer(rlayer)

        self.dlg.pushButton_reproject.clicked.connect(reproject)  
        self.dlg.pushButton_reproject.setStyleSheet("color: blue;font-size: 12pt; ") 


        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
