# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .aggregation_rules_dialog import AggregationRulesDialog
import os.path
from qgis import processing
#import processing
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QCheckBox, QListView, QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QCheckBox
from qgis.core import QgsVectorLayer, QgsDataSourceUri,QgsProject

import re
import  os
import psycopg2
class AggregationRules:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
       
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'AggregationRules_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Aggregation Rules')

        
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('AggregationRules', message)


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
            self.action = QAction(QIcon(icon_path),"AggregationRules", self.iface.mainWindow())
            self.action.setObjectName( 'AggregationRules' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"AggregationRules", self.iface.mainWindow())
            self.action.setObjectName( 'AggregationRules' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "AggregationRules":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
       
        if self.first_start == True:
            self.first_start = False
            self.dlg = AggregationRulesDialog()
            
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'BISAG-N_MeitY.jpg').scaledToWidth(120))
        def firstpage():
            self.dlg.stackedWidget.setCurrentIndex(1)
            
        self.dlg.pushButton.clicked.connect(firstpage)
        
        def rules():
            valtxt= self.dlg
            connection = psycopg2.connect(user="postgres", password="postgres", host=valtxt.lineEdit_ip.text(), database=valtxt.lineEdit_db.text())
            cursor = connection.cursor()
            
            formation = [['platoons'], ['companyplus1', 'company', 'companyminus1'], ['Battalionplus2', 'Battalionplus1', 'Battalion', 'Battalionminus1', 'Battalionminus2']]#proble table name

            data = {'platoons':[valtxt.lineEdit_p1.text(),valtxt.lineEdit_p2.text(),'p1','p2'],
                    'companyminus1':[valtxt.lineEdit_c11.text(),valtxt.lineEdit_c12.text(),'c_11','c_12'],
                    'company':[valtxt.lineEdit_c21.text(),valtxt.lineEdit_c22.text(),'c_21','c_22'],
                    'companyplus1':[valtxt.lineEdit_c31.text(),valtxt.lineEdit_c32.text(),'c_31','c_32'],
                    'Battalionminus2':[valtxt.lineEdit_b11.text(),valtxt.lineEdit_b12.text(),'b_11','b_12'],
                    'Battalionminus1':[valtxt.lineEdit_b21.text(),valtxt.lineEdit_b22.text(),'b_21','b_22'],
                    'Battalion':[valtxt.lineEdit_b31.text(),valtxt.lineEdit_b32.text(),'b_31','b_32'],
                    'Battalionplus1':[valtxt.lineEdit_b41.text(),valtxt.lineEdit_b42.text(),'b_41','b_42'],
                    'Battalionplus2':[valtxt.lineEdit_b51.text(),valtxt.lineEdit_b52.text(),'b_51','b_52']}##mountain
            print(data)
            
            ydata= ["".join(re.split("[^a-zA-Z]*", j[0].replace('plus','').replace('minus',''))) for j in formation]    
            
            ydata.insert(0,valtxt.lineEdit_maintable.text())
            ################################################
            k1 = 0
            for j in formation:
                
                print("\ngroup: ",j)

                proc_layer = ydata[k1]
                print("table is : ",proc_layer)
                table_name = os.path.splitext(os.path.basename(proc_layer))[0]

                query = f"SELECT EXISTS (SELECT relname FROM pg_class WHERE relname = '{table_name}');"
                cursor.execute(query)
                rows = cursor.fetchone()
                print('find table: ',rows[0]) ##True or False

                #if exist table then processing 
                if rows[0]:
                    
                    nullvalLayerpath = [proc_layer]
                    
                    for i in j:
                        print(f"for loop process of layer is :{i} :base on ",nullvalLayerpath[-1])

                        min1,max1,fn1,sfn = data[i][0],data[i][1],data[i][2],data[i][3]
                        
                        print(f'for min max fieldname fieldsize and tablename: ',min1,max1,fn1,sfn,nullvalLayerpath[-1])

                        query = f"SELECT EXISTS (SELECT relname FROM pg_class WHERE relname = '{nullvalLayerpath[-1]}');"#### check table it exist or not 
                        cursor.execute(query)
                        rows = cursor.fetchone()
                        print(rows[0]) ##True or False

                        ############dbscan cluster condition
                        cursor.execute(f"SELECT cluster_id FROM (SELECT ST_ClusterDBSCAN(geom,{max1},{min1}) OVER () AS cluster_id FROM {nullvalLayerpath[-1]}) sq;")
                        x = cursor.fetchall()
                        clusterFval = [ii[0] for ii in x]   ##### cluster field value 
                        clusterFval = [ii for ii in clusterFval if ii]   ###without null value of cluster field
                        print('clusterFval value len: ',len(clusterFval))

                        ########## id clustering value finded without null then
                        
                        if len(clusterFval)>0:
                            print("finded process .....")
                            #check table is exist or not
                            query = f"SELECT EXISTS (SELECT relname FROM pg_class WHERE relname = '{i}');"
                            cursor.execute(query)
                            tnm = cursor.fetchone()
                            
                            if tnm[0] == True: #if exist table then remove else no remove
                                print(f"remove table {i}")

                                cursor.execute(f"DROP TABLE {i}")

                            cursor.execute(f"CREATE TEMP TABLE IF NOT EXISTS {i}data(cid text, geom geometry)")#create temp table not null
                            cursor.execute(f"CREATE TEMP TABLE IF NOT EXISTS {i}null(cid text, geom geometry)")#create temp with null
                            cursor.execute(f"CREATE TABLE IF NOT EXISTS {i}({fn1} text, geom geometry)") ##create main tanle
                            
                            ##### null value (dbscan clustering)
                            cursor.execute(f'SELECT * FROM (SELECT ST_ClusterDBSCAN(geom, {max1},{min1}) OVER () AS cluster_id, geom FROM {table_name}) sq WHERE cluster_id IS NULL;')
                            dbscan_null = cursor.fetchall()
                            
                            for inull in dbscan_null:
                                cursor.execute(f"INSERT INTO {i}null(cid, geom) VALUES (%s, %s)",(inull[0] ,inull[1]))
                            nullvalLayerpath.append(f'{i}null')
                            
                            ##### with not null value (dbscan clustering)
                            cursor.execute(f'SELECT * FROM (SELECT ST_ClusterDBSCAN(geom, {max1},{min1}) OVER () AS cluster_id, geom FROM {table_name}) sq WHERE cluster_id IS NOT NULL;')
                            dbscan = cursor.fetchall()
                            for dbc in dbscan:
                                cursor.execute(f"INSERT INTO {i}data(cid, geom) VALUES (%s, %s)",(dbc[0] ,dbc[1]))
                            
                            ##dissolve and centroid:
                            cursor.execute(f'SELECT st_centroid(ST_Collect(geom)) AS geom, array_agg(cid) AS cid1 FROM (SELECT cid, ST_ClusterDBSCAN(geom, {max1},{min1}) over () AS cid1, geom FROM {i}data) sq GROUP BY cid')
                            dis_cent_res= cursor.fetchall()
                            for dis_cent in dis_cent_res:
                                cursor.execute(f"INSERT INTO {i}({fn1}, geom) VALUES (%s, %s)",(dis_cent[1][1] ,str(dis_cent[0])))

                            connection.commit()
                           
                            print(f"success ::{i} table \n")
                            
                            #####open postgis layer
                            tablename = f"{i}"
                            geometrycol = "geom"

                            pnode = QgsDataSourceUri()
                            pnode.setConnection(valtxt.lineEdit_ip.text(), "5432", valtxt.lineEdit_db.text(), "postgres", "postgres")
                            pnode.setDataSource("public", tablename, geometrycol)
                            nodelayer = QgsVectorLayer(pnode.uri(), tablename, "postgres")
                            QgsProject.instance().addMapLayer(nodelayer)
                    
                        else:
                            print(" not dbscan cluster found (i.e all NULL value of field )"," continue next process ..:::..\n")
                else:
                    print(f"stop process because: {proc_layer} table not find for : ",j,'\n')
                    
                k1 = k1 + 1
            #################################################
            
        self.dlg.pushButton_rule.clicked.connect(rules)
        
        self.dlg.stackedWidget.setCurrentIndex(0)
        
        ##style
        self.dlg.pushButton.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_rule.setStyleSheet("color: green;font-size: 12pt; ") 
        
        self.dlg.label_title.setStyleSheet("color: purple;") 

        self.dlg.label.setStyleSheet("color: brown;") 
        self.dlg.label_2.setStyleSheet("color: brown;") 
        self.dlg.label_3.setStyleSheet("color: brown;") 
        self.dlg.label_p.setStyleSheet("color: brown;") 
        self.dlg.label_c3.setStyleSheet("color: brown;") 
        self.dlg.label_c2.setStyleSheet("color: brown;") 
        self.dlg.label_c1.setStyleSheet("color: brown;") 
        self.dlg.label_b5.setStyleSheet("color: brown;") 
        self.dlg.label_b4.setStyleSheet("color: brown;") 
        self.dlg.label_b3.setStyleSheet("color: brown;") 
        self.dlg.label_b2.setStyleSheet("color: brown;") 
        self.dlg.label_b1.setStyleSheet("color: brown;") 
        self.dlg.label_min.setStyleSheet("color: blue;") 
        self.dlg.label_eps.setStyleSheet("color: blue;") 
        self.dlg.label_4.setStyleSheet("color: red;") 




        self.dlg.show()
        self.dlg.exec_()
        