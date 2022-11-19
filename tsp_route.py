# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *
from .tsp_route_dialog import TspRouteDialog
import os.path

from PyQt5 import QtGui
from qgis.core import (
    QgsProject,QgsFeature,QgsPointXY,QgsGeometry,QgsSvgMarkerSymbolLayer,QgsField,QgsVectorDataProvider,
    QgsVectorLayer, QgsVectorLayer,QgsGeometryGeneratorSymbolLayer,QgsSymbol,QgsArrowSymbolLayer,QgsFillSymbol,QgsPalLayerSettings,QgsVectorLayerSimpleLabeling)
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog
from PyQt5.QtCore import *
from qgis import processing
import json

import numpy as np
import math

class TspRoute:
    layer1 = ''
    layer2 = ''
    layer11 = ''
    layer22 = ''
    

    filename = ''
    r_layer = ''
    lyr_list = []
    lastlayertime = ''
    lstId = 0
    addlayerpath = []
    field_name = []

    def __init__(self, iface):
       
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'TspRoute_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Tsp Route')

        self.first_start = None

    def tr(self, message):
        
        return QCoreApplication.translate('TspRoute', message)


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
            self.action = QAction(QIcon(icon_path),"TspRoute", self.iface.mainWindow())
            self.action.setObjectName( 'TspRoute' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"TspRoute", self.iface.mainWindow())
            self.action.setObjectName( 'TspRoute' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "TspRoute":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)
                
    def firstSeg(self,layer,angleval,height,velocity):
        layer.selectByExpression("\"AUTO\"=1")
        selection = layer.selectedFeatures()
        wkt = selection[0].geometry().asWkt()
        

        temp = QgsVectorLayer("Linestring?crs=EPSG:4326", 'first segment', "memory")

        #QgsProject.instance().addMapLayer(temp)
        temp.startEditing()
        geom = QgsGeometry()
        geom = QgsGeometry.fromWkt(wkt)
        feat = QgsFeature()
        feat.setGeometry(geom)
        temp.dataProvider().addFeatures([feat])
        temp.commitChanges()
        
        # thetaDeg =  np.sin(math.degrees(angleval))
        # thetaRad = np.sin(math.radians(angleval))
        
        thetaRad =  math.sin(angleval)
        thetaDeg = math.sin(math.radians(angleval))
        print(thetaDeg,thetaRad)

        climbLen = height/thetaDeg##meter

        print('climbing (AC): ',climbLen)

        projectLen = climbLen*np.cos(angleval)
        print('projected (BC): ',projectLen)

        projectLendeg = projectLen/111100###degree(4326)buffer

        print(projectLendeg)
        
        output1 = processing.run("native:interpolatepoint", 
            {'INPUT':temp,
            'DISTANCE':abs(float(projectLendeg)),
            'OUTPUT':'/home/bisag/interpoint.geojson'})

        temp1 = QgsVectorLayer(output1['OUTPUT'], "inter point", "ogr")
        
        temp_data = temp1.dataProvider()

        
        temp_data.addAttributes([QgsField("seq",QVariant.String),QgsField("angle",QVariant.String),QgsField("distance",QVariant.String),QgsField("velocity",QVariant.String),QgsField("reach_time",QVariant.String)])
        temp1.updateFields()
        
        temp1.startEditing()
        dist = abs(float(projectLen))/1000#(km)
        reach_t = dist/velocity##km/(km/h)

        attr = [str(1),str(angleval),str(abs(float(projectLen))),str(velocity),str(reach_t)]
                
        for feature in temp1.getFeatures():
            fid = feature.id()
            feature.setAttributes(attr)
            temp_data.addFeatures([feature])
        
        temp.updateFields()
            
        caps = temp_data.capabilities()
        feats = temp1.getFeatures()
        dfeats = []

        if caps & QgsVectorDataProvider.DeleteFeatures:
            for feat in feats:
                if not feat['seq']:
                    dfeats.append(feat.id())
            temp1.dataProvider().deleteFeatures(dfeats)
            temp1.triggerRepaint()
        
        temp1.commitChanges()

        QgsProject.instance().addMapLayer(temp1)
                
    def test_3(self,layer):
        sym = layer.renderer().symbol()#
        
        shape_sym = QgsGeometryGeneratorSymbolLayer.create({'outline_color': 'black', 'symbolType': '1'})
        shape_sym.setSymbolType(QgsSymbol.Line)
        
        arrow = QgsArrowSymbolLayer.create(
            {
                "arrow_width": "0.5",
                "head_length": "3",
                "head_thickness": "2",
                "head_type": "0",
                "arrow_type": "0",
                "is_curved": "1",
                "arrow_start_width": "0.3"
            }
        )
        
        shape_sym.subSymbol().changeSymbolLayer(0, arrow) 
        #layer.triggerRepaint()

        sym.changeSymbolLayer(0, shape_sym)
        
        layer_settings  = QgsPalLayerSettings()#
        layer_settings.fieldName = "AUTO"
        layer_settings.placement = 2
        layer_settings.enabled = True

        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        layer.setLabelsEnabled(True)
        layer.setLabeling(layer_settings)
        layer.triggerRepaint()
        layer.startEditing()
        layer.triggerRepaint()
        layer.commitChanges()
        
    def startPoint(self,layer):#
        plugin_dir = os.path.dirname(__file__)
        
        layer.selectByExpression("\"seq\"=0")
        selection = layer.selectedFeatures()


        geom = selection[0].geometry().asWkt()
        x ,y = geom.replace('Point (','').replace(')','').split(' ')
        

        vl = QgsVectorLayer("Point", "start", "memory")
        pr = vl.dataProvider()
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(x) ,float(y))))
        pr.addFeatures([fet])
        vl.updateExtents()

        symbol = vl.renderer().symbol()
        svgStyle = {}
        svgStyle['fill'] = '#000000'
        svgStyle['name'] = f'{plugin_dir}{os.sep}red-marker.svg'
        svgStyle['outline'] = '#000000'
        svgStyle['outline-width'] = '0.3'
        svgStyle['size'] = '10'

        symbol_layer = QgsSvgMarkerSymbolLayer.create(svgStyle)
        symbol.changeSymbolLayer(0, symbol_layer)
        vl.triggerRepaint()

        QgsProject.instance().addMapLayer(vl)

    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            self.dlg = TspRouteDialog()
            
        plugin_dir = os.path.dirname(__file__)
        self.dlg.label_logo.setPixmap(QtGui.QPixmap(plugin_dir+os.sep+'BISAG-N_MeitY.jpg').scaledToWidth(120))
        
        layer_canvas = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        self.dlg.comboBox.addItems(layer_canvas)
        
        def selectinput():
            self.layer1, _filter = QFileDialog.getOpenFileName(self.dlg, "Select existing layer for input  ","", ' *.shp *.gpkg *.geojson')
            self.layer11 = QgsVectorLayer(self.layer1, "input layer", "ogr")
            self.dlg.comboBox.insertItem(0, "input layer")
            self.dlg.comboBox.setCurrentText("input layer")
            
            fieldname = [field.name() for field in self.layer11.fields()]

            QgsProject.instance().addMapLayer(self.layer11)
        
        def tsp():
            
            attid ='Sno'#serial no
            attSeq = 'seq'#seq field
            attSensor = 'Sensor'
            attSector = 'Sector'
            atttime = 'DT'#dwelltime(hour)
            attGNAME= "GNAME"
            attlen = "seg_length(km)"
            attVelocity = 'velocity'
            

            velocity = float(self.dlg.lineEdit.text()) #(km/h)
            angleval = float(self.dlg.lineEdit_2.text()) #(deg)
            height = float(self.dlg.lineEdit_3.text()) #(m)
            
            Endu = 8 #hour (capacity of fly plane)
            
            opsave ='output'

            optimal_path = os.path.join(plugin_dir,opsave,'output_loc.geojson')

            ls = QgsProject.instance().layerStore()
            r_layer = ls.mapLayersByName(self.dlg.comboBox.currentText())[0]
            
            input_path = r_layer.dataProvider().dataSourceUri()
            
            os.system(f"python3 {plugin_dir}/tsp.py {plugin_dir} {input_path} ")
            
            output_path = os.path.join(plugin_dir,opsave,'sequence.geojson')

            optimal_path = os.path.join(plugin_dir,opsave,'output_loc.geojson')
            
            
            lay = QgsVectorLayer(output_path, "sequence", "ogr")

            QgsProject.instance().addMapLayer(lay)
            self.startPoint(lay)
            
            resalgo = processing.run("qgis:pointstopath",#create path
                                                    {'INPUT':output_path,
                                                    'CLOSE_PATH':True,
                                                    'ORDER_FIELD':attSeq,
                                                    'GROUP_FIELD':'',
                                                    'DATE_FORMAT':'',
                                                    'OUTPUT':'TEMPORARY_OUTPUT'})

                
            resalgo1 = processing.run("native:explodelines",##single part to multipart (line segement)
                            {'INPUT':resalgo['OUTPUT'],
                            'OUTPUT':'TEMPORARY_OUTPUT'})

            opres = processing.run("native:addautoincrementalfield", {'INPUT':resalgo1['OUTPUT'],
                                                                'FIELD_NAME':'AUTO',
                                                                'START':1,
                                                                'GROUP_FIELDS':[],'SORT_EXPRESSION':'','SORT_ASCENDING':True,'SORT_NULLS_FIRST':False,
                                                                'OUTPUT':os.path.join(plugin_dir,opsave,'segmentlineId_loc.geojson')})

            ###add information of point to line segment (path) 
            with open(output_path) as f:#read sequence data
                data = json.load(f)
                
            idList,seqList ,timelist,attSensorList,attSectorList,attGNAMEList = [],[],[],[],[],[]

            for feature in data['features']:
                id = feature['properties'][attid]
                seq = feature['properties'][attSeq]
                timeval = feature['properties'][atttime]
                sen = feature['properties'][attSensor]
                sec = feature['properties'][attSector]
                gn = feature['properties'][attGNAME]
                
                idList.append(id)
                seqList.append(seq)
                timelist.append(timeval)
                attSensorList.append(sen)
                attSectorList.append(sec)
                attGNAMEList.append(gn)
                
                
            idtime = {idList[i]: timelist[i] for i in range(len(idList))}
            idsen = {idList[i]: attSensorList[i] for i in range(len(idList))}
            idsec = {idList[i]: attSectorList[i] for i in range(len(idList))}
            idgname = {idList[i]: attGNAMEList[i] for i in range(len(idList))}
            print(seqList)

            latlong2 = [idList[i]for i in seqList]

            res = list(zip(latlong2, latlong2[1:] + latlong2[:1]))#id and seq

            with open(opres['OUTPUT']) as f:##add id to line segment
                data = json.load(f)
                
            z = 0
            for feature in data['features']:
                feature['properties']['fromto']=str(res[z])
                feature['properties'][atttime]=idtime[res[z][0]]
                feature['properties'][attSensor]=idsen[res[z][0]]
                feature['properties'][attSector]=idsec[res[z][0]]
                feature['properties'][attGNAME]=idgname[res[z][0]]
                feature['properties']['begin']=str(res[z][0])
                feature['properties']['end']=str(res[z][1])
                
                z = z+1
                
            with open(optimal_path, 'w+') as f:
                json.dump(data, f, indent=2)
                

            out = processing.run("native:fieldcalculator", {'INPUT':optimal_path,# ##find length feature
                                                        'FIELD_NAME':attlen,
                                                        'FIELD_TYPE':0,
                                                        'FIELD_LENGTH':0,
                                                        'FIELD_PRECISION':0,
                                                        'FORMULA':' round($length /1000,3)',
                                                        'OUTPUT':'TEMPORARY_OUTPUT'})
            
            output = processing.run("native:fieldcalculator", {'INPUT':out['OUTPUT'],
                                                      'FIELD_NAME':attVelocity,#'velocity',
                                                      'FIELD_TYPE':0,#float
                                                      'FIELD_LENGTH':0,
                                                      'FIELD_PRECISION':0,
                                                      'FORMULA':f'{velocity}',
                                                      'OUTPUT':'TEMPORARY_OUTPUT'})
                                                    
            output1 = processing.run("native:fieldcalculator", {'INPUT':output['OUTPUT'],# ##find reach time feature
                                                        'FIELD_NAME':'reach_time',
                                                        'FIELD_TYPE':0,
                                                        'FIELD_LENGTH':0,
                                                        'FIELD_PRECISION':0,
                                                        'FORMULA':f'round(\"{attlen}\" /{velocity},3)',
                                                        'OUTPUT':os.path.join(plugin_dir,opsave,'result.geojson')})
            
            layer11 = QgsVectorLayer(output1['OUTPUT'], "optimal path", "ogr")

            QgsProject.instance().addMapLayer(layer11)
            
            self.test_3(layer11)
            
            self.firstSeg(layer11,angleval,height,velocity)

            with open(output1['OUTPUT']) as f:##add id to line segment
                data = json.load(f)
                
            rech_t,dtime = [],[]
            for feature in data['features']:
                r=feature['properties']['reach_time']
                d =feature['properties'][atttime]
                rech_t.append(float(0.0 if r is None else r))
                dtime.append(float(0.0 if d is None else d))#value nonetype so error
                
            overalltime = sum(rech_t)+sum(dtime)

            if overalltime>24:
                pass
           
        
        self.dlg.pushButton_select.clicked.connect(selectinput)
        self.dlg.pushButton.clicked.connect(tsp)
        
        
        self.dlg.pushButton_select.setToolTip('brows layer')
        self.dlg.pushButton.setToolTip('find optimal route')
        
        
        self.dlg.pushButton_select.setStyleSheet("color: green;")
        self.dlg.pushButton.setStyleSheet("color: green;")
        
        
        self.dlg.label.setStyleSheet("color: brown;")
        self.dlg.label_2.setStyleSheet("color: brown;")
        
        self.dlg.label_4.setStyleSheet("color: brown;")
        self.dlg.label_5.setStyleSheet("color: brown;")
        
        self.dlg.label_7.setStyleSheet("color: purple;")
        self.dlg.label_3.setStyleSheet("color: purple;")

        self.dlg.show()
        self.dlg.exec_()
        