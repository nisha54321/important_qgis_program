#import modules of qgis
import sys
import os
import shutil
import time
import logging
import pathlib
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
import psycopg2
import time
import requests
import glob
import shapefile
import json
import xmltodict

#the following imports are used for infer
import cv2
import numpy as np
import torch
from torchvision import models, transforms
from PIL import Image
import torch.backends.cudnn as cudnn
from getLayers import getLayers
from createRendered import createRendered
from image_info import insert_sat_image_data_to_db, insert_grid_image_data_to_db, fetch_grid_images_from_sat_img_id, insert_predictions_to_db
import rasterio
from shapely.geometry import Polygon

# qgis_path = ['C:/PROGRA~1/QGIS3~1.14/apps/qgis/./python', 'C:/Users/Administrator/AppData/Roaming/QGIS/QGIS3\\profiles\\default/python', 'C:/Users/Administrator/AppData/Roaming/QGIS/QGIS3\\profiles\\default/python/plugins', 'C:/PROGRA~1/QGIS3~1.14/apps/qgis/./python/plugins', 'C:\\PROGRA~1\\QGIS3~1.14\\apps\\Python37', 'C:\\PROGRA~1\\QGIS3~1.14\\apps\\Python37\\Scripts', 'C:\\Program Files\\QGIS 3.14\\bin\\python37.zip', 'C:\\PROGRA~1\\QGIS3~1.14\\apps\\Python37\\DLLs', 'C:\\PROGRA~1\\QGIS3~1.14\\apps\\Python37\\lib', 'C:\\Program Files\\QGIS 3.14\\bin', 'C:\\PROGRA~1\\QGIS3~1.14\\apps\\Python37\\lib\\site-packages', 'C:\\PROGRA~1\\QGIS3~1.14\\apps\\Python37\\lib\\site-packages\\win32', 'C:\\PROGRA~1\\QGIS3~1.14\\apps\\Python37\\lib\\site-packages\\win32\\lib', 'C:\\PROGRA~1\\QGIS3~1.14\\apps\\Python37\\lib\\site-packages\\Pythonwin', 'C:/Users/Administrator/AppData/Roaming/QGIS/QGIS3\\profiles\\default/python']
# for i in qgis_path:
#     sys.path.append(i)
#
#from qgis.core import *

###

geoserver_coverage_store_url = r"http://localhost:8080/geoserver/rest/workspaces/cite/coveragestores"
geoserver_layer_publish = r"http://localhost:8080/geoserver/rest/workspaces/cite/coveragestores/"
base_path = r"/home/bisag/test" + os.path.sep
workspace = 'cite'
logging.basicConfig(level=logging.ERROR)

cudnn.benchmark = True
cudnn.enabled = True

device = 'cuda' if torch.cuda.is_available() else 'cpu'

model_path = 'deeplabv3_resnet101_infer_v3.pt' #give the path to the model. either absolute or relative if it is in the same directory as the program

model = torch.load(model_path,map_location=device)
mean = [0.485, 0.456, 0.406]
std = [0.229, 0.224, 0.225]

model = model.to(device)

model = model.eval()

test_transform = transforms.Compose([transforms.Resize((512, 512)),
                                        transforms.ToTensor(),
                                        transforms.Normalize(mean=mean, std=std)])


# def infer_pytorch(test_img_path):
#     print(test_img_path)
#     test_img = Image.open(test_img_path).convert('RGB')

#     width, height = test_img.size

#     test_tensor = test_transform(test_img).unsqueeze(0).to(device)

#     test_out = transforms.ToPILImage()(torch.sigmoid(model(test_tensor)['out'])[0, 0].cpu())
#     test_out = test_out.resize((width, height))
#     test_out = np.array(test_out).copy()
#     test_img = np.array(test_img).copy()
#     test_img_result = test_out

#     mask_rgb = cv2.merge((test_img_result,
#                             np.zeros((height, width), dtype=np.uint8),
#                             np.zeros((height, width), dtype=np.uint8)))

#     # cv2.imwrite(os.path.join('red_results', prefix) + '_1.jpg', mask_rgb[:, :, ::-1])

#     _, thr_img = cv2.threshold(test_img_result, 10, 255, cv2.THRESH_BINARY)
#     thr_img = cv2.morphologyEx(thr_img, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))

#     contours = cv2.findContours(thr_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
#     contour_plot = test_img.copy()

#     for contour in contours:
#         prev = contour[0][0]
#         start = prev
#         for point in contour[1:]:
#             cur = point[0]
#             cv2.line(contour_plot, (prev[0], prev[1]), (cur[0], cur[1]), (0, 0, 255), thickness=2)
#             prev = cur
#         cv2.line(contour_plot, (prev[0], prev[1]), (start[0], start[1]), (0, 0, 255), thickness=2)

