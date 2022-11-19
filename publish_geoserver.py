# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .publish_geoserver_dialog import PublishGeoserverDialog
import os.path

from PyQt5 import QtCore, QtGui, QtWidgets
import os
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from geo.Geoserver import Geoserver
import requests
from qgis.core import (
    QgsVectorLayer,QgsRasterLayer,QgsProject
)

class PublishGeoserver:
    publish_file = ''
    style_file = ''
    def __init__(self, iface):
       
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PublishGeoserver_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Publish Geoserver')

        
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('PublishGeoserver', message)


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
            self.action = QAction(QIcon(icon_path),"PublishGeoserver", self.iface.mainWindow())
            self.action.setObjectName( 'PublishGeoserver' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"PublishGeoserver", self.iface.mainWindow())
            self.action.setObjectName( 'PublishGeoserver' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "PublishGeoserver":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)



    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = PublishGeoserverDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        

        def upload_file():
            self.publish_file, _filter = QFileDialog.getOpenFileName(self.dlg, "Select input file ","", '*.shp *.gpkg *.tif *.sdat')
            crsList = ["EPSG:4326","EPSG:3857","EPSG:32643"]
            
            
        def layer_style():
            self.style_file, _filter = QFileDialog.getOpenFileName(self.dlg, "Select style file ","", '*.qml *.sld ')
            
        
        def publishLayer():
            filepath = self.publish_file
            y = os.path.basename(filepath)
            
            extension = os.path.splitext(y)[1]
            resource_id = os.path.splitext(y)[0]#store name
            auth = ("admin", "geoserver")
            workspace1 = self.dlg.lineEdit_workspace.text()
            print(workspace1,"workspace1")

            if extension ==".shp":
                print("vector")

                vlayer = QgsVectorLayer(filepath, resource_id, "ogr")
                QgsProject.instance().addMapLayer(vlayer)

                url = "http://localhost:8080/geoserver/rest/workspaces/"+workspace1+"/datastores/" + resource_id + "/external.shp"
                data = "file:////"+self.publish_file

                response = requests.put(url, data=data, auth=auth)
                print(response.text)

                print(self.publish_file, "success to publish:")
            else:
                print("raster")
                vlayer = QgsRasterLayer(filepath, resource_id)
                QgsProject.instance().addMapLayer(vlayer)

                folder_name = resource_id
                folderpath_strip = self.publish_file

                geoserver_coverage_store_url = r"http://localhost:8080/geoserver/rest/workspaces/"+workspace1+r"/coveragestores"
                geoserver_layer_publish = r"http://localhost:8080/geoserver/rest/workspaces/"+workspace1+r"/coveragestores/"
                headers = {'Content-Type': 'application/xml'}

                xmldata_datacoverage = r"<coverageStore><name>" + folder_name + "</name><enabled>true</enabled><workspace><name>"+workspace1+"</name></workspace><type>GeoTIFF</type><url>file:" + folderpath_strip + "</url></coverageStore>"

                response_new = requests.post(geoserver_coverage_store_url, headers=headers, auth=auth, data=xmldata_datacoverage)
                print(response_new)

                #publish layer
                xmldata_layer_publish1 = '''<coverage>
                        <name>'''+ folder_name +'''</name>
                        <title>'''+ folder_name +'''</title>
                        <nativeCRS>EPSG:4326</nativeCRS>
                        <srs>EPSG:4326</srs>
                        </coverage>'''

                publish_url = geoserver_layer_publish + folder_name + "/coverages"

                publish_response = requests.post(publish_url, headers=headers, auth=auth, data=xmldata_layer_publish1)
                print(publish_response)

                # geo = Geoserver('http://localhost:8080/geoserver', username='admin', password='geoserver')
                # geo.create_coveragestore(layer_name=resource_id ,path=filepath, workspace=workspace1)

                print(self.publish_file, "success to publish:")
            
            
        self.dlg.pushButton_file.clicked.connect(upload_file)
        self.dlg.pushButton_style.clicked.connect(layer_style)
        self.dlg.pushButton_publish.clicked.connect(publishLayer)


        self.dlg.label.setStyleSheet("color: brown;") 
        self.dlg.label_footer.setStyleSheet("color: blue;") 
        self.dlg.pushButton_file.setStyleSheet("color: green; ") 
        self.dlg.pushButton_file.setToolTip('click')

        self.dlg.label.setStyleSheet("color: brown;") 
        self.dlg.label_title.setStyleSheet("color: blue;") 
        self.dlg.label_2.setStyleSheet("color: brown;") 
        self.dlg.pushButton_publish.setStyleSheet("color: green;") 
        self.dlg.pushButton_style.setStyleSheet("color: green") 
        self.dlg.pushButton_style.setToolTip('click')

        self.dlg.label_workspace.setStyleSheet("color: brown;") 
        self.dlg.lineEdit_workspace.setPlaceholderText('Workspace') 


        self.dlg.show()
        self.dlg.exec_()
        