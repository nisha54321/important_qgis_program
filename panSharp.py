####low to high resolution
# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .pan_sharp_dialog import PanSharpDialog
import os.path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis import processing
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,QgsRasterLayer,
    QgsPathResolver
)

class PanSharp:
    """QGIS Plugin Implementation."""
    filename = ''
    filename1 = ''
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PanSharp_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Pan Sharp')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PanSharp', message)


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

        # icon_path = ':/plugins/pan_sharp/icon.png'
        # self.add_action(
        #     icon_path,
        #     text=self.tr(u'Pan Sharp'),
        #     callback=self.run,
        #     parent=self.iface.mainWindow())

        plugin_dir = os.path.dirname(__file__)
        icon_path = plugin_dir+'/'+'bisag_n.png'

        # self.menu = self.iface.mainWindow().findChild( QMenu, '&Algorithm' )
        # self.action = QAction(QIcon(icon_path),"Pan Sharp", self.iface.mainWindow())
        # self.action.triggered.connect(self.run)
        # self.menu.addAction(self.action)

        self.menu = self.iface.mainWindow().findChild( QMenu, '&Algorithm' )

        if not self.menu:
            self.menu = QMenu( '&Algorithm', self.iface.mainWindow().menuBar() )
            self.menu.setObjectName( '&Algorithm' )
            actions = self.iface.mainWindow().menuBar().actions()
            lastAction = actions[-1]
            self.iface.mainWindow().menuBar().insertMenu( lastAction, self.menu )
            self.action = QAction(QIcon(icon_path),"pan sharp", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"pan sharp", self.iface.mainWindow())
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)


        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Pan Sharp'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        if self.first_start == True:
            self.first_start = False
            self.dlg = PanSharpDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        def select():
            self.filename, _filter = QFileDialog.getOpenFileName(self.dlg, "Select   input file ","", '*.tif *.shp *jp2')
            self.dlg.label_title_sd.setWordWrap(True)
            self.dlg.label_title_sd.setText(self.filename)

        def select1():
            self.filename1, _filter = QFileDialog.getOpenFileName(self.dlg, "Select   input file ","", '*.tif *.shp *jp2')
            self.dlg.label_title_pd.setWordWrap(True)
            self.dlg.label_title_pd.setText(self.filename1)

        self.dlg.pushButton_s.clicked.connect(select)
        self.dlg.pushButton_p.clicked.connect(select1)

        resampling_metod = [" Nearest neighbour","Bilinear","Cubic","Cubic spline","Lanczos windowed sinc","Average"]
        alg_method  = self.dlg.comboBox.addItems(resampling_metod)

        def algo():
            datatype = self.dlg.comboBox.currentIndex()

            print("algo method",datatype)

            processing.run("gdal:pansharp",
                {'SPECTRAL':self.filename,
                'PANCHROMATIC':self.filename1,
                'RESAMPLING':datatype,
                'OPTIONS':'',
                'EXTRA':'',
                'OUTPUT':plugin_dir+'/pansharp.tif'})

            rlayer = QgsRasterLayer(plugin_dir+'/pansharp.tif', "pansharp Image")
            QgsProject.instance().addMapLayer(rlayer)


        self.dlg.pushButton_run.clicked.connect(algo)

        self.dlg.pushButton_run.setStyleSheet("color: blue;font-size: 12pt; ") 
        self.dlg.pushButton_run.setToolTip('click')

        self.dlg.label_title.setStyleSheet("color: brown;font-size: 12pt; ") 
        self.dlg.label_title_2.setStyleSheet("color: brown;font-size: 12pt; ") 
        self.dlg.label_title_3.setStyleSheet("color: brown;font-size: 12pt; ") 



        


        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass



