from qgis.gui import QgsMapToolEmitPoint
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox, QLabel, QToolTip, QPushButton
from PyQt5.QtGui import *
from PyQt5.QtCore import * 
from PyQt5 import QtGui
import numpy as np
from osgeo import gdal
import os

###clip data

clip_op ='/home/bisag/Documents/extractRaster/clipImage.tif'


######################===========================find max value of raster image and get coordinates
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
    
import fiona
import json
import numpy as np
import rasterio
import rasterio.mask
from shapely.geometry import box, Polygon
from rasterstats import zonal_stats

def max_round(x):
    m = x.max()
    if m is np.ma.masked:
        return None
    else:
        return m

vectorbac = "/home/bisag/Documents/extractRaster/Buffer100m.shp"
#raster = "/home/bisag/Documents/extractRaster/clipImage.tif"
raster = '/home/bisag/Documents/extractRaster/Badmer(DEM1)_09_16.tif'
stats = zonal_stats(vectorbac, raster,copy_properties = True,geojson_out = True, prefix = "preci_",stats = ['max'],raster_out = True, add_stats = {"max": max_round})

loopy = range(0, len(stats))

geom = []

for i in loopy:
    geom.append(stats[i]['geometry']['coordinates'])

with fiona.open(vectorbac, "r") as shapefile:
    shapes = [feature["geometry"] for feature in shapefile]

with rasterio.open(raster) as src:
    out_image, out_transform = rasterio.mask.mask(src, 
                                                  shapes, 
                                                  crop = False, 
                                                  nodata = -999 )
    out_meta = src.meta

xminR = out_transform[2]
xmaxR = xminR + out_meta['width']*out_transform[0]
ymaxR = out_transform[5]
yminR = ymaxR + out_meta['height']*out_transform[4]

for i in range(len(geom)):
    poly = Polygon(geom[i][0])
    bounds = poly.bounds
    xmin, ymin, xmax, ymax = bounds
    rowR1 = int((ymaxR - ymax)/(-out_transform[4]))
    colR1 = int((xmin - xminR)/out_transform[0])
    rowR2 = int((ymaxR - ymin)/(-out_transform[4]))
    colR2 = int((xmax - xminR)/out_transform[0])
    width = colR2 - colR1 + 1
    height = rowR2 - rowR1 + 1


    values = []
    indices = []

    for i in range(rowR1, rowR2):
        for j in range(colR1, colR2):
            values.append(out_image[0][i][j])
            indices.append([i,j])

    ma = np.ma.masked_equal(values, -999, copy=False)

    max = ma.max()
    print(max)
    idx = ma.argmax()
    coord = xminR + indices[idx][1]*out_transform[0] + out_transform[0]/2, ymaxR + indices[idx][0]*out_transform[4] + out_transform[4]/2
    print(coord)


# import fiona
# import json
# import numpy as np
# import rasterio
# import rasterio.mask
# from shapely.geometry import box, Polygon
# from rasterstats import zonal_stats

# def max_round(x):
#     m = x.max()
#     if m is np.ma.masked:
#         return None
#     else:
#         return m

# vectorbac = "/home/bisag/Documents/extractRaster/Buffer100m.shp"
# #raster = "/home/bisag/Documents/extractRaster/clipImage.tif"
# raster = '/home/bisag/Documents/extractRaster/Badmer(DEM1)_09_16.tif'
# stats = zonal_stats(vectorbac, raster,copy_properties = True,geojson_out = True, prefix = "preci_",stats = ['max'],raster_out = True, add_stats = {"max": max_round})

# loopy = range(0, len(stats))

# geom = []

# for i in loopy:
#     geom.append(stats[i]['geometry']['coordinates'])

# with fiona.open(vectorbac, "r") as shapefile:
#     shapes = [feature["geometry"] for feature in shapefile]

# with rasterio.open(raster) as src:
#     out_image, out_transform = rasterio.mask.mask(src, 
#                                                   shapes, 
#                                                   crop = False, 
#                                                   nodata = -999 )
#     out_meta = src.meta

# xminR = out_transform[2]
# xmaxR = xminR + out_meta['width']*out_transform[0]
# ymaxR = out_transform[5]
# yminR = ymaxR + out_meta['height']*out_transform[4]

# for i in range(len(geom)):
#     poly = Polygon(geom[i][0])
#     bounds = poly.bounds
#     xmin, ymin, xmax, ymax = bounds
#     rowR1 = int((ymaxR - ymax)/(-out_transform[4]))
#     colR1 = int((xmin - xminR)/out_transform[0])
#     rowR2 = int((ymaxR - ymin)/(-out_transform[4]))
#     colR2 = int((xmax - xminR)/out_transform[0])
#     width = colR2 - colR1 + 1
#     height = rowR2 - rowR1 + 1


#     values = []
#     indices = []

#     for i in range(rowR1, rowR2):
#         for j in range(colR1, colR2):
#             values.append(out_image[0][i][j])
#             indices.append([i,j])

#     ma = np.ma.masked_equal(values, -999, copy=False)

#     max = ma.max()
#     print(max)
#     idx = ma.argmax()
#     coord = xminR + indices[idx][1]*out_transform[0] + out_transform[0]/2, ymaxR + indices[idx][0]*out_transform[4] + out_transform[4]/2
#     print(coord)
