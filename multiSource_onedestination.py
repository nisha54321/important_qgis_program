# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *
from .multiSource_onedestination_dialog import MultiSourceOnedestinationDialog
import os.path
from PyQt5.QtWidgets import QMenu, QAction
from qgis.gui import QgsMapToolEmitPoint
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import (
    QgsProject,QgsCoordinateReferenceSystem,QgsRasterLayer,QgsFeature,QgsVectorFileWriter,QgsPoint,QgsPointXY,QgsField,QgsPalLayerSettings,QgsVectorLayerSimpleLabeling,
    QgsVectorLayer,QgsGeometry,QgsTextFormat,QgsRaster,QgsProcessingFeatureSourceDefinition,QgsFeatureRequest,QgsRasterLayer,QgsVectorFileWriter,QgsProject,QgsVectorLayer, QgsVectorLayer,QgsCoordinateReferenceSystem,QgsFeature,QgsGeometry,QgsPointXY,QgsField,QgsPalLayerSettings,QgsVectorLayerSimpleLabeling
)
from osgeo import ogr, osr
from json import dumps
import shapefile
import time
from qgis.core import *

from qgis import processing
from PyQt5 import  QtGui
from PyQt5.QtWidgets import QMenu, QAction
import shutil
from osgeo import ogr
import os
from collections import defaultdict
from itertools import chain
import operator
import shapefile
from json import dumps
from qgis import processing
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time

