# -*- coding: utf-8 -*-
from qgis.core import QgsVectorFileWriter

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, QtGui
from qgis.core import Qgis
import subprocess
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .raster_path_dialog import RasterPathDialog
import os.path
from qgis import processing
from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsPointXY,
    QgsRaster,
    QgsRasterShader,
    QgsColorRampShader,QgsLayerTreeLayer,
    QgsSingleBandPseudoColorRenderer,QgsVectorLayerTemporalProperties,QgsCoordinateReferenceSystem,QgsSvgMarkerSymbolLayer,QgsVectorFileWriter,
    QgsSingleBandColorDataRenderer,
    QgsSingleBandGrayRenderer,QgsVectorLayer, QgsPoint, QgsVectorLayer, QgsFeature, QgsGeometry, QgsVectorFileWriter, QgsField, QgsPalLayerSettings, QgsVectorLayerSimpleLabeling
)
from qgis.gui import QgsMapToolIdentifyFeature, QgsMapToolEmitPoint
from PyQt5 import QtWidgets 
from PyQt5 import QtGui
from qgis.PyQt.QtWidgets import QAction
import re, os.path
from qgis.PyQt.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QWidget, QVBoxLayout, QAction, QLabel, QLineEdit, QMessageBox, QFileDialog, QFrame, QDockWidget, QProgressBar, QProgressDialog, QToolTip
from datetime import timedelta, datetime
from time import strftime
from time import gmtime

