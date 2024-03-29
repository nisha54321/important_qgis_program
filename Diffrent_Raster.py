# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DiffrentRaster
                                 A QGIS plugin
 Diffrent between Raster
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-04-22
        git sha              : $Format:%H$
        copyright            : (C) 2021 by bisag-n
        email                : bisag.co.in
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject, QgsRasterLayer, QgsPointXY, QgsRaster
from qgis.gui import QgsMapToolEmitPoint

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Diffrent_Raster_dialog import DiffrentRasterDialog
import os.path
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog


class DiffrentRaster:
    """QGIS Plugin Implementation."""
    x = 0.0
    y = 0.0
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
            'DiffrentRaster_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Diffrent Raster')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DiffrentRaster', message)


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
            self.action = QAction(QIcon(icon_path),"DiffrentRaster", self.iface.mainWindow())
            self.action.setObjectName( 'DiffrentRaster' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"DiffrentRaster", self.iface.mainWindow())
            self.action.setObjectName( 'DiffrentRaster' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "DiffrentRaster":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = DiffrentRasterDialog()

        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            print(coorx,coory)
            self.x = coorx
            self.y = coory

        # a reference to our map canvas 
        canvas = self.iface.mapCanvas() 
        pointTool = QgsMapToolEmitPoint(canvas)

        pointTool.canvasClicked.connect( display_point )

        canvas.setMapTool( pointTool )

        layers = QgsProject.instance().layerTreeRoot().children()

        self.dlg.comboBox_1.addItems([layer.name() for layer in layers])
        self.dlg.comboBox_2.addItems([layer.name() for layer in layers])

        selectedLayerIndex = self.dlg.comboBox_1.currentIndex()
        print(selectedLayerIndex)
        selectedLayer = layers[selectedLayerIndex]
        print(selectedLayer)
        

        # d = {x: r1[x] - r2[x] for x in r1 if x in r2}
        # print("diffrent is: ",d)
        def diffrent1():
            p = QgsPointXY(self.x,self.y)
        
            rasterLyr = QgsRasterLayer("/home/bisag/Documents/1DEM/asterDem.tif","Sat Image")
            qry = rasterLyr.dataProvider().identify(p,QgsRaster.IdentifyFormatValue)
            qry.isValid()
            r2 = qry.results()
            print(r2)

            rasterLyr1 = QgsRasterLayer("/home/bisag/Documents/NE1_HR_LC/NE1_HR_LC_REPROJECTION.tif","Sat tiff")
            rasterLyr1.isValid()
            qry = rasterLyr1.dataProvider().identify(p,QgsRaster.IdentifyFormatValue)
            qry.isValid()
            r1 = qry.results()

            print(r1)
            d = {x: r1[x] - r2[x] for x in r1 if x in r2}
            print("diffrent is: ",d)
            op = str(d[1])
            self.dlg.textEdit_op.setText(op)

        self.dlg.pushButton_diff.clicked.connect(diffrent1)

        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