class MultiSourceOnedestination:
    iii = 0
    vl =''
    vld =''
    vl2 =''
    xy1 = []
    xy2 = []
    xy = []
    xyd = []
    vlayer1 = ''
    mbselect = ''
    sel1 = []
    vis = ''
    pth =[]

    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MultiSourceOnedestination_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&MultiSource Onedestination')

        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('MultiSourceOnedestination', message)


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

        icon_path = ':/plugins/multiSource_onedestination/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'path for MultiSource Onedestination'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&MultiSource Onedestination'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = MultiSourceOnedestinationDialog()
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+'/'+'bisag_n.png').scaledToWidth(120))
        
        cwd = '/home/bisag/Music/webMobility'

        ########dynamic grid
        grd = cwd+'/geojson/mobility_grid_geojson'
        g =[]
        for root, dirs, files in os.walk(grd):
                for file in files:
                    if file.endswith(".geojson") and file.startswith("Mobility_Grid"):
                        g.append(os.path.join(root, file))
                        #os.remove(os.path.join(root, file))
    
        m =processing.run("native:mergevectorlayers", 
                    {'LAYERS':g,
                    'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                    'OUTPUT':grd+'/mergegrid.geojson'})
                    
        grid = processing.run("native:addautoincrementalfield", 
                    {'INPUT':m['OUTPUT'],
                    'FIELD_NAME':'id',
                    'START':1,
                    'GROUP_FIELDS':[],
                    'SORT_EXPRESSION':'',
                    'SORT_ASCENDING':True,
                    'SORT_NULLS_FIRST':False,
                    'OUTPUT':grd+'/grid.geojson'})
        #####3
    
        log1 = open(cwd+'/log.txt','a')
        log1.write("\n\n\n")
        log1.write("start plugin:or refresh plugin")
        log1.close()

        if(self.iii == 0):
            
            self.vl = QgsVectorLayer("Point?crs=EPSG:4326", "source", "memory")
            self.vld = QgsVectorLayer("Point?crs=EPSG:4326", "Destination", "memory")

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

            ##################33'/home/bisagn/Downloads/grid.geojson'
            #self.vlayer1 = QgsVectorLayer(grid['OUTPUT'], "select Grid", "ogr")
            self.vlayer1 = QgsVectorLayer('/home/bisag/Downloads/grid.geojson', "select Grid", "ogr")

            single_symbol_renderer = self.vlayer1.renderer()####holo (outerline black symbology)
            symbol = single_symbol_renderer.symbol()
            symbol.setColor(QColor("transparent"))
            symbol.symbolLayer(0).setStrokeColor(QColor("black"))   # change the stroke colour (Fails)
            symbol.symbolLayer(0).setStrokeWidth(2)   # change the stroke colour (Fails)

            self.vlayer1.triggerRepaint()
            self.vlayer1.commitChanges()
            QgsProject.instance().addMapLayer(self.vlayer1)

            
            self.vis = QgsVectorLayer("Point?crs=EPSG:4326", "visibility Analysis", "memory")

            self.iii = 1

        #set active layer grid
        self.vlayer1.removeSelection()###remove selection
        self.iface.actionSelect().trigger()############enable select tools

        sg = QgsProject.instance().mapLayersByName('select Grid')[0]
        self.iface.setActiveLayer(sg)

        ###click point:
        s= "source"
        d= "destination"


        def display_point1( pointTool ):
             
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))

            xy = str(coorx)+','+str(coory)
            self.xy.append(xy)
            #self.xy.append(coory)

            self.vl.renderer().symbol().setColor(QColor("blue"))
            self.vl.renderer().symbol().setSize(4)

            self.vl.triggerRepaint()

            f = QgsFeature()#QgsPointXY,QgsField,QgsPalLayerSettings,QgsVectorLayerSimpleLabeling
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx, coory)))
            pr = self.vl.dataProvider()

            #Add Attribute
            self.vl.startEditing()
            pr.addAttributes([QgsField("point_label", QVariant.String)])

            attvalAdd = [s]
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

            text_format = QgsTextFormat()
            text_format.setFont(QFont("MS Shell Dlg 2"))
            text_format.setSize(10.0)
            text_format.setColor(QColor("red"))
            text_format.setFont(QFont("MS Shell Dlg 2",10,QFont.Bold))
            layer_settings.setFormat(text_format)

            layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
            self.vl.setLabelsEnabled(True)
            self.vl.setLabeling(layer_settings)
            self.vl.triggerRepaint()
            self.vl.startEditing()
            self.vl.triggerRepaint()
            self.vl.commitChanges()

        def display_point2( pointTool ): 
            coorx = float('{}'.format(pointTool[0]))
            coory = float('{}'.format(pointTool[1]))

            xy = str(coorx)+','+str(coory)
            self.xyd.append(xy)

            
            self.vld.renderer().symbol().setColor(QColor("gray"))
            self.vld.renderer().symbol().setSize(4)

            self.vld.triggerRepaint()

            f = QgsFeature()#QgsPointXY,QgsField,QgsPalLayerSettings,QgsVectorLayerSimpleLabeling
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coorx, coory)))
            pr = self.vld.dataProvider()

            #Add Attribute
            self.vld.startEditing()
            pr.addAttributes([QgsField("point_label", QVariant.String)])

            attvalAdd = [d]
            f.setAttributes(attvalAdd)
            self.vld.triggerRepaint()

            pr.addFeature(f)
            self.vld.updateExtents() 
            self.vld.updateFields() 
            QgsProject.instance().addMapLayers([self.vld])

            #set label
            layer_settings  = QgsPalLayerSettings()
            layer_settings.fieldName = "point_label"
            layer_settings.placement = 2
            layer_settings.enabled = True

            text_format = QgsTextFormat()
            text_format.setFont(QFont("MS Shell Dlg 2"))
            text_format.setSize(10.0)
            text_format.setColor(QColor("red"))
            text_format.setFont(QFont("MS Shell Dlg 2",10,QFont.Bold))
            layer_settings.setFormat(text_format)

            layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
            self.vld.setLabelsEnabled(True)
            self.vld.setLabeling(layer_settings)
            self.vld.triggerRepaint()
            self.vld.startEditing()
            self.vld.triggerRepaint()
            self.vld.commitChanges()

        canvas = self.iface.mapCanvas()   
        pointTool = QgsMapToolEmitPoint(canvas)
        cwd = '/home/bisag/Music/webMobility'
        loc = cwd+'/geojson/multisource'
        def mobility():
            log1 = open(cwd+'log.txt','a')
            extractFet = processing.run("native:saveselectedfeatures",
            # 
                        #{'INPUT':grid['OUTPUT'],
                        {'INPUT':'/home/bisag/Downloads/grid.geojson',

                        'OUTPUT':loc+'/selectFeat.shp'})

            temp = QgsVectorLayer(extractFet["OUTPUT"], "selectSaveGrid", "ogr")

            single_symbol_renderer = temp.renderer()####holo (outerline black symbology)
            symbol = single_symbol_renderer.symbol()
            symbol.setColor(QColor("transparent"))
            symbol.symbolLayer(0).setStrokeColor(QColor("black"))   # change the stroke colour (Fails)
            symbol.symbolLayer(0).setStrokeWidth(1.5)   # change the stroke colour (Fails)

            temp.triggerRepaint()
            temp.commitChanges()
            QgsProject.instance().addMapLayer(temp)
            QgsProject.instance().layerTreeRoot().findLayer(temp.id()).setItemVisibilityChecked(False)

            ex = temp.extent()
            xmax = str(ex.xMaximum())
            ymax = str(ex.yMaximum())
            xmin = str(ex.xMinimum())
            ymin = str(ex.yMinimum())
            ex1 = xmax+','+xmin+','+ymax+','+ymin+' [EPSG:4326]'
            #print(ex1)
            log1.write("extend is:"+str(ex1))
            
            ####clip dataset:

            wktfix = processing.run("native:fixgeometries",
                         {'INPUT':cwd+'/mobility_wkt1.geojson',
                         'OUTPUT':cwd+'/new/mobility_wkt1.geojson'})

            clip1 = processing.run("native:clip",
                            {'INPUT':wktfix['OUTPUT'],
                            'OVERLAY':temp,
                            'OUTPUT':loc+'/clip.shp'})

            temp1 = QgsVectorLayer(clip1['OUTPUT'], "clip", "ogr")
            single_symbol_renderer = temp1.renderer()
            symbol = single_symbol_renderer.symbol()
            symbol.setColor(QColor("black"))
            symbol.symbolLayer(0).setStrokeColor(QColor("black"))   # change the stroke colour (Fails)
            temp1.commitChanges()
            temp1.triggerRepaint()

            res3 = processing.run("native:rasterize",
                     {'EXTENT':ex1,
                        'EXTENT_BUFFER':0,
                        'TILE_SIZE':1024,
                        'MAP_UNITS_PER_PIXEL':0.00009,
                        'MAKE_BACKGROUND_TRANSPARENT':False,
                        'MAP_THEME':None,
                        'LAYERS':[temp1,temp],
                        'OUTPUT':plugin_dir+'/output/convertMapRaster.tif'})

            res4 = processing.run("gdal:cliprasterbyextent", 
                        {'INPUT':res3['OUTPUT'],
                        'PROJWIN':ex1,
                        'NODATA':None,
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'EXTRA':'',
                        'OUTPUT':plugin_dir+'/output/convertMapRasterClip.tif'})

            rasterize = QgsRasterLayer(res4['OUTPUT'], "rasterize")
            # QgsProject.instance().addMapLayer(rasterize)
            # QgsProject.instance().layerTreeRoot().findLayer(rasterize.id()).setItemVisibilityChecked(False)

            # res5 = processing.run("gdal:cliprasterbymasklayer", {'INPUT':res4['OUTPUT'],
            #         'MASK':QgsProcessingFeatureSourceDefinition('/home/bisagn/Downloads/grid.geojson',
            #          selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),'SOURCE_CRS':None,'TARGET_CRS':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':'','DATA_TYPE':0,'EXTRA':'',
            #     'OUTPUT':plugin_dir+'/output/clipped2.tif'})

            processing.run("gdal:rearrange_bands",
                        {'INPUT':res4['OUTPUT'],
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

            rasterize = QgsRasterLayer(reclass['OUTPUT'], "reclass")
            QgsProject.instance().addMapLayer(rasterize)

            print("succees:")
            log1.write("succees run background algorithm is:")
            log1.close()

            
   
        self.dlg.pushButton_select.clicked.connect(mobility)  


        def clicksource():##source
            pointTool.canvasClicked.connect( display_point1 )
            canvas.setMapTool( pointTool )

        self.dlg.pushButton_s.clicked.connect(clicksource) 

        def clickdestination():##destination
            pointTool.canvasClicked.connect( display_point2 )
            canvas.setMapTool( pointTool )

        self.dlg.pushButton_d.clicked.connect(clickdestination) 

        def tankrun():
            print('source:',self.xy)
            print('destination:',self.xyd)
            for k1 in self.xyd:
                self.xy.remove(k1)
            coord = []    
            for i in self.xy:
                i = i.split(',')
                j = self.xyd[-1]
                j = j.split(',')
                k = i[0]+','+i[1]+','+j[0]+','+j[1]
                coord.append(k)
            #print(coord)
            p1 = 1
            for y in coord:
                y = y.split(",")
                xy = [float(i) for i in y]
                #print(type(xy),xy[-4])
                print(xy)

                ################
                os.system(f"python3 {plugin_dir}/shortest_path.py {xy[-4]} {xy[-3]} {xy[-2]} {xy[-1]}")#####3change shortest_path.py (input = plugin_dir+'/recassify1.tif')

                ############convert to geojson and shape file
                try:
                    f = open(plugin_dir+"/path.txt", "r")
                    x = f.read()
                    f.close()

                    wkt2 = x.split("\n")
                    wkt2 = [i for i in wkt2 if i]#remove empty string

                    spatialref = osr.SpatialReference()
                    spatialref.ImportFromProj4('+proj=longlat +datum=WGS84 +no_defs')

                    driver = ogr.GetDriverByName("ESRI Shapefile")
                    c= 1
                    for wktval in wkt2:

                        ###################convert shp
                        input_folder = plugin_dir+"/shapefile/line{}_{}.shp".format(str(p1),str(c))

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

                            print("length is (m):",len1)
                            log1.write("length is (m):"+str(len1))

                        except Exception as e:
                            print(e)

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
                            except Exception as e:
                                print(e)
                        for sr in reader.shapeRecords():
                            atr = dict(zip(field_names, sr.record))
                            try:
                                geom = sr.shape.__geo_interface__
                                if geom['type'] == 'LineString':
                                    atr['length_(m)'] = round(len1, 2)

                                line.append(dict(type="Feature", \
                                geometry=geom, properties=atr)) 
                            except Exception as e:
                                print(e)

                        # write the GeoJSON file
                        #op = plugin_dir+'/geojson'
                        op = cwd+'/geojson/multisource'
                        print(op+"/line{}_{}.geojson".format(str(p1),str(c)))
                        geojson11 = open(op+"/line{}_{}.geojson".format(str(p1),str(c)), "w")
                        geojson11.write(dumps({"type": "FeatureCollection", "features": line}, indent=2) + "\n")
                        geojson11.close()

                        temp = QgsVectorLayer(op+"/line{}_{}.geojson".format(str(p1),str(c)), f"line{p1}_{c}", "ogr")
                        QtGui.QColor(255, 0, 0)#(pink:209, 31, 150),(green:40, 156, 22),(navyBlue:22, 53, 156)
                        ##symbol.setColor(QtGui.QColor(1, 111, 0)) please set color

                        single_symbol_renderer = temp.renderer()
                        symbol = single_symbol_renderer.symbol()
                        symbol.setWidth(1.08)

                        #add maptips(mouse hover)
                        expression = """[%  @layer_name  %]"""
                        temp.setMapTipTemplate(expression)
                        QgsProject.instance().addMapLayer(temp)#

                        #buffer1()#find the buffer of shortest path(500 meter)
                        # processing.run("native:buffer", 
                        #             {'INPUT':input_folder,
                        #             'DISTANCE':0.0021,
                        #             'SEGMENTS':5,
                        #             'END_CAP_STYLE':0,
                        #             'JOIN_STYLE':0,
                        #             'MITER_LIMIT':2,
                        #             'DISSOLVE':False,
                        #             'OUTPUT':plugin_dir+"/buffer"+'/buffer{}.shp'.format(str(c))})
                    ########################
                        c = c+1

                except Exception as e:
                    print(e)
                p1 = p1 +1


        self.dlg.pushButton.clicked.connect(tankrun) 

        

        ######style 
        self.dlg.pushButton_select.setStyleSheet("color: green;") 
        self.dlg.pushButton_select.setToolTip('click')
        self.dlg.label_title.setStyleSheet("color: purple;font-size: 13pt;") 
        self.dlg.label_2.setStyleSheet("color: brown;") 
        self.dlg.label.setStyleSheet("color: brown;") 
        self.dlg.pushButton_s.setStyleSheet("color: green;") 
        self.dlg.pushButton_s.setToolTip('click')
        self.dlg.pushButton_d.setStyleSheet("color: green;") 
        self.dlg.pushButton_d.setToolTip('click')
        self.dlg.pushButton.setStyleSheet("color: green;") 
        self.dlg.pushButton.setToolTip('click')
        self.dlg.show()
        self.dlg.exec_()
        