#     cv2.imwrite(test_img_path, contour_plot)

#     #overlaid_img = cv2.addWeighted(test_img, 0.7, mask_rgb, 0.3, 0)
#     #cv2.imwrite(os.path.join('purple_results', prefix) + '_3.jpg', overlaid_img)
#     # print("result saved")

#     # Return number of detected contours in the image
#     return len(contours)

def infer_pytorch(grid_image_data):
    test_img_path = grid_image_data[1]
    jpg_path = test_img_path.split('.tif')[0] + '.jpg'
    print(test_img_path)
    test_img = Image.open(jpg_path).convert('RGB')

    width, height = test_img.size

    test_tensor = test_transform(test_img).unsqueeze(0).to(device)

    test_out = transforms.ToPILImage()(torch.sigmoid(model(test_tensor)['out'])[0, 0].cpu())
    test_out = test_out.resize((width, height))
    test_out = np.array(test_out).copy()
    test_img = np.array(test_img).copy()
    test_img_result = test_out

    mask_rgb = cv2.merge((test_img_result,
                          np.zeros((height, width), dtype=np.uint8),
                          np.zeros((height, width), dtype=np.uint8)))

    # cv2.imwrite(os.path.join('red_results', prefix) + '_1.jpg', mask_rgb[:, :, ::-1])

    _, thr_img = cv2.threshold(test_img_result, 10, 255, cv2.THRESH_BINARY)
    thr_img = cv2.morphologyEx(thr_img, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))

    contours = cv2.findContours(thr_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
    contour_plot = test_img.copy()

    polygons = []
    map_layer = rasterio.open(test_img_path)
    for contour in contours:
        prev = contour[0][0]
        start = prev
        for point in contour[1:]:
            cur = point[0]
            cv2.line(contour_plot, (prev[0], prev[1]), (cur[0], cur[1]), (0, 0, 255), thickness=2)
            prev = cur
        cv2.line(contour_plot, (prev[0], prev[1]), (start[0], start[1]), (0, 0, 255), thickness=2)

        print(contour)
        lon_lat_points = [list(map_layer.xy(int(point[0][1]), int(point[0][0]))) for point in contour]
        polygons.append(Polygon(lon_lat_points))

    cv2.imwrite(jpg_path, contour_plot)

    # overlaid_img = cv2.addWeighted(test_img, 0.7, mask_rgb, 0.3, 0)
    # cv2.imwrite(os.path.join('purple_results', prefix) + '_3.jpg', overlaid_img)
    # print("result saved")

    # Return number of detected contours in the image
    # return len(contours)
    return polygons

class EventHandler(RegexMatchingEventHandler):
    REGEX = [r"^.*$"]

    def __init__(self):
        super().__init__(self.REGEX)

    def on_created(self, event):
        print(event)
        try:
            # connection = psycopg2.connect(
            #     user="postgres", password="postgres", host="localhost", database="project")
            # cursor = connection.cursor()
            myval = str(event.src_path)
            # print(type(event.src_path))

            if event.__class__.__name__ == 'FileCreatedEvent' and myval.endswith('.tif') and not myval.endswith('_rendered.tif'):
                # src_path = event.src_path
                historicalSize = -1
                while (historicalSize != os.path.getsize(myval)):
                    historicalSize = os.path.getsize(myval)
                    time.sleep(5)

                print("New file found: "+ myval)
                checkRendered = createRendered(myval)
                targetdir_tif_path = None
                if(checkRendered[0] == 0):
                    targetdir_tif_path = checkRendered[1]
                    sat_img_id = insert_sat_image_data_to_db(targetdir_tif_path)
                elif(checkRendered[0] == -1):
                    targetdir_tif_path = None
                    print("Cannot create rendered file because: "+ checkRendered[1])
                else:
                    targetdir_tif_path = None
                    print("An unknown error has occured while rendering")
                
                if targetdir_tif_path is not None:

                    folder_path = os.path.splitext(targetdir_tif_path)[0] #this gives the foldername
                    os.makedirs(folder_path,exist_ok=True) # we make the folder for the uploaded file
                    #The following code can be used to publish all folders at once if geoserver data directory is corrupt or del
                    #for entry_name in os.listdir(base_path):
                    #    entry_path = os.path.join(base_path, entry_name)
                    #    if os.path.isdir(entry_path):
                    #        folder_names.append(entry_name)
                    # Use variable for gdal retile --targetDir path
                    targetdir_path = folder_path #base_path + folder_names[0]  ### folder_path
                    targetdir_tif_path = targetdir_tif_path#event.src_path.split('.')[0] + '_rendered.tif'
                    #############     commented this
                    #returnval = os.system(r'python-qgis.bat -m gdal_retile -v -r bilinear -levels 4 -ps 512 512 -co "TILED=YES" -co "COMPRESS=LZW" -targetDir  C:\Users\Administrator\Videos\test\C2A052241_01011PS_20180101_DIP_ort_rendered C:\Users\Administrator\Videos\test\C2A052241_01011PS_20180101_DIP_ort_rendered.tif')
                    
                    # if operatingsys == win:
                    #     print()
                    # elif opertingsys == linux:
                    #     print()

                    if sys.platform.startswith('win32'):
                        print("windows")
                        gdal_retile_execute = r'python-qgis.bat -m gdal_retile -v -r bilinear -levels 4 -ps 512 512 -co "TILED=YES" -co "COMPRESS=LZW" -targetDir {0} {1}'.format(targetdir_path, targetdir_tif_path)
                        print(gdal_retile_execute)
                        returnval = os.system(gdal_retile_execute)

                    elif sys.platform.startswith('linux'):
                        print("linux")
                        gdal_retile_execute = r'gdal_retile.py -v -r bilinear -levels 4 -ps 512 512 -co "TILED=YES" -co "COMPRESS=LZW" -targetDir {0} {1}'.format(targetdir_path, targetdir_tif_path)
                        print(gdal_retile_execute)
                        returnval = os.system(gdal_retile_execute)

                        
                        # processing.run("gdal:retile", {'INPUT':['/home/user/Desktop/image/Slave.tif'],
                        #                                                 'TILE_SIZE_X':300,
                        #                                                 'TILE_SIZE_Y':250,
                        #                                                 'OVERLAP':0,
                        #                                                 'LEVELS':1,
                        #                                                 'SOURCE_CRS':None,
                        #                                                 'RESAMPLING':0,
                        #                                                 'DELIMITER':';',
                        #                                                 'OPTIONS':'',
                        #                                                 'EXTRA':'',
                        #                                                 'DATA_TYPE':5,
                        #                                                 'ONLY_PYRAMIDS':False,
                        #                                                 'DIR_FOR_ROW':False,
                        #                                                 'OUTPUT':'/home/user/Desktop/retile'})
                        
                        
                    else:
                        print("!! OS is not recognized !!")

                    if(returnval == 0):
                        # cursor.execute("INSERT INTO tifs_list (tifs_path) VALUES ('" + myval + "')")
                        # connection.commit()
                        #Now we publish this as image pyramid in geoserver
                        # code for establish coverage/datastore

                        #for folder in open(folders).readlines():
                        geoserver_layers = getLayers()
                        print("Geoserver Layers")
                        print(geoserver_layers)
                        print(os.path.basename(targetdir_path))
                        print("--key:value--")
                        mykey = workspace+":"+os.path.basename(targetdir_path)
                        print(mykey)
                        if(not mykey in geoserver_layers):
                            print("Layer does not exist. Publishing in geoserver: "+ targetdir_path)
                            
                            url = geoserver_coverage_store_url
                            folderpath_strip = folder_path.strip()
                            folder_name = os.path.basename(folderpath_strip)
                            xmldata_datacoverage = r"<coverageStore><name>" + folder_name + "</name><enabled>true</enabled><workspace><name>cite</name></workspace><type>ImagePyramid</type><url>file:" + folderpath_strip + "</url></coverageStore>"
                            xmldata_layer_publish = r"<coverage><nativeName>" + folder_name + "</nativeName><name>" + folder_name + "</name><title>myLayer</title><srs>EPSG:4326</srs></coverage>"
                            headers = {'Content-Type': 'application/xml'}
                            auth = ('admin', 'geoserver')
                            xmldata = xmldata_datacoverage
                            response_new = requests.post(url, headers=headers, auth=auth, data=xmldata)
                            print(response_new)
                            print(response_new.text)

                            publish_url = geoserver_layer_publish + folder_name + "/coverages"
                            print(publish_url)
                            publish_xml = xmldata_layer_publish
                            publish_response = requests.post(publish_url, headers=headers, auth=auth, data=publish_xml)
                            print(publish_response)
                            print(publish_response.text)

                            #we will preprocess and infer the newly created layer
                            
                            # now we convert all the 0*.tif to 0*.jpg
                            # indented 4 space
                            #os.chdir(r"C:\Users\Administrator\Videos\test\C2A052241_01011PS_20180101_DIP_ort_rendered\0")
                            infer_path = folder_path + os.path.sep + '0'
                            zero_folder_path = infer_path
                            os.chdir(zero_folder_path)
                            if sat_img_id is not None:
                                insert_grid_image_data_to_db(zero_folder_path, sat_img_id)
                            grid_image_data_list=fetch_grid_images_from_sat_img_id(sat_img_id)
                            # print(grid_image_data_list)
                            lines = glob.glob('*.tif', recursive=False)
                            for line in lines:
                                img = Image.open(line.strip()).convert('RGB')
                                img.convert('RGB').save(line.strip().replace(".tif", "") + ".jpg")
                            #Now we edit the shapefile for including only .jpg files
                            shp_file_path = infer_path + os.path.sep + "0.shp"
                            file_name = shp_file_path

                            r = shapefile.Reader(file_name)

                            outlist = []

                            for shaperec in r.iterShapeRecords():
                                outlist.append(shaperec)
                            shapeType =  r.shapeType
                            rFields = list(r.fields)
                            r = None
                            ##to be sure we delete the existing shapefile
                            if os.path.exists(file_name):
                                os.remove(file_name)
                            else:
                                print("file does not exist"+ file_name)

                            ##to be sure we delete the existing dbf file
                            dbf_file = file_name.replace(".shp",".dbf")
                            if os.path.exists(dbf_file):
                                os.remove(dbf_file)
                            else:
                                print("file does not exist" + dbf_file)
                            ##to be sure we delete the existing shx file
                            shx_file = file_name.replace(".shp", ".shx")
                            if os.path.exists(shx_file):
                                os.remove(shx_file)
                            else:
                                print("file does not exist" + shx_file)

                            w = shapefile.Writer(file_name,shapeType)

                            w.fields = rFields

                            for shaperec in outlist:
                                record = shaperec.record[0].replace('.tif', '.jpg')
                                w.record(record)
                                w.shape(shaperec.shape)
                                # print(shaperec)
                            w.close()
                            #Now we infer the 0 folder created by the image pyramid
                            #os.chdir(r"C:\\Users\\Administrator\\Videos\\test\\C2A052241_01011PS_20180101_DIP_ort_rendered\\0\\")
                            #for file in glob.glob("*.tif"):
                            #    print(file)
                            #    img = Image.open(file).convert('RGB')
                            #    img.convert('RGB').save(file.strip().replace(".tif", "") + ".jpg")
                            meta_data = {}
                            start = time.time()
                            # for fn in os.listdir(infer_path):
                            #     if fn.endswith('.jpg'):
                            #         meta_data[fn] = infer_pytorch(os.path.join(infer_path, fn))
                            
                            # print(sum(meta_data.values()))
                            predictions = []
                            for grid_image_data in grid_image_data_list:
                                polygons = infer_pytorch(grid_image_data)
                                if len(polygons) == 0:
                                    continue
                                prediction = list(grid_image_data)
                                prediction.append(polygons)
                                predictions.append(prediction)
                            insert_predictions_to_db(predictions)
                            print('Total inference time: {} seconds'.format(time.time() - start))

                        else:
                            print("Layer Exists: "+ targetdir_path)
                            print("we will not infer again... this might give incorrect output as infer will be done on inferred images")

                else:
                    print("An error has occured. Rendered file is None")

        except Exception as error:
            print(error)

        # finally:
        #     if (connection):
        #         cursor.close()
                # connection.close()

# print("Created new File/Folder - %s " %event.src_path)

def on_deleted(self, event):
    print(event)
    # try:
    #     connection = psycopg2.connect(
    #         user = "postgres", password = "postgres", host = "localhost", database = "project"
    #     )
    #     cursor = connection.cursor()
    #     myval2 = str(event.src_path)
    #     cursor.execute("DELETE FROM tifs_list WHERE tifs_path=('" + myval2 + "') ")
    #     connection.commit()
    # except (Exception, psycopg2.Error) as error:
    #     print(error)
    #     if (connection):
    #         print("Failed to insert record into table", error)
    # finally:
    #     if (connection):
    #         cursor.close()
    #         connection.close()

def on_modified(self, event):
    print(event)

#     # print(event.src_path)

def on_moved(self, event):
    print(event)
    try:
        connection = psycopg2.connect(
            user="postgres", password="postgres", host="localhost", database="project")
        cursor = connection.cursor()
        myval = str(event.dest_path)
        myval2 = str(event.src_path)
        # print(type(event.src_path))
        cursor.execute("UPDATE tifs_list SET  tifs_path=('" + myval + "') WHERE  tifs_path=('" + myval2 + "') ")
        connection.commit()


    except (Exception, psycopg2.Error) as error:
        print(error)
        if (connection):
            print("Failed to insert record into table", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
    # print(event.src_path)


class Monitor:
    def __init__(self, src_path):
        self.__src_path = src_path
        self.__event_handler = EventHandler()
        self.__event_observer = Observer()

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        self.__schedule()
        self.__event_observer.start()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()

    def __schedule(self):
        self.__event_observer.schedule(
            self.__event_handler,
            self.__src_path,
            recursive=False#We dont want to watch whatever happens inside the newly created folders
        )


src_path = sys.argv[1] if len(sys.argv) > 1 else base_path   
Monitor(src_path).run()


	
	