class RasterPath:
    """QGIS Plugin Implementation."""
    xy = []
    iii = 0
    vl = ''
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
            'RasterPath_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Raster Path')

        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('RasterPath', message)


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
            self.action = QAction(QIcon(icon_path),"RasterPath", self.iface.mainWindow())
            self.action.setObjectName( 'RasterPath' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"RasterPath", self.iface.mainWindow())
            self.action.setObjectName( 'RasterPath' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "RasterPath":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        if self.first_start == True:
            self.first_start = False
            self.dlg = RasterPathDialog()
        
        plugin_dir = os.path.dirname(__file__)

        ##
        f = open(plugin_dir+"/mobility_wkt1.txt", "r")
        wkt = f.read()

        temp = QgsVectorLayer("MultiPolygon?crs=EPSG:4326", "Wkt polygon", "memory")
        #QgsProject.instance().addMapLayer(temp)

        ###border remove polygon
        single_symbol_renderer = temp.renderer()
        symbol = single_symbol_renderer.symbol()
        #Set fill colour
        symbol.setColor(QColor.fromRgb(0,255,28))
        #Set fill style
        symbol.symbolLayer(0).setStrokeStyle(Qt.PenStyle(Qt.NoPen))

        temp.triggerRepaint()

        temp.startEditing()
        geom = QgsGeometry()
        geom = QgsGeometry.fromWkt(wkt)
        feat = QgsFeature()
        feat.setGeometry(geom)
        temp.dataProvider().addFeatures([feat])
        temp.commitChanges()
        #save file code
        QgsVectorFileWriter.writeAsVectorFormat(temp, plugin_dir+"/wktpolygon.shp", "UTF-8", temp.crs(), "ESRI Shapefile")

        processing.run("native:rasterize",
                {'EXTENT':'71.004347413,71.266877426,26.193131580,26.432582205 [EPSG:4326]',
                'EXTENT_BUFFER':0,
                'TILE_SIZE':1024,
                'MAP_UNITS_PER_PIXEL':0.00005,
                'MAKE_BACKGROUND_TRANSPARENT':False,
                'MAP_THEME':None,
                'LAYERS':[temp],
                'OUTPUT':plugin_dir+'/convertMapRaster.tif'})
                
        processing.run("gdal:rearrange_bands",
                    {'INPUT':plugin_dir+'/convertMapRaster.tif',
                    'BANDS':[1],
                    'OPTIONS':'',
                    'DATA_TYPE':0,
                    'OUTPUT':plugin_dir+'/singleband.tif'})
                    
        processing.run("native:reclassifybytable",
                    {'INPUT_RASTER':plugin_dir+'/singleband.tif',
                    'RASTER_BAND':1,
                    'TABLE':[0,38,1,38,255,2],
                    'NO_DATA':-9999,
                    'RANGE_BOUNDARIES':0,
                    'NODATA_FOR_MISSING':False,
                    'DATA_TYPE':5,
                    'OUTPUT':plugin_dir+'/recassify.tif'})

            
        if(self.iii == 0):
            self.vl = QgsVectorLayer("Point?crs=EPSG:4326", "markpoint", "memory")
            self.rlayer = QgsRasterLayer(plugin_dir+'/recassify.tif', "nogoarea")

            QgsProject.instance().addMapLayer(self.rlayer)
            op = plugin_dir+"/linestring.shp"
            if os.path.exists(op):
                os.remove(op)

            op1 = plugin_dir+"/buffer.shp"
            if os.path.exists(op1):
                os.remove(op1)
                
            self.iii = 1
        
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))
        #buffer create 
        def buffer():
            bufferSize = self.dlg.lineEdit.text()
            bufferSize = (float(bufferSize)/111000)/2
            out_buffer_path = plugin_dir+'/buffer.shp'#0.0027027027

            processing.run("native:buffer", {'INPUT':plugin_dir+'/linestring.shp',
                        'DISTANCE':bufferSize,
                        'SEGMENTS':5,
                        'END_CAP_STYLE':0,
                        'JOIN_STYLE':0,
                        'MITER_LIMIT':2,
                        'DISSOLVE':False,
                        'OUTPUT':out_buffer_path})

            vlayer = QgsVectorLayer(out_buffer_path, "Buffer", "ogr")
            if not vlayer.isValid():
                print("Layer failed to load!")
            else:
                QgsProject.instance().addMapLayer(vlayer)

       

        self.dlg.label_path.show()
        self.dlg.pushButton_path.show()
        
        self.dlg.label_info.show()
        self.iface.messageBar().pushMessage("Please Select Two Points for Shortest Path", level=Qgis.Info)

        #point_label = iter(["source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination"])

        x = "Source,Destination,"
        y = x *10
        z = y.split(",")

        point_label = iter(z)
        
        ##get coordinates of click event
        def display_point( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            print(coorx, coory)
            self.xy.append(coorx)
            self.xy.append(coory)

            #marked points
            self.vl.renderer().symbol().setColor(QColor("red"))
            self.vl.renderer().symbol().setSize(4)

            self.vl.triggerRepaint()

            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx, coory)))
            pr = self.vl.dataProvider()

            #Add Attribute
            self.vl.startEditing()
            pr.addAttributes([QgsField("point_label", QVariant.String)])

            x = next(point_label)
            attvalAdd = [x]
            f.setAttributes(attvalAdd)
            self.vl.triggerRepaint()

            pr.addFeature(f)
            self.vl.updateExtents() 
            self.vl.updateFields() 
            QgsProject.instance().addMapLayers([self.vl])

            #set label
            layer_settings  = QgsPalLayerSettings()
            layer_settings.fieldName = "point_label"
            layer_settings.placement = 2
            layer_settings.enabled = True

            layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
            self.vl.setLabelsEnabled(True)
            self.vl.setLabeling(layer_settings)
            self.vl.triggerRepaint()
            self.vl.startEditing()
            self.vl.triggerRepaint()

            ###################### user not click obstacles part .....(give message ....(not valid))
            ident = self.rlayer.dataProvider().identify(QgsPointXY(coorx, coory), QgsRaster.IdentifyFormatValue)

            if ident.isValid():
                v = ident.results()
                val = v[1]
                
                if val == 0.0:
                    self.iface.messageBar().pushMessage("This is OBSTACLES or NOGOAREA ", level=Qgis.Info)
                    self.iface.messageBar().pushMessage("please click valid input point ", level=Qgis.Info)
                else:
                    pass

       
        canvas = self.iface.mapCanvas()   
        pointTool = QgsMapToolEmitPoint(canvas)
        pointTool.canvasClicked.connect( display_point )
        canvas.setMapTool( pointTool )
 
        def line1():
            self.iface.messageBar().pushMessage("Please wait ...............", level=Qgis.Info)
            start_point = QgsPoint(self.xy[-4], self.xy[-3])
            end_point = QgsPoint(self.xy[-2], self.xy[-1])
            print("line====  ",self.xy)
            import os

            os.system(f"python3 /home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/shortest_path.py {self.xy[-4]} {self.xy[-3]} {self.xy[-2]} {self.xy[-1]}")
            
            vl = QgsVectorLayer("MultiLineString?crs=EPSG:4326", "Shortest path", "memory")
            vl.renderer().symbol().setColor(QColor("green"))
            vl.renderer().symbol().setWidth(1.06)

            vl.triggerRepaint()
            pr = vl.dataProvider()
            wktdata = ''

            with open("/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/path.txt", 'r') as file_obj:
                wkt1 = file_obj.read().strip()
                multiwkt = wkt1.split(os.linesep)
                
                for wkt in  multiwkt:
                    vl.startEditing()

                    pr = vl.dataProvider()
                    pr.addAttributes([QgsField("length", QVariant.String)])
                    vl.updateFields()

                    feature_obj = QgsFeature()
                    
                    feature_obj.setGeometry(QgsGeometry.fromWkt(wkt))
                    pr.addFeature(feature_obj)
                    
                    x = feature_obj.geometry().length()*100
                    len1 = "%.2f" % x +" km"

            #        print(len1)
                    feature_obj.setAttributes([len1])
                    pr.addFeatures([feature_obj])
                    
                    vl.triggerRepaint()
                    vl.updateExtents() 
                    
                    layer_settings  = QgsPalLayerSettings()
                    layer_settings.fieldName = "length"
                    layer_settings.placement = 2
                    layer_settings.enabled = True

                    layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
                    vl.setLabelsEnabled(True)
                    vl.setLabeling(layer_settings)
                    vl.triggerRepaint()
                    vl.startEditing()
                    vl.commitChanges()
                    QgsProject.instance().addMapLayer(vl)
        
                    ###animationAt
                    for feature in vl.getFeatures():
                        geom = feature.geometry()
                        wktdata1 = geom.asWkt()
                        wktdata += wktdata1
            ##find min value of field
            fieldname='length'
            #layer=iface.activeLayer()
            idx=vl.fields().indexFromName(fieldname)
            print("min distance")

            slen = vl.minimumValue(idx)
            print(vl.minimumValue(idx))

            ###selection feature of layer according to short length
            vl.selectByExpression('"length"= '+"'"+slen+"'", QgsVectorLayer.SetSelection)
            self.iface.mapCanvas().setSelectionColor( QColor("blue") )
   
            #add maptips(mouse hover)
            expression = """[%  @layer_name  %]"""
            vl.setMapTipTemplate(expression)

            vl.updateExtents() 
            vl.updateFields() 
            
            #############################################
            ##intersection between shortest path with road ,rail and settlement
            # roadrailset = []
            # name = ["Rail_","Road_","Settlement"]
            # s1 = iter(name)
            # for file in os.listdir(plugin_dir+"/data/"):
            #     if file.endswith(".shp"):
            #         fpath = os.path.join(plugin_dir+"/data/", file)
            #         roadrailset.append(fpath)
            # print("road rail sett :",roadrailset)

            # for line in roadrailset:
            #     y1 = next(s1)
            #     processing.run("native:lineintersections",
            #                     {'INPUT':vl,
            #                     'INTERSECT':line,
            #                     'INPUT_FIELDS':[],
            #                     'INTERSECT_FIELDS':[],
            #                     'INTERSECT_FIELDS_PREFIX':'',
            #                     'OUTPUT':plugin_dir+'/intersect/%sIntersect.shp'%(y1)})
            #     vlayer = QgsVectorLayer(plugin_dir+'/intersect/%sIntersect.shp'%(y1), '%sIntersect.shp'%(y1))
            #     vlayer.renderer().symbol().setColor(QColor("Coral"))
            #     vlayer.renderer().symbol().setSize(3)

            #     vlayer.triggerRepaint()
            #     QgsProject.instance().addMapLayer(vlayer)

            #add animation csv file

            for feature in vl.getFeatures():
               geom = feature.geometry()
               wkt = geom.asWkt()
               
            wkt = wktdata
            wkt = wkt.replace("LineString (","")

            wkt = wkt.replace(")LineString (",",")
            wkt = wkt.replace(")","")

            longlat = wkt.split(", ")
            pair = list(zip(longlat, longlat[1:] + longlat[:1]))
            animationfile = open(plugin_dir+"/animationcsv/Animation_path.csv","w")
            animationfile.write("field_1,field_2,field_3,field_4\n")

            min1 = 0
            ct = str(datetime.now())
            timelist = []
            timelist.append(ct)

            for i in pair:
                x = (i[0])
                coord = x.replace(" ",",")
                
                min1 +=2
                add = str(datetime.now() +timedelta( minutes=min1 ))
                timelist.append(add)

                csv = timelist[0] +","+ coord +","+ timelist[1]
                timelist.pop(0)
                
                animationfile.write(csv+"\n")
   
            animationfile.close()
           
            #######################save shortest path layer

            save_options = QgsVectorFileWriter.SaveVectorOptions()
            save_options.driverName = "ESRI Shapefile"
            save_options.fileEncoding = "UTF-8"
            transform_context = QgsProject.instance().transformContext()
            error = QgsVectorFileWriter.writeAsVectorFormatV2(vl,
                                                  plugin_dir+"/linestring.shp",
                                                  transform_context,
                                                  save_options)
            if error[0] == QgsVectorFileWriter.NoError:
                print("success again!")
            else:
                print(error)

            buffer()
            
            os.system(f"python3 {plugin_dir}/elevation_profile.py")
            self.dlg.pushButton_cesium.show()
            self.dlg.pushButton_path_2.show()
            self.dlg.pushButton_animation.show()
            
        def elevation_profile():
            os.system(f"eog {plugin_dir}/elevation_profile.png")

            # os.system(f"eog "+plugin_dir+"/elevation_profile.png")

        def cesium():
            run_server = 'gnome-terminal --title="cesium_server" --command="bash -c \'cd /home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/raster_path/; python3 -m http.server 3000; $SHELL\'"'
            os.system(run_server)
            os.system("/opt/google/chrome/chrome http://127.0.0.1:3000/index.html")

        def animation():
            directory = plugin_dir+"/animationcsv"

            def load_and_configure(filename):
                path = os.path.join(directory, filename)
                uri = 'file:///' + path + "?type=csv&escape=&useHeader=No&detectTypes=yes"
                uri = uri + "&crs=EPSG:4326&xField=field_2&yField=field_3"
                vlayer = QgsVectorLayer(uri, filename, "delimitedtext")

                try:
                    symbol = QgsSvgMarkerSymbolLayer(plugin_dir+'/svg/transport/transport_bus_stop.svg')

                    symbol.setSize(9)
                    symbol.setFillColor(QColor('#3333cc'))

                    vlayer.renderer().symbol().changeSymbolLayer(0, symbol )
                    vlayer.triggerRepaint()
                    vlayer.startEditing()
                    
                except Exception as e4:
                    print('Error: ' + str(e4))

                QgsProject.instance().addMapLayer(vlayer)
                mode = QgsVectorLayerTemporalProperties.ModeFeatureDateTimeStartAndEndFromFields

                tprops = vlayer.temporalProperties()

                tprops.setStartField("field_1")
                tprops.setEndField("field_4")
                tprops.setMode(mode)
                tprops.setIsActive(True)

            for filename in os.listdir(directory):
                if filename.endswith(".csv"):
                    load_and_configure(filename)

            for i in self.iface.mainWindow().findChildren(QtWidgets.QDockWidget):
                if i.objectName() == 'Temporal Controller':
                    i.setVisible(True) 

        self.dlg.pushButton_animation.clicked.connect(animation)  
        self.dlg.pushButton_animation.setStyleSheet("color: green;font-size: 12pt; ") 

        self.dlg.pushButton_cesium.clicked.connect(cesium)  
        self.dlg.pushButton_cesium.setStyleSheet("color: blue;font-size: 12pt; ") 

        #self.dlg.pushButton_slope.clicked.connect(slope1)  
        #self.dlg.pushButton_reclassify.clicked.connect(reclassifytable) 
        self.dlg.pushButton_path.clicked.connect(line1) 
        self.dlg.pushButton_path_2.clicked.connect(elevation_profile)  
        self.dlg.pushButton_path_2.setStyleSheet("color: Maroon;font-size: 12pt; ") 
        # self.dlg.pushButton_slope.setStyleSheet("color: green;font-size: 12pt; ") 

        # self.dlg.pushButton_reclassify.setStyleSheet("color: green;font-size: 12pt; ") 
        # self.dlg.pushButton_reclassify.setToolTip('click')

        self.dlg.pushButton_path.setStyleSheet("color: green;font-size: 12pt; ") 
        self.dlg.pushButton_path.setToolTip('click for Find Shortest Path')
        self.dlg.label_title.setStyleSheet("color: Indigo; font-size: 13pt;") 
        #self.dlg.label_slope.setStyleSheet("color: brown; ") 
        #self.dlg.label_reclassify.setStyleSheet("color: brown; ") 
        self.dlg.label_path.setStyleSheet("color: brown; ") 
        self.dlg.label_info.setStyleSheet("color: Navy; ") 
        self.dlg.label.setStyleSheet("color: brown; ") 

        self.dlg.pushButton_cesium.setToolTip('click for Show Shortest path in 3D')
        self.dlg.pushButton_path_2.setToolTip('click for Show elevation profile')
        self.dlg.pushButton_animation.setToolTip('click for show Route Animation')

        # self.dlg.pushButton_cesium.setStyleSheet("QPushButton::hover"
        #              "{"
        #              "background-color : lightgreen;"
        #              "}")
        # self.dlg.label_reclassify.hide()
        # self.dlg.pushButton_reclassify.hide()

        #self.dlg.label_path.hide()
        #self.dlg.pushButton_path.hide()
        # self.dlg.pushButton_path_2.hide()
        # self.dlg.label_info.hide()
        
        # self.dlg.pushButton_cesium.hide()
        
        # self.dlg.pushButton_animation.hide()
        
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
