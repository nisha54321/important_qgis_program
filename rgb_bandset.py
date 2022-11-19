# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .rgb_bandset_dialog import RgbBandsetDialog
import os.path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis import processing
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,QgsRasterLayer,
    QgsPathResolver
)
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QCheckBox, QListView, QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QCheckBox


class RgbBandset:
    """QGIS Plugin Implementation."""
    filename = ''
    rlayer = ''
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
            'RgbBandset_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Rgb Bandset')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RgbBandset', message)


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
            self.action = QAction(QIcon(icon_path),"RgbBandset", self.iface.mainWindow())
            self.action.setObjectName( 'RgbBandset' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"RgbBandset", self.iface.mainWindow())
            self.action.setObjectName( 'RgbBandset' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "RgbBandset":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)

    def run(self):
    
        if self.first_start == True:
            self.first_start = False
            self.dlg = RgbBandsetDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        def select():
            self.filename, _filter = QFileDialog.getOpenFileName(self.dlg, "Select   input file ","", '*.tif *.shp *jp2')
            self.dlg.label_title_selectfilename.setWordWrap(True)
            self.dlg.label_title_selectfilename.setText(str(self.filename))

            print(self.filename)
            self.rlayer = QgsRasterLayer(self.filename, "multiband image")
            QgsProject.instance().addMapLayer(self.rlayer)

            total_band = self.rlayer.bandCount()

            banditems =[]
            for i in range(total_band):
                item = "Band "+str(i+1)
                banditems.append(item)
            
            self.dlg.comboBox_r.addItems(banditems)
            self.dlg.comboBox_g.addItems(banditems)
            self.dlg.comboBox_b.addItems(banditems)

        self.dlg.pushButton_select.clicked.connect(select)

        def rgbBand():
            r = self.dlg.comboBox_r.currentIndex()
            g = self.dlg.comboBox_g.currentIndex()
            b = self.dlg.comboBox_b.currentIndex()

            #lyr = self.iface.activeLayer() #An multiband (8 band) raster 

            self.rlayer.renderer().setRedBand(r+1)
            self.rlayer.renderer().setGreenBand(g+1)
            self.rlayer.renderer().setBlueBand(b+1)

            self.rlayer.triggerRepaint()
        self.dlg.pushButton.clicked.connect(rgbBand)

        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
