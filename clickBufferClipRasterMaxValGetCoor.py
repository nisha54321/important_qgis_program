from qgis.gui import QgsMapToolEmitPoint
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox, QLabel, QToolTip, QPushButton
from PyQt5.QtGui import *
from PyQt5.QtCore import * 
from PyQt5 import QtGui
import numpy as np
from osgeo import gdal
import os
iii = 0
rasterLyr = QgsRasterLayer("/home/bisag/Documents/extractRaster/Badmer(DEM1)_09_16.tif","Sat Image")
lval = []
if(iii == 0):
    vpoly = QgsVectorLayer("Polygon?crs=EPSG:4326", "Buffer" , "memory")
    iii = 1
    
def display_point( pointTool ): 
    coorx = float('{}'.format(pointTool[0]))
    coory = float('{}'.format(pointTool[1]))
    
    x = coorx
    y = coory
    print(coorx,coory)
    
    f = QgsFeature()
    
    symbol1 = QgsSymbol.defaultSymbol(vpoly.geometryType())

    symbol = QgsSymbol.defaultSymbol(vpoly.geometryType())
    symbol.setColor(QColor("#c97653")) 
    symbol.symbolLayer(0).setBrushStyle(Qt.BrushStyle(Qt.FDiagPattern))
    symbol.symbolLayer(0).setStrokeColor(QColor("#f5c9c9"))

    vpoly.triggerRepaint()

    pr = vpoly.dataProvider()
    vpoly.startEditing()

    
    f = QgsFeature()

    vpoly.triggerRepaint()

    pr = vpoly.dataProvider()

    ##100 meter buffer create(pass radius)
    f.setGeometry( QgsGeometry.fromPointXY(QgsPointXY(x, y)).buffer(0.0005,7))
    pr.deleteAttributes
    vpoly.startEditing()
    pr.addFeatures( [f] )
    vpoly.commitChanges()
    
    #raster value fetch for click coordinates
    p = QgsPointXY(x,y)
    qry = rasterLyr.dataProvider().identify(p,QgsRaster.IdentifyFormatValue)
    qry.isValid()
    r2 = qry.results()
    val = r2[1]
    print("raster val: ",val)
    
    ###clip data with buffer layer
    
    clip_op ='/home/bisag/Documents/extractRaster/clipImage.tif'

    if os.path.exists(clip_op):
        os.remove(clip_op) 
        
    processing.run("gdal:cliprasterbymasklayer",
            {'INPUT':'/home/bisag/Documents/extractRaster/Badmer(DEM1)_09_16.tif',
#            'MASK':'/home/bisag/Documents/extractRaster/buffer.shp|layername=buffer',
            'MASK':vpoly,

           'SOURCE_CRS':None,
            'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
            'NODATA':None,
            'ALPHA_BAND':False,
            'CROP_TO_CUTLINE':True,
            'KEEP_RESOLUTION':False,
            'SET_RESOLUTION':False,
            'X_RESOLUTION':None,
            'Y_RESOLUTION':None,
            'MULTITHREADING':False,
            'OPTIONS':'',
            'DATA_TYPE':0,
            'EXTRA':'',
            'OUTPUT':clip_op})
        
    #add layer into qgis mapcanvas
    clip = QgsRasterLayer(clip_op,"clipImage")
    QgsProject.instance().addMapLayer(clip)
    QgsProject.instance().addMapLayer(vpoly)

    #save layer
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "ESRI Shapefile"
    save_options.fileEncoding = "UTF-8"
    transform_context = QgsProject.instance().transformContext()
    error = QgsVectorFileWriter.writeAsVectorFormatV2(vpoly,
                                                  "/home/bisag/Documents/extractRaster/Buffer100m.shp",
                                                  transform_context,
                                                  save_options)


    ######################=======find max value of raster image and get coordinates
    # Open raster file, and get GeoTransform
    rast_src = gdal.Open(clip_op)
    rast_gt = rast_src.GetGeoTransform()

    def get_xy(r, c):
        x0, dx, rx, y0, ry, dy = rast_gt
        return(x0 + r*dx + dx/2.0, y0 + c*dy + dy/2.0)

    # Get first raster band
    rast_band = rast_src.GetRasterBand(1)

    # Retrieve as NumPy array to do the serious work
    rast = rast_band.ReadAsArray()

    # Sort raster pixels from highest to lowest
    sorted_ind = rast.argsort(axis=None)[::-1]
    # Show highest top 10 values
    for ind in sorted_ind[:1]:
        # Get row, column for index
        r, c = np.unravel_index(ind, rast.shape)
        
        # Get [projected] X and Y coordinates
        x, y = get_xy(r, c)
        max = rast[r, c]
        
        print("max : ",max)
        print("coordinate : ",x,y)
        
    iface.actionPan().trigger()
    
canvas = iface.mapCanvas() 
pointTool = QgsMapToolEmitPoint(canvas)
pointTool.canvasClicked.connect( display_point )
canvas.setMapTool( pointTool )

