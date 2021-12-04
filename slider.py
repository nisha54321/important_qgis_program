from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
import sys,os
import numpy as np
import rasterio
from osgeo import gdal
import struct

app = Flask(__name__)
CORS(app)

cwd = os.getcwd()
nameraster = cwd+"/view.tif"
maxten = []
@app.route("/", methods= ['GET', 'POST'])
def index():

    dataset = rasterio.open(cwd+'/view.tif')
    band1 = dataset.read(1)

    #matrix(multidimention to one) to one dimension(use .flatten() method)
    flat=band1.flatten()

    flat.sort()
    
    #remove duplicates
    res = []
    [res.append(x) for x in flat if x not in res]

    #decesnding
    res1 =  sorted(res, key=int, reverse=True)

    n = 10 #first 10 number
    nthmax = res1[ : n]

    print(nthmax)


    #maxval = [500, 400, 300, 200, 100]
    max1 = [str(i)for i in nthmax]

    print(max1)
    if request.method == 'POST':
        val1 = request.form["slider1"]
        print("hi")
        print(val1)
    maxten.append(nthmax)
    return render_template("slider.html", maxval = nthmax, max1 = max1)


@app.route("/get_data", methods= ['GET', 'POST'])
def get_data():

    if request.method == 'POST':
        json_data = request.get_json()
        rval = json_data['dd']
        print(rval)

        print(maxten[0])
        ########find latlong base on raster grid value

        dataset = gdal.Open(nameraster)
        geotransform = dataset.GetGeoTransform()
        band = dataset.GetRasterBand(1)

        fmttypes = {'Byte':'B', 'UInt16':'H', 'Int16':'h', 'UInt32':'I', 
                    'Int32':'i', 'Float32':'f', 'Float64':'d'}

        #print ("rows = %d columns = %d" % (band.YSize, band.XSize))

        BandType = gdal.GetDataTypeName(band.DataType)

        X = geotransform[0] 
        Y = geotransform[3] 
        valcoor = {}
        key = []
        coord = []

        nthmax = maxten[0]

        for y in range(band.YSize):

            scanline = band.ReadRaster(0, y, band.XSize, 1, band.XSize, 1, band.DataType)
            values = struct.unpack(fmttypes[BandType] * band.XSize, scanline)
            #print(values)
            
            for value in values:

                if(value == rval):  
                    latlong = "%.11f  %.11f " % (X, Y)
                    coord.append(latlong)
                    key.append(rval)

                X += geotransform[1] 
            X = geotransform[0]
            Y += geotransform[5] 
        dataset = None

        all_data = {'rval':rval,'coord':coord}

        return jsonify(all_data)
        
    return render_template("slider.html")

if __name__ == '__main__':
    app.run(debug=True,port = '5544')
