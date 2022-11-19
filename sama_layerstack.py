# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5 import QtWidgets, QtGui

from .resources import *
from .sama_layerstack_dialog import SamaLayerstackDialog
import os.path

import sys
#from zipfile import ZipFile
import os, zipfile
import fnmatch
from qgis import processing
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog

class SamaLayerstack:

    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SamaLayerstack_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Sama Layerstack')

       
        self.first_start = None

    def tr(self, message):
        
        return QCoreApplication.translate('SamaLayerstack', message)


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
            self.action = QAction(QIcon(icon_path),"SamaLayerstack", self.iface.mainWindow())
            self.action.setObjectName( 'SamaLayerstack' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"SamaLayerstack", self.iface.mainWindow())
            self.action.setObjectName( 'SamaLayerstack' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "SamaLayerstack":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = SamaLayerstackDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        #######################unzip file
        def unzip():
            dir_name = "/home/bisag/Documents/SAMA/"
            extract = "/home/bisag/Documents/zip1/extract"
            extension = ".zip"

            os.chdir(dir_name) 

            for item in os.listdir(dir_name): 
                if item.endswith(extension): 
                    file_name = os.path.abspath(item)
                    zip_ref = zipfile.ZipFile(file_name)
                    zip_ref.extractall(extract) 
                    zip_ref.close() 
            print("success:")
            
        self.dlg.pushButton_unzip.clicked.connect(unzip) 
        self.dlg.pushButton_merge.setStyleSheet("color: blue;font-size: 12pt; ") 
        self.dlg.pushButton_merge.setToolTip('click')
        self.dlg.label.setStyleSheet("color: brown;font-size: 12pt; ") 

        root1 = "/home/bisag/Documents/zip1/extract/"
        oppath = "/home/bisag/Documents/zip1/samaLayerstack/"

        def layerstack():
            
            matches = []

            for root, dirs, files in os.walk(root1):
                for basename in files:
                    if fnmatch.fnmatch(basename, '*02.jp2') or fnmatch.fnmatch(basename, '*03.jp2') or fnmatch.fnmatch(basename, '*04.jp2') or fnmatch.fnmatch(basename, '*08.jp2') :
                        filename = os.path.join(root, basename)
                        matches.append(filename)
            #print(matches)
            n = 4
            jpfile = [matches[i:i+n] for i in range(0,len(matches),n)]
            #print(jpfile)

            for file1 in jpfile:
                opnm = os.path.basename(file1[0])
                op = opnm[:-8]
                #print(file1)
                
                processing.run("gdal:merge", 
                    {'INPUT':file1,
                        'PCT':False,
                        'SEPARATE':True
                        ,'NODATA_INPUT':None,
                        'NODATA_OUTPUT':None,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'DATA_TYPE':2,
                        'OUTPUT':oppath+opnm[:-8]+'.tif'})
                        
                #print(oppath+opnm[:-8]+'.tif')


            print("success")


        self.dlg.pushButton_merge.clicked.connect(layerstack) 

        self.dlg.pushButton_merge.setStyleSheet("color: blue;font-size: 12pt; ") 

        self.dlg.label_title.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_merge.setToolTip('click')


        self.dlg.show()
        result = self.dlg.exec_()
        