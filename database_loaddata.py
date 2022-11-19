# -*- coding: utf-8 -*-
from sqlite3 import Cursor
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *
from .database_loaddata_dialog import DatabaseLoaddataDialog
import os.path

from PyQt5 import QtGui
import psycopg2
from qgis.core import QgsVectorLayer,QgsProject,QgsDataSourceUri,QgsSnappingConfig
from qgis.core import Qgis

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 

from datetime import datetime

class DatabaseLoaddata:
    dblayer = ''
    alltbl = []
    checkbox = ''
    un = ''
    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DatabaseLoaddata_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Database Loaddata New')

        self.first_start = None

    def tr(self, message):
       
        return QCoreApplication.translate('DatabaseLoaddata', message)


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
            self.action = QAction(QIcon(icon_path),"DatabaseLoaddata", self.iface.mainWindow())
            self.action.setObjectName( 'DatabaseLoaddata' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"DatabaseLoaddata", self.iface.mainWindow())
            self.action.setObjectName( 'DatabaseLoaddata' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "DatabaseLoaddata":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = DatabaseLoaddataDialog()

        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))

        dbname = "plugin"

        connection = psycopg2.connect(user="postgres", password="postgres", host="localhost", database=dbname)
        cursor = connection.cursor()

        #log table create:
        cursor.execute("CREATE TABLE IF NOT EXISTS swamitva_metadata_log(id serial NOT NULL,date timestamp without time zone,layertype character varying(255),projectname character varying(255),publishlayer character varying(255),tablename character varying(255),upload_file character varying(255),userid integer,username character varying(70),EditFID text,state character varying(70),CONSTRAINT swamitva_metadata_pkey PRIMARY KEY (id),CONSTRAINT uk_8m19pvbie0yfgm32bk2sj754a UNIQUE (publishlayer))")
        selectLayer1 =[]
        def editlayer():
            current_datetime = datetime.now()
            self.dlg.pushButton_save.show()
            self.dlg.comboBox.show()#
            self.dlg.checkBox_snap.show()#checkBox_snap


            connection = psycopg2.connect(user="postgres", password="postgres", host="localhost", database=dbname)
            cursor = connection.cursor()
            dburi = QgsDataSourceUri()
            dburi.setConnection("localhost", "5432", dbname, "postgres", "postgres")
            
            spatialtablename = "SELECT table_name FROM information_schema.columns WHERE column_name = 'geom' or column_name = 'wkb_geometry' or column_name = 'the_geom' or column_name = 'geometry'"
            cursor.execute(spatialtablename)
            alltable = cursor.fetchall()

            def checklayer(checkbox):
                chb1 = checkbox.sender()

                if chb1.isChecked():

                    new_conf = QgsSnappingConfig(QgsProject.instance().snappingConfig())
                    new_conf.setEnabled(True)
                    QgsProject.instance().setSnappingConfig(new_conf)
                    QgsProject.instance().setTopologicalEditing(True)
                else:
                    new_conf = QgsSnappingConfig(QgsProject.instance().snappingConfig())
                    new_conf.setEnabled(False)
                    QgsProject.instance().setSnappingConfig(new_conf)
                    QgsProject.instance().setTopologicalEditing(False)

            self.dlg.checkBox_snap.stateChanged.connect(lambda:checklayer(self.dlg.checkBox_snap))

            
            def onChanged():
                selectLayer = self.dlg.comboBox.currentText()
                selectLayer1.append(selectLayer)
                print(selectLayer)

                #edit layer (according check box)
                layer = QgsProject.instance().mapLayersByName(selectLayer)[0]
                QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
                self.iface.setActiveLayer(layer)

                layer.startEditing()
                self.iface.actionVertexTool().trigger()

                #zoom to layer
                canvas = self.iface.mapCanvas()
                extent = layer.extent()
                canvas.setExtent(extent)
                canvas.refresh()

                self.dlg.showMinimized()
                
            for i in alltable:
                tbname = i[0]
                print(tbname)

                #self.checkbox = QCheckBox(tbname)
                self.dlg.comboBox.addItem(tbname)
                self.dlg.comboBox.setStyleSheet("color: Indigo;") 


                dburi.setDataSource("public", tbname, "geom")
                self.dblayer = QgsVectorLayer(dburi.uri(), tbname, "postgres")
                self.alltbl.append((self.dblayer))
                QgsProject.instance().addMapLayer(self.dblayer)

                QgsProject.instance().layerTreeRoot().findLayer(self.dblayer.id()).setItemVisibilityChecked(False)


            self.dlg.comboBox.activated[str].connect(onChanged)

            self.iface.actionVertexTool().trigger()

            #self.dlg.showMinimized()
            self.dlg.pushButton_stopedit.show()

        self.dlg.pushButton_edit.clicked.connect(editlayer)

        def stopEdit():
            current_datetime = datetime.now()
            test_list = list(set(selectLayer1))
            tbname = str(test_list)
            tbname = tbname.replace("[","")
            tbname = tbname.replace("]","")
            tbname = tbname.replace("'","")

            print(tbname)
            un = self.dlg.lineEdit_user.text()
            #cursor.execute("CREATE TABLE IF NOT EXISTS swamitva_metadata_log(id serial NOT NULL,date timestamp without time zone,layertype character varying(255),projectname character varying(255),publishlayer character varying(255),tablename character varying(255),upload_file character varying(255),userid integer,username character varying(70),state character varying(70),CONSTRAINT swamitva_metadata_pkey PRIMARY KEY (id),CONSTRAINT uk_8m19pvbie0yfgm32bk2sj754a UNIQUE (publishlayer))")
            layer = self.iface.activeLayer()
            
            res = QMessageBox.question( self.iface.mainWindow(),"Stop Editing","Do you want to save the changes to layer {}?".format(layer),QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if res == QMessageBox.Save:
                buffer = layer.editBuffer()
                print(buffer.changedGeometries())

                changed_geom =  buffer.changedGeometries().keys() #list of feature ID
                editfid = list(changed_geom)
                print(list(changed_geom))

                layer.commitChanges()
                print("save")

            elif res == QMessageBox.Discard:
                editfid = 'none'
                layer.rollBack()
                print("rollBack")

            elif res == QMessageBox.Cancel:
                editfid = 'none'

            print(self.un,"username")
            editlayername = str(selectLayer1[-1])
            editlayername = editlayername.replace("[","")
            editlayername = editlayername.replace("]","")
            editlayername = editlayername.replace("'","")

            cursor.execute("INSERT INTO swamitva_metadata_log (date ,tablename, username ,EditFID) VALUES (%s, %s, %s,%s)",(current_datetime, editlayername, self.un ,str(editfid)))
            connection.commit()


        self.dlg.pushButton_stopedit.clicked.connect(stopEdit)

        def save():
            i = self.iface.activeLayer()
            i.commitChanges()
            i.startEditing()
            self.iface.actionVertexTool().trigger()

            print("layer save:")
        self.dlg.pushButton_save.clicked.connect(save)

        def login():
            un = self.dlg.lineEdit_user.text()
            pswrd = self.dlg.lineEdit_password.text()

            cursor.execute("select username,password1 from login ")
            user_pass = cursor.fetchall()

            for u_p in user_pass:

                if un ==u_p[0] and pswrd == u_p[1]:
                    self.dlg.pushButton_out.show()
                    user = self.dlg.lineEdit_user.text()

                    self.dlg.label_logineusername.setText("Wellcome : "+str(user))
                    self.un = user

                    self.dlg.pushButton_edit.show()
                   
                    self.dlg.label_ld.show()

                    self.iface.messageBar().pushMessage("success", level=Qgis.Info)

                    self.dlg.label_login.hide()
                    self.dlg.label_password.hide()
                    self.dlg.label_user.hide()
                    self.dlg.lineEdit_password.hide()
                    self.dlg.lineEdit_user.hide()
                    user = self.dlg.lineEdit_user.text()
                    self.dlg.label_logineusername.show()
                    self.dlg.pushButton_login.hide()
                else:
                    self.dlg.lineEdit_user.setPlaceholderText('Enter valid Username')
                    self.dlg.lineEdit_password.setPlaceholderText('Enter valid Password')
                    self.dlg.lineEdit_user.setText("")
                    self.dlg.lineEdit_password.setText("")
                    

        def logout():
            #remove all layers
            QgsProject.instance().removeAllMapLayers()
            self.dlg.comboBox.clear()#clear all combobox items

            self.dlg.label_login.show()
            self.dlg.label_password.show()
            self.dlg.label_user.show()
            self.dlg.lineEdit_password.show()
            self.dlg.lineEdit_user.show()

            self.dlg.lineEdit_password.setText("")
            self.dlg.lineEdit_user.setText("")

            self.dlg.pushButton_out.show()
            self.dlg.label_logineusername.hide()
            self.dlg.pushButton_login. show()
            self.dlg.pushButton_out.hide()

            self.dlg.label_ld.hide()
            self.dlg.pushButton_edit.hide()
            self.dlg.pushButton_stopedit.hide()

            self.dlg.comboBox.hide()
            self.dlg.checkBox_snap.hide()

            self.dlg.pushButton_save.hide()

        self.dlg.pushButton_login.clicked.connect(login)
        self.dlg.pushButton_login.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_login.setToolTip('click')

        self.dlg.pushButton_out.clicked.connect(logout)
        self.dlg.pushButton_out.setStyleSheet("color: red;font-size: 12pt; ") 
        self.dlg.pushButton_out.setToolTip('click')
        self.dlg.pushButton_out.hide()
        self.dlg.pushButton_edit.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_edit.setToolTip('click')
        self.dlg.pushButton_stopedit.setStyleSheet("color: blue;font-size: 12pt; ") 
        self.dlg.pushButton_stopedit.setToolTip('click')
        self.dlg.label_ld.setStyleSheet("color: brown;") 

        self.dlg.pushButton_login.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_login.setToolTip('click')

        self.dlg.label_login.setStyleSheet("color: blue;font-size: 12pt;") 
        self.dlg.label_user.setStyleSheet("color: brown; ") 
        self.dlg.label_password.setStyleSheet("color: brown;") 

        self.dlg.lineEdit_user.setPlaceholderText('Enter Username')
        self.dlg.lineEdit_password.setPlaceholderText('Enter Password')
        self.dlg.lineEdit_password.setEchoMode(QLineEdit.Password)###password mode
        self.dlg.label_footer.setStyleSheet("color: blue;") 
        self.dlg.label_logineusername.setStyleSheet("color: blue;font-size: 12pt;") 

        self.dlg.pushButton_edit.hide()
        self.dlg.label_logineusername.hide()

        self.dlg.pushButton_save.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_save.setToolTip('click')
        self.dlg.pushButton_save.hide()

        self.dlg.checkBox_snap.setStyleSheet("color: brown; ") #

        self.dlg.label_ld.hide()
        self.dlg.pushButton_stopedit.hide()
        self.dlg.pushButton_out.hide()

        self.dlg.comboBox.hide()
        self.dlg.checkBox_snap.hide()



        self.dlg.show()
        self.dlg.exec_()
        