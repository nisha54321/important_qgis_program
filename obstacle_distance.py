# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .resources import *
from .obstacle_distance_dialog import ObstacleDistanceDialog
import os.path
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from qgis.gui import QgsMapToolEmitPoint
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,QgsRasterLayer,QgsPoint,QgsFeature,QgsVectorFileWriter,QgsPointXY,QgsField,QgsPalLayerSettings,QgsVectorLayerSimpleLabeling,
    QgsPathResolver,QgsVectorLayer,QgsGeometry
)
from qgis.core import ( QgsApplication,QgsProject,QgsVectorLayer, QgsVectorLayer,QgsCoordinateReferenceSystem,QgsProcessingFeatureSourceDefinition,QgsFeatureRequest)
from osgeo import ogr, osr
from json import dumps
import sys
import shapefile
import time
from qgis.core import *

from qgis import processing
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QCheckBox, QListView, QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QCheckBox
import shutil

class ObstacleDistance:
    iii = 0
    vl =''
    xy1 = []
    xy = []
    def __init__(self, iface):
       
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ObstacleDistance_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&ObstacleDistance')

        self.first_start = None

    def tr(self, message):
        
        return QCoreApplication.translate('ObstacleDistance', message)


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
        icon_path = plugin_dir+'/'+'bisag_n.png'

        self.menu = self.iface.mainWindow().findChild( QMenu, '&Algorithm' )

        if not self.menu:
            self.menu = QMenu( '&Algorithm', self.iface.mainWindow().menuBar() )
            self.menu.setObjectName( '&Algorithm' )
            actions = self.iface.mainWindow().menuBar().actions()
            lastAction = actions[-1]
            self.iface.mainWindow().menuBar().insertMenu( lastAction, self.menu )
            self.action = QAction(QIcon(icon_path),"ObstacleDistance", self.iface.mainWindow())
            self.action.setObjectName( 'ObstacleDistance' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"ObstacleDistance", self.iface.mainWindow())
            self.action.setObjectName( 'ObstacleDistance' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        
        # for action in self.actions:
        #     print(action)
        #     self.iface.removePluginMenu(self.tr(u'&ObstacleDistance'),self.menu.menuAction())
        #     self.iface.removeToolBarIcon(action)
        menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "ObstacleDistance":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)

    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = ObstacleDistanceDialog()
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))
        #remove all files
        mypath1 = plugin_dir+"/shapefile/"
        mypath2 = plugin_dir+"/buffer/"
        mypath3 = plugin_dir+"/output/"
        mypath4 =plugin_dir+"/distance/"

        l = [mypath1,mypath2,mypath3,mypath4]
        for delfol in l:
            #print(delfol)
            for root, dirs, files in os.walk(delfol):
                for file in files:
                    os.remove(os.path.join(root, file))

        mypath11 = plugin_dir+"/geojson/"
        for root, dirs, files in os.walk(mypath11):
                for file in files:
                    if file.endswith(".geojson"):
                        os.remove(os.path.join(root, file))

        plugin_dir = os.path.dirname(__file__)
        if(self.iii == 0):
            self.vl = QgsVectorLayer("Point?crs=EPSG:4326", "markpoint", "memory")
            vlayer = QgsVectorLayer(plugin_dir+'/grid.shp', "select Grid", "ogr")
            QgsProject.instance().addMapLayer(vlayer)

            self.iii = 1
        # for feature in layer.selectedFeatures():
        #     print(feature['id'])
        #iface.actionZoomToSelected().trigger() 
        point_label = iter(["source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination","source", "destination"])

        def display_point1( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))
            print("shortest path \n",coorx, coory)
            self.xy.append(coorx)
            self.xy.append(coory)
            self.vl.renderer().symbol().setColor(QColor("red"))
            self.vl.renderer().symbol().setSize(4)

            self.vl.triggerRepaint()

            f = QgsFeature()#QgsPointXY,QgsField,QgsPalLayerSettings,QgsVectorLayerSimpleLabeling
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

        canvas = self.iface.mapCanvas()   
        pointTool = QgsMapToolEmitPoint(canvas)
        
        def mobility():
            
            res = processing.run("gdal:clipvectorbypolygon", 

                        {'INPUT':plugin_dir+'/mobility_wkt1.geojson',
                        'MASK':QgsProcessingFeatureSourceDefinition(plugin_dir+'/grid.shp', 
                        selectedFeaturesOnly=True,
                        featureLimit=-1,
                        geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                        'OPTIONS':'',
                        'OUTPUT':plugin_dir+'/mobility_wkt2.geojson'
                        })

            ############background run algorithm
            temp = QgsVectorLayer(res["OUTPUT"], "Wkt polygon", "ogr")
            QgsProject.instance().addMapLayer(temp)


            ex = temp.extent()
            xmax = str(ex.xMaximum())
            ymax = str(ex.yMaximum())
            xmin = str(ex.xMinimum())
            ymin = str(ex.yMinimum())
            ex1 = xmax+','+xmin+','+ymax+','+ymin+' [EPSG:4326]'

            print(ex1)

            # temp = QgsVectorLayer("MultiPolygon?crs=EPSG:4326", "Wkt polygon", "memory")
            ##border remove polygon
            single_symbol_renderer = temp.renderer()
            symbol = single_symbol_renderer.symbol()
            symbol.setColor(QColor.fromRgb(0,0,0))
            symbol.symbolLayer(0).setStrokeStyle(Qt.PenStyle(Qt.NoPen))

            temp.triggerRepaint()
            processing.run("native:rasterize",
                    {'EXTENT':ex1,
                    'EXTENT_BUFFER':0,
                    'TILE_SIZE':1024,
                    'MAP_UNITS_PER_PIXEL':0.00005,
                    'MAKE_BACKGROUND_TRANSPARENT':False,
                    'MAP_THEME':None,
                    'LAYERS':[temp],
                    'OUTPUT':plugin_dir+'/output/convertMapRaster.tif'})
                    
            processing.run("gdal:rearrange_bands",
                        {'INPUT':plugin_dir+'/output/convertMapRaster.tif',
                        'BANDS':[1],
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'OUTPUT':plugin_dir+'/output/singleband.tif'})
                        
            reclass = processing.run("native:reclassifybytable",
                        {'INPUT_RASTER':plugin_dir+'/output/singleband.tif',
                        'RASTER_BAND':1,
                        'TABLE':[0,38,1,38,255,2],
                        'NO_DATA':-9999,
                        'RANGE_BOUNDARIES':0,
                        'NODATA_FOR_MISSING':False,
                        'DATA_TYPE':5,
                        'OUTPUT':plugin_dir+'/recassify.tif'})
            print("succees:")
            

        self.dlg.pushButton_select.clicked.connect(mobility)  

        ##find elevation profile
        def elevation():
            os.system(f"python3 /home/bisag/Music/webMobility/elevation_profile.py")
            #os.system(f"eog /home/bisag/Music/webMobility/elevation_profile.png")

        def click1():
            pointTool.canvasClicked.connect( display_point1 )
            canvas.setMapTool( pointTool )

        self.dlg.pushButton_2.clicked.connect(click1)  


        def shortest_path():
           
            start = time.time()
            
            print(self.xy)
            os.system(f"python3 {plugin_dir}/shortest_path.py {self.xy[-4]} {self.xy[-3]} {self.xy[-2]} {self.xy[-1]}")#####3change shortest_path.py (input = plugin_dir+'/recassify1.tif')
            #lat_long_list.close()
            #elevation()

            ############convert to geojson and shape file
            f = open(plugin_dir+"/path.txt", "r")
            x = f.read()
            f.close()

            wkt = x.split("\n")
            wkt = [i for i in wkt if i]#remove empty string

            #print(len(wkt))

            spatialref = osr.SpatialReference()
            spatialref.ImportFromProj4('+proj=longlat +datum=WGS84 +no_defs')

            driver = ogr.GetDriverByName("ESRI Shapefile")
            c= 1

            for wktval in wkt:

                ###################convert shp
                input_folder = plugin_dir+"/shapefile/line{}.shp".format(str(c))

                dstfile = driver.CreateDataSource(input_folder)
                dstlayer = dstfile.CreateLayer("line", spatialref, geom_type=ogr.wkbLineString)
                fielddef = ogr.FieldDefn("ID", ogr.OFTInteger)
                fielddef.SetWidth(10)
                dstlayer.CreateField(fielddef)
                poly = ogr.CreateGeometryFromWkt(wktval)
                feature = ogr.Feature(dstlayer.GetLayerDefn())
                feature.SetGeometry(poly)
                feature.SetField("ID", 0)
                dstlayer.CreateFeature(feature)
                feature.Destroy()
                dstfile.Destroy()

                try:
                    from pyproj import Geod
                    from shapely import wkt

                    #in meter
                    line =wkt.loads(wktval)
                    geod = Geod(ellps="WGS84")

                    len1 = geod.geometry_length(line)

                    print("length is (meter):",len1)
                except Exception as e:
                    pass

                ##convert shape to geojson
                reader = shapefile.Reader(input_folder)
                fields = reader.fields[1:]
                field_names = [field[0] for field in fields]
                line = []

                for sr in reader.shapeRecords():
                    atr = dict(zip(field_names, sr.record))
                    try:
                        geom = sr.shape.__geo_interface__
                        line.append(dict(type="Feature", geometry=geom, properties=atr))
                    except:
                        pass 
                for sr in reader.shapeRecords():
                    atr = dict(zip(field_names, sr.record))
                    try:
                        geom = sr.shape.__geo_interface__
                        if geom['type'] == 'LineString':
                            atr['length_meter'] = len1

                        line.append(dict(type="Feature", \
                        geometry=geom, properties=atr)) 
                    except:
                        pass

                # write the GeoJSON file
                op = plugin_dir+'/geojson'

                geojson11 = open(op+"/line{}.geojson".format(str(c)), "w")
                geojson11.write(dumps({"type": "FeatureCollection", "features": line}, indent=2) + "\n")
                geojson11.close()

                #buffer1()#find the buffer of shortest path(500 meter)
                processing.run("native:buffer", 
                            {'INPUT':input_folder,
                            'DISTANCE':0.0021,
                            'SEGMENTS':5,
                            'END_CAP_STYLE':0,
                            'JOIN_STYLE':0,
                            'MITER_LIMIT':2,
                            'DISSOLVE':False,
                            'OUTPUT':plugin_dir+"/buffer"+'/buffer{}.shp'.format(str(c))})

                ##################distance between obstacles:
                mypath = plugin_dir+"/obstacleDis"
                point_dist = 0.005
                bfrDis1 = 0.05

                ##find buffer 0.005 rad
                bfr = processing.run("native:buffer", 
                {'INPUT':op+"/line{}.geojson".format(str(c)),
                'DISTANCE':bfrDis1,
                'SEGMENTS':5,
                'END_CAP_STYLE':0,
                'JOIN_STYLE':0,
                'MITER_LIMIT':2,
                'DISSOLVE':False,
                'OUTPUT':mypath+f'/buffer{c}.shp'})
                
                mlprt = processing.run("native:multiparttosingleparts", 
                            {'INPUT':plugin_dir+'/mobility_wkt1.geojson',
                            'OUTPUT':mypath+'/multipart_single.shp'})
                        
                dispoint = processing.run("native:pointsalonglines",
                        {'INPUT':op+"/line{}.geojson".format(str(c)),
                        'DISTANCE':point_dist,
                        'START_OFFSET':0,
                        'END_OFFSET':0,
                        'OUTPUT':mypath+f'/dis_point{c}.shp'})
                        
                ##for line segment point find
                segpoint = processing.run("native:extractvertices", 
                                {'INPUT':op+"/line{}.geojson".format(str(c)),
                                'OUTPUT':mypath+f'/segment_point{c}.shp'})
                                
                ##extract node specific value
                endpont = processing.run("native:extractspecificvertices", 
                            {'INPUT':op+"/line{}.geojson".format(str(c)),
                            'VERTICES':'-1',
                            'OUTPUT':mypath+f'/endPoint{c}.shp'})
                                
                points1 = processing.run("native:mergevectorlayers", 
                    {'LAYERS':[dispoint['OUTPUT'],endpont['OUTPUT']],
                    'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                    'OUTPUT':mypath+f'/points1_{c}.shp'})
                    
                points =processing.run("native:addautoincrementalfield", 
                            {'INPUT':points1['OUTPUT'],
                            'FIELD_NAME':'AUTO',
                            'START':1,
                            'GROUP_FIELDS':[],
                            'SORT_EXPRESSION':'',
                            'SORT_ASCENDING':True,
                            'SORT_NULLS_FIRST':False,
                            'OUTPUT':mypath+f'/points_{c}.shp'
                            })
                        
                ###createradiallines
                rl = processing.run("shapetools:createradiallines", 
                        {'INPUT':points['OUTPUT'],
                        'NumberOfLines':16,
                        'OuterRadius':2,
                        'InnerRadius':0,
                        'UnitsOfMeasure':0,
                        'ExportInputGeometry':False,
                        'OUTPUT':mypath+f'/radialline{c}.shp'})
                        
                srl1 = processing.run("native:multiparttosingleparts",
                                {'INPUT':rl['OUTPUT'],
                                'OUTPUT':mypath+f'/singlepartline1{c}.shp'})
                ####3
                clipObstacle =processing.run("native:clip", 
                            {'INPUT':mlprt['OUTPUT'],
                            'OVERLAY':bfr['OUTPUT'],
                            'OUTPUT':mypath+f'/clipObstacle{c}.shp'})   
                            
                it =processing.run("native:intersection",
                        {'INPUT':mlprt['OUTPUT'],
                        'OVERLAY':bfr['OUTPUT'],
                        'INPUT_FIELDS':[],
                        'OVERLAY_FIELDS':[],
                        'OVERLAY_FIELDS_PREFIX':'',
                        'OUTPUT':mypath+f'/intersection{c}.shp'
                        })
                        
                un1 =processing.run("native:union", 
                            {'INPUT':it['OUTPUT'],
                            'OVERLAY':bfr['OUTPUT'],
                            'OVERLAY_FIELDS_PREFIX':'',
                            'OUTPUT':mypath+f'/union{c}.shp'})  
                            
                vlayer = QgsVectorLayer(un1['OUTPUT'], "selected feature", "ogr")
                QgsProject.instance().addMapLayer(vlayer)

                #######for selected feature (union file)
                processing.run("qgis:selectbyattribute",
                        {'INPUT':un1['OUTPUT'],
                        'FIELD':'ID',
                        'OPERATOR':8,
                        'VALUE':'',
                        'METHOD':0}) 
                        
                vlayer = QgsVectorLayer(srl1['OUTPUT'], "selectbylocation(line)", "ogr")
                QgsProject.instance().addMapLayer(vlayer)

                sl1 =processing.run("native:selectbylocation",
                        {'INPUT':srl1['OUTPUT'],
                        'PREDICATE':[0],
                        'INTERSECT':it['OUTPUT'],
                        'METHOD':0}
                        )  
                        
                clip = processing.run("native:clip",
                    {'INPUT':QgsProcessingFeatureSourceDefinition(srl1['OUTPUT'],
                    selectedFeaturesOnly=True,
                    featureLimit=-1, 
                    geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                    'OVERLAY':QgsProcessingFeatureSourceDefinition(un1['OUTPUT'],
                    selectedFeaturesOnly=True,
                    featureLimit=-1,
                    geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                    'OUTPUT':mypath+'/clip{c}.shp'})
                        
                clipM_s = processing.run("native:multiparttosingleparts",
                                {'INPUT':clip['OUTPUT'],
                                'OUTPUT':mypath+f'/clipMulSingle{c}.shp'})
                ###   
                vlayer = QgsVectorLayer(clipM_s['OUTPUT'], "selectbylocation(clip)", "ogr")
                QgsProject.instance().addMapLayer(vlayer)

                selectLoc =processing.run("native:selectbylocation",
                        {'INPUT':clipM_s['OUTPUT'],
                        'PREDICATE':[0],
                        'INTERSECT':points['OUTPUT'],
                        'METHOD':0})

                                
                save = processing.run("native:saveselectedfeatures",
                        {'INPUT':vlayer,
                        'OUTPUT':mypath+f'/clipLine{c}.shp'})

                len = processing.run("native:fieldcalculator", 
                        {'INPUT':save['OUTPUT'],
                        'FIELD_NAME':'length',
                        'FIELD_TYPE':0,
                        'FIELD_LENGTH':0,
                        'FIELD_PRECISION':0,
                        'FORMULA':'round($length,2)',
                        'OUTPUT':mypath+f'/len{c}.shp'})
                        
                vlayer = QgsVectorLayer(len['OUTPUT'], "final(clip)", "ogr")
                QgsProject.instance().addMapLayer(vlayer)

                print("success")

                ##################end find distance

                reader = shapefile.Reader(len['OUTPUT'])
                fields = reader.fields[1:]
                field_names = [field[0] for field in fields]
                line = []
                for sr in reader.shapeRecords():
                    atr = dict(zip(field_names, sr.record))
                    try:
                        geom = sr.shape.__geo_interface__
                        line.append(dict(type="Feature", \
                        geometry=geom, properties=atr))
                    except:
                        pass 

                geojson11 = open(op+"/obstacle_len{}.geojson".format(str(c)), "w")
                geojson11.write(dumps({"type": "FeatureCollection", "features": line}, indent=2) + "\n")
                geojson11.close()
                print("success:find obstacles distance.")

                ##################end
                ###########create Buffer
                
                bshp = plugin_dir+"/buffer"+'/buffer{}.shp'.format(str(c))
                print("bfr:",bshp)

                reader = shapefile.Reader(plugin_dir+"/buffer"+'/buffer{}.shp'.format(str(c)))
                fields = reader.fields[1:]
                field_names = [field[0] for field in fields]
                buffer = []

                for sr in reader.shapeRecords():
                    try:
                        atr = dict(zip(field_names, sr.record))

                        atr['name2'] = "/Buffer_{}".format(str(c))
                        geom = sr.shape.__geo_interface__
                        buffer.append(dict(type="Feature", \
                        geometry=geom, properties=atr))
                    except:
                        pass
                
                # write the GeoJSON file
                geojson1 = open(op+"/Buffer_line{}.geojson".format(str(c)), "w")
                geojson1.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
                geojson1.close()

                
                ##clip Buffer
                clip = processing.run("native:clip", 
                    {'INPUT':plugin_dir+'/mobility_wkt1.geojson',
                    'OVERLAY':op+"/Buffer_line{}.geojson".format(str(c)),
                    'OUTPUT':plugin_dir+'/clipunion/'+"Buffer_clip{}.geojson".format(str(c))
                    }
                    )
                union = processing.run("native:union", 
                    {'INPUT':clip['OUTPUT'],
                    'OVERLAY':op+"/Buffer_line{}.geojson".format(str(c)),
                    'OVERLAY_FIELDS_PREFIX':'',
                    'OUTPUT':op+"/union_{}.geojson".format(str(c))})  

                ##add field 
                source = ogr.Open(union['OUTPUT'], update=True)
                layer = source.GetLayer()

                f3 = ogr.FieldDefn('name', ogr.OFTString)
                layer.CreateField(f3)

                f3 = ogr.FieldDefn('color', ogr.OFTString)
                layer.CreateField(f3)

                feature = None
                n = 0

                nm = ['wkt','Buffer','Buffer']
                clr = ["red","green","green"]
                for feature in layer:  
                    fid = feature.GetFID()

                    if id is not None:
                        feature.SetField("name", nm[n])
                        feature.SetField("color", clr[n])

                        layer.SetFeature(feature)
                    n =n+1
                source = None

                print("successs")
            

                c = c+1
            print(f'Generated 5 paths in {time.time() - start}s')
            ###################################end

        #
        self.dlg.pushButton.clicked.connect(shortest_path)  

        # self.dlg.pushButton_select.hide()
        # self.dlg.pushButton.hide()
        

        self.dlg.show()
        self.dlg.exec_()
        