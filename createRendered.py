import sys

new_path =['/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/planet_explorer/extlibs', '/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python3.6/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms', '/home/bisag/.local/lib/python3.6/site-packages/IPython/extensions']

for i in new_path:
    sys.path.append(i)
from qgis.core import *


def createRendered(srcFilename):
    ##[Example scripts]=group
    # Limits=selection "MinMax";"StdDev";"Cumulative"
    Limits = {"MinMax": 0, "StdDev": 1, "Cumulative": 2}
    Limits = Limits["Cumulative"]
    # Stretch=selection "NoStretch";"StretchToMinMax";"StretchAndClipToMinMax";"ClipToMinMax"
    Stretch = {"NoStretch": 0, "StretchToMinMax": 1, "StretchAndClipToMinMax": 2, "ClipToMinMax": 3}
    Stretch = Stretch["StretchToMinMax"]
    ##StdDev=number 1.0
    CumulativeLower = 0.02
    CumulativeUpper = 0.98

    # get the path to a tif file  e.g. /home/project/data/srtm.tif
    # path_to_tif = os.path.join(QgsProject.instance().homePath(), "data", "test.tif")

    # dir_path = os.path.dirname(os.path.realpath(__file__))+"/input"
    # print(dir_path)

    # print(file_list)
    # print("path to tiff: " + str(srcFilename))
    layer = QgsRasterLayer(srcFilename, "srcLayer")
    try:
        if not layer.isValid():
            print("Layer failed to load!")
            return [-1, "Layer failed to load!"]
        else:
            print("layer loaded !!")

            layer_crs = layer.crs().authid()
            print(layer_crs)
            layerType = layer.type()
            if layerType == QgsMapLayer.RasterLayer:
                renderType = layer.renderer().type()
                if renderType == "multibandcolor":
                    bands = 3
                else:
                    bands = 1

                for Band in range(bands):
                    if renderType == "multibandcolor":
                        if Band == 0:
                            myBand = layer.renderer().redBand()
                        elif Band == 1:
                            myBand = layer.renderer().greenBand()
                        elif Band == 2:
                            myBand = layer.renderer().blueBand()
                    else:
                        myBand = layer.renderer().grayBand()
                    myType = layer.renderer().dataType(myBand)

                    if Stretch == 0:
                        ContrastEnhancement = QgsContrastEnhancement.NoEnhancement
                    elif Stretch == 1:
                        ContrastEnhancement = QgsContrastEnhancement.StretchToMinimumMaximum
                    elif Stretch == 2:
                        ContrastEnhancement = QgsContrastEnhancement.StretchAndClipToMinimumMaximum
                    elif Stretch == 3:
                        ContrastEnhancement = QgsContrastEnhancement.ClipToMinimumMaximum

                    myEnhancement = QgsContrastEnhancement(myType)
                    myEnhancement.setContrastEnhancementAlgorithm(ContrastEnhancement, True)

                    if Limits == 0:
                        myRasterBandStats = layer.dataProvider().bandStatistics(myBand,
                                                                                QgsRasterBandStats.Min | QgsRasterBandStats.Max)
                        myMin = myRasterBandStats.minimumValue
                        myMax = myRasterBandStats.maximumValue

                    elif Limits == 1:
                        myRasterBandStats = layer.dataProvider().bandStatistics(myBand,
                                                                                QgsRasterBandStats.Mean | QgsRasterBandStats.StdDev)
                        myMin = myRasterBandStats.mean - (StdDev * myRasterBandStats.stdDev)
                        myMax = myRasterBandStats.mean + (StdDev * myRasterBandStats.stdDev)

                    elif Limits == 2:
                        myMin, myMax = layer.dataProvider().cumulativeCut(myBand, CumulativeLower,
                                                                          CumulativeUpper)

                    #           raise GeoAlgorithmExecutionException( str(myBand) + " " + str(myMin) + " " + str(myMax))
                    myEnhancement.setMinimumValue(myMin)
                    myEnhancement.setMaximumValue(myMax)

                    if renderType == "multibandcolor":
                        if Band == 0:
                            layer.renderer().setRedContrastEnhancement(myEnhancement)
                        elif Band == 1:
                            layer.renderer().setGreenContrastEnhancement(myEnhancement)
                        elif Band == 2:
                            layer.renderer().setBlueContrastEnhancement(myEnhancement)
                    else:
                        layer.renderer().setContrastEnhancement(myEnhancement)
                pipe = QgsRasterPipe()
                pipe.set(layer.renderer().clone())
                pipe.set(layer.dataProvider().clone())
                tif_new = srcFilename[:-4] + '_rendered.tif'
                print("outputfile: " + tif_new)
                file_writer = QgsRasterFileWriter(tif_new)
                file_writer.writeRaster(pipe, layer.width(), layer.height(), layer.extent(), layer.crs())
                # file_writer.writeRaster(pipe)
                return [0, tif_new]
            else:
                return [-1, "Layer is not a recognized raster"]

    except:
        print("Except Error: " + sys.exc_info()[0])
        return [-1, sys.exc_info()[0]]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("source file name is required")
    else:
        print(createRendered(sys.argv[1]))
