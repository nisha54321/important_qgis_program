# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *
from .line_angledis_dialog import Line_AngledisDialog
import os.path

from PyQt5 import QtGui
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,
    QgsPointXY,QgsPoint,QgsProcessingFeatureSourceDefinition ,QgsFeatureRequest,QgsVectorFileWriter,
    QgsMarkerSymbol,QgsCategorizedSymbolRenderer,QgsRendererCategory,QgsSymbol,
    QgsVectorLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField )
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis.gui import  QgsMapToolEmitPoint
import pandas as pd
import re
from PyQt5.QtCore import *
from qgis import processing
class Line_Angledis:
    xy = []
    coord = []
    x = 0.0
    y = 0.0
    c = 1
    iii = 0
    layer = ''
    vl = ''
    filename = ''
    roiname = ''
    r_layer = ''
    save = ''
    lyr_list = []
    lastlayertime = ''
    lstId = 0
    addlayerpath = []
    fn = ''
    csv = ''
    layeris = ''
    field_name = []

    def __init__(self, iface):
       
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Line_Angledis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Line Angledis')

        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('Line_Angledis', message)


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
            self.action = QAction(QIcon(icon_path),"Line_Angledis", self.iface.mainWindow())
            self.action.setObjectName( 'Line_Angledis' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"Line_Angledis", self.iface.mainWindow())
            self.action.setObjectName( 'Line_Angledis' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "Line_Angledis":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = Line_AngledisDialog()
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+os.sep+'BISAG-N_MeitY.jpg').scaledToWidth(120))
        
        if(self.iii == 0):
            getCrs = 'EPSG:4326'
            self.vl = QgsVectorLayer("Point?crs="+getCrs, "point", "memory")
            op = plugin_dir+f'{os.sep}output{os.sep}'
            point1 =plugin_dir+f'{os.sep}point{os.sep}'
            line1 = plugin_dir+f'{os.sep}line{os.sep}'
            
            path2 = [op,point1,line1]
            
            for path1 in path2:
                for root, dirs, files in os.walk(path1):##remove geojson files
                    for file in files:
                        os.remove(os.path.join(root, file))
                    
            self.iii = 1
        
        def select():
            self.csv, _filter = QFileDialog.getOpenFileName(self.dlg, "Select existing layer for segment  ","", '*.csv *.xlsx')
            df = pd.read_csv (self.csv)

            pd.set_option('display.max_rows', 150000)
            pd.set_option('display.max_columns', 500)

            column_name= list(df.columns)
            
            col_val = []
            
            for i in column_name:
                field = QgsField(i, QVariant.String)
                self.field_name.append(field)
                val = df[i].tolist()
                col_val.append(val)
            self.field_name.append(QgsField('x', QVariant.String))
            self.field_name.append(QgsField('y', QVariant.String))
            
            csvAttVal = list(zip(*col_val))
            
                   
            
            for points in csvAttVal:
                nan = pd.isna(points[2])
    
                if not nan:
                    x,y=points[3],points[2]
                    
                    try:
                 
                        direction,deg, minutes, seconds =  re.split('[ °\']', x)
                        coordx = (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction in ['W', 'S'] else 1)
                        
                        direction1,deg1, minutes1, seconds1 =  re.split('[ °\']', y)
                        coordy = (float(deg1) + float(minutes1)/60 + float(seconds1)/(60*60)) * (-1 if direction1 in ['W', 'S'] else 1)
                        
                        layer = QgsVectorLayer("Point?crs="+getCrs, "point", "memory")

                        
                        symbol = QgsMarkerSymbol.createSimple({'color': 'green','size':'2'})
                        layer.renderer().setSymbol(symbol)
                        
                        attvalAdd = [i for i in points]
                        attvalAdd.append(coordx)
                        attvalAdd.append(coordy)
                        

                        
                        pr = layer.dataProvider() 
                        layer.startEditing()
                        pr.addAttributes(self.field_name)
                        layer.updateFields() 
                        f = QgsFeature()   
                        
                        
                        f.setAttributes(attvalAdd)
                        
                        layer.updateFields()

                        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coordx,coordy)))
                        pr.addFeatures([f])

                        layer.triggerRepaint()
                        layer.commitChanges()
                        
                        #QgsProject.instance().addMapLayers([layer])
                        
                        QgsVectorFileWriter.writeAsVectorFormat(layer, plugin_dir+f"{os.sep}point{os.sep}{points[5]}_point.shp", "UTF-8", layer.crs(), "ESRI Shapefile")
                        #print(points[5],points[19])
                        
                        res = processing.run("shapetools:createlob", 
                           {'INPUT':layer,
                            'Azimuth':points[5],
                            'Distance':points[19],
                            'Offset':0,
                            'Units':1,'ExportInputGeometry':False,
                            'OUTPUT':plugin_dir+f'{os.sep}line{os.sep}{points[5]}_line.shp'}) 
                        
                        # v2 = QgsVectorLayer(res['OUTPUT'], f"{points[5]}_line", "ogr")

                        # QgsProject.instance().addMapLayers([v2])


                    except Exception as e:
                        pass
            self.dlg.pushButton_merge.show()
            
        
           
        self.dlg.pushButton_select.clicked.connect(select)   
        
        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            
            self.x = coorx
            self.y = coory
            
            pnt = QgsPoint(self.x,self.y)
            
            self.coord.append(self.x)
            self.coord.append(self.y)

            self.xy.append(pnt)
        
            symbol = QgsMarkerSymbol.createSimple({ 'color': 'blue','size':'3'})
            self.vl.renderer().setSymbol(symbol)

            self.vl.triggerRepaint()

            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx, coory)))
            pr = self.vl.dataProvider()
            self.vl.triggerRepaint()

            pr.addFeature(f)
            self.vl.updateExtents() 
            self.vl.updateFields() 
            QgsProject.instance().addMapLayers([self.vl])
            
            self.dlg.lineEdit_lat.setText(str(round(coory, 3)  ))
            self.dlg.lineEdit_long.setText(str(round(coorx, 3)  ))


        canvas = self.iface.mapCanvas()
        pointTool = QgsMapToolEmitPoint(canvas)
        
        def clickCanvas():
            
            pointTool.canvasClicked.connect( display_point )
            canvas.setMapTool( pointTool )
            self.dlg.label_2.show()
            self.dlg.label_4.show()
            self.dlg.label.show()
            self.dlg.label_5.show()
            self.dlg.label_6.show()
            self.dlg.lineEdit_lat.show()
            self.dlg.lineEdit_long.show()
            self.dlg.lineEdit_bear.show()
            self.dlg.lineEdit_dis.show()
            self.dlg.pushButton.show()
            
        self.dlg.pushButton_click.clicked.connect(clickCanvas)  
        
        def drawLine():
            bear =self.dlg.lineEdit_bear.text()
            dis = self.dlg.lineEdit_dis.text()
            
            res = processing.run("shapetools:createlob", 
                           {'INPUT':self.vl,
                            'Azimuth':bear,
                            'Distance':dis,
                            'Offset':0,
                            'Units':1,'ExportInputGeometry':False,
                            'OUTPUT':plugin_dir+f'{os.sep}output{os.sep}output_line.shp'}) 
                        
            v2 = QgsVectorLayer(res['OUTPUT'], f"output_line", "ogr")
            QgsProject.instance().addMapLayers([v2])
            
        def merge():
            dirline = plugin_dir+f'{os.sep}line{os.sep}'
            dirpoint = plugin_dir+f'{os.sep}point{os.sep}'

            allline = []
            for file in os.listdir(dirline):
                if file.endswith(".shp"):
                    fpath = os.path.join(dirline, file)
                    allline.append(fpath)
            allpoint = []
            for file in os.listdir(dirpoint):
                if file.endswith(".shp"):
                    fpath = os.path.join(dirpoint, file)
                    allpoint.append(fpath)
                    
            res1 = processing.run("native:mergevectorlayers",
                           {'LAYERS':allline,
                            'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                            'OUTPUT':plugin_dir+f'{os.sep}output{os.sep}merge_line.shp'})
            
            res2 = processing.run("native:mergevectorlayers",
                           {'LAYERS':allpoint,
                            'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                            'OUTPUT':plugin_dir+f'{os.sep}output{os.sep}merge_point.shp'})
            
            v1 = QgsVectorLayer(res1['OUTPUT'], f"output_line", "ogr")
            v2 = QgsVectorLayer(res2['OUTPUT'], f"output_point", "ogr")
            
            list1 = [v1,v2]
            for r_layer in list1:
                ficon = r_layer.fields().indexFromName('PRI Type')
                icon1 = r_layer.dataProvider().uniqueValues(ficon)
                icon12 = list(icon1)
                icon12.sort()
                categories = []

                for value in icon12:
                    symbol = QgsSymbol.defaultSymbol(r_layer.geometryType())
                    category = QgsRendererCategory(value, symbol, str(value))#
                    categories.append(category)
                    
                renderer = QgsCategorizedSymbolRenderer('PRI Type', categories)
                if renderer is not None:
                    r_layer.setRenderer(renderer)    
                r_layer.triggerRepaint()

            QgsProject.instance().addMapLayers([v1,v2])

        self.dlg.pushButton_merge.clicked.connect(merge)  

        self.dlg.pushButton.clicked.connect(drawLine)  
        
        
        self.dlg.pushButton_merge.setToolTip('click')
        self.dlg.pushButton.setToolTip('click')
        self.dlg.pushButton_select.setToolTip('click')
        
        self.dlg.pushButton_merge.setStyleSheet("color: green;")
        self.dlg.pushButton.setStyleSheet("color: green;")
        self.dlg.pushButton_click.setStyleSheet("color: green;")

        
        self.dlg.label_2.hide()
        self.dlg.label_4.hide()
        self.dlg.label_5.hide()
        self.dlg.label_6.hide()
        self.dlg.lineEdit_lat.hide()
        self.dlg.lineEdit_long.hide()
        self.dlg.lineEdit_bear.hide()
        self.dlg.lineEdit_dis.hide()
        self.dlg.pushButton.hide()
        self.dlg.pushButton_merge.hide()
        
        
        self.dlg.label_2.setStyleSheet("color: brown;")
        self.dlg.label_4.setStyleSheet("color: brown;")
        self.dlg.label.setStyleSheet("color: brown;")
        self.dlg.label_5.setStyleSheet("color: brown;")
        self.dlg.label_6.setStyleSheet("color: brown;")
        self.dlg.label_8.setStyleSheet("color: brown;")
        
        self.dlg.label_7.setStyleSheet("color: purple;")

        self.dlg.label_3.setStyleSheet("color: blue;")
        self.dlg.label.setStyleSheet("color: brown;")
        self.dlg.pushButton_select.setStyleSheet("color: green;")
        self.dlg.pushButton_merge.setStyleSheet("color: purple;")
        
        



        self.dlg.show()
        self.dlg.exec_()
       