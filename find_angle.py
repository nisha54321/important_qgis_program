# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *
from .find_angle_dialog import FindAngleDialog
import os.path
from qgis import processing
from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsPointXY,
    QgsRaster,
    QgsRasterShader,
    QgsColorRampShader,QgsLayerTreeLayer,
    QgsSingleBandPseudoColorRenderer,QgsVectorLayerTemporalProperties,QgsCoordinateReferenceSystem,QgsSvgMarkerSymbolLayer,
    QgsSingleBandColorDataRenderer,
    QgsSingleBandGrayRenderer,QgsVectorLayer, QgsPoint, QgsVectorLayer, QgsFeature, QgsGeometry, QgsVectorFileWriter, QgsField, QgsPalLayerSettings, QgsVectorLayerSimpleLabeling
)
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QCheckBox, QListView, QMessageBox, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtWidgets 
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.gui import QgsMapToolIdentifyFeature, QgsMapToolEmitPoint
from PyQt5 import QtWidgets 
from PyQt5 import QtGui
from qgis.PyQt.QtWidgets import QAction
import re, os.path
from qgis.PyQt.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QWidget, QVBoxLayout, QAction, QLabel, QLineEdit, QMessageBox, QFileDialog, QFrame, QDockWidget, QProgressBar, QProgressDialog, QToolTip
from datetime import timedelta, datetime
import math


class FindAngle:
    iii =0
    xy = []
    vl =''
    v_layer =''
    xy1 = []
    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FindAngle_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Find Angle')

        self.first_start = None

    def tr(self, message):
        
        return QCoreApplication.translate('FindAngle', message)


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
            self.action = QAction(QIcon(icon_path),"FindAngle", self.iface.mainWindow())
            self.action.setObjectName( 'FindAngle' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"FindAngle", self.iface.mainWindow())
            self.action.setObjectName( 'FindAngle' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "FindAngle":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = FindAngleDialog()
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))
        if(self.iii == 0):
            self.vl = QgsVectorLayer("Point?crs=EPSG:4326", "point", "memory")
            self.v_layer = QgsVectorLayer('LineString?crs=epsg:4326', 'line', 'memory')

            # QgsProject.instance().addMapLayer(rlayer)
            self.iii = 1

        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            print(coorx, coory)
            
            self.xy.append(coorx)
            self.xy.append(coory)


            self.vl.renderer().symbol().setSize(3.5)
            self.vl.renderer().symbol().setColor(QColor("green"))
            self.vl.triggerRepaint()

            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx,coory)))
            pr = self.vl.dataProvider()

            pr.addFeature(f)
            self.vl.updateExtents() 
            self.vl.updateFields() 
            QgsProject.instance().addMapLayers([self.vl])
            
            
        canvas = self.iface.mapCanvas()   
        pointTool = QgsMapToolEmitPoint(canvas)

        def clickPoint():
            pointTool.canvasClicked.connect( display_point )
            canvas.setMapTool( pointTool )

        self.dlg.pushButton_select.clicked.connect(clickPoint)

        def angle():
            
            [self.xy1.append(x) for x in self.xy if x not in self.xy1] #remove duplicate

            self.iface.actionPan().trigger()

            start_point = QgsPoint(self.xy1[-4], self.xy1[-3])
            end_point = QgsPoint(self.xy1[-2], self.xy1[-1])
            
            #draw line
            pr = self.v_layer.dataProvider()
            seg = QgsFeature()
            seg.setGeometry(QgsGeometry.fromPolyline([start_point, end_point]))
            pr.addFeatures([ seg ])
            QgsProject.instance().addMapLayers([self.v_layer])

            #azimuth
            a = start_point.azimuth(end_point)
            if a < 0:
                a += 360

            print("Azimuth :",a)
                
            print("COORDINATES:", self.xy1[-3] , self.xy1[-1],self.xy1[-4] , self.xy1[-2])

            ###find angle
            angle = math.atan2( self.xy1[-3]-self.xy1[-1],self.xy1[-4]-self.xy1[-2])#radians

            angle1 =angle*( 180 / math.pi)#degrees
            print("first angle1:",angle1)

            angle2 = 90-abs(angle1)
            print('angle2:',angle2)
            
            angle3 = 90+abs(angle1)
            print('angle3:',abs(angle3))

        
            # mydegrees = math.degrees(angle2)
            #mangle1_rad = math.radians(angle1)

            self.dlg.label_angle.setText("Azimuth :"+str(a)+"\n"+"angle(x)(deg):"+str(round(angle1, 2))+'\n'+"angle(y)(deg):"+str(round(angle2, 2))+'\n'+"angle(y)(deg):"+str(round(angle3, 2)))

            
        self.dlg.pushButton_angle.clicked.connect(angle)
        self.dlg.pushButton_angle.setStyleSheet("color: green;") 
        self.dlg.pushButton_angle.setToolTip('click')

        self.dlg.pushButton_select.setStyleSheet("color: green; ") 
        self.dlg.pushButton_select.setToolTip('click')

        self.dlg.label_angle.setStyleSheet("color: purple; ") 
        self.dlg.label_title.setStyleSheet("color: brown; ") 


        self.dlg.show()
        self.dlg.exec_()
        