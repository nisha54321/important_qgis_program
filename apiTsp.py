#http://0.0.0.0:2001/?inputpath=/home/bisag/Downloads/TSP-ILP-main/location2.geojson
import sys,os
new_path = ['/usr/share/qgis/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/usr/share/qgis/python/plugins', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/home/bisag/.local/lib/python3.6/site-packages', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages', '/usr/lib/python3.6/dist-packages', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins', '/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones/iso/utilities', '.', '/home/bisag/.local/lib/python3.6/site-packages/', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/qproto', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/csv_tools', '/app/share/qgis/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins', '/app/share/qgis/python/plugins', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages', '/app/lib/python3.8/site-packages/numpy-1.19.2-py3.8-linux-x86_64.egg', '/app/lib/python3.8/site-packages/MarkupSafe-1.1.1-py3.8-linux-x86_64.egg', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python', '/home/bisag/.local/lib/python3.6/site-packages/', '.', '/home/bisag/.var/app/org.qgis.qgis/data/QGIS/QGIS3/profiles/default/python/plugins/QuickMultiAttributeEdit3/forms', '/home/bisag/.local/lib/python3.6/site-packages/IPython/extensions']

for i in new_path:
    sys.path.append(i)

from qgis.core import (QgsApplication)
QgsApplication.setPrefixPath('/usr', True) 
qgs = QgsApplication([],False)
qgs.initQgis()
from qgis import processing
from qgis.analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing
Processing.initialize()
#QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
  
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
from scipy.spatial import distance_matrix

from flask import Flask, request, jsonify
from flask_cors import CORS

import json
app = Flask(__name__)
CORS(app)

def create_data_model(dis_mat):
    data = {}
    data['distance_matrix'] = dis_mat
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data


def print_solution(manager, routing, solution):
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = []
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output.append(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output.append(manager.IndexToNode(index))
    print('route_distance:',route_distance)
    return plan_output

@app.route('/',methods=['GET'])
def main():
    
    input_path = request.args.get('inputpath')
    cwd = os.getcwd()
    attid ='Sno'#serial no
    attSeq = 'seq2'#seq field
    attSensor = 'Sensor'
    attSector = 'Sector'
    atttime = 'DT'#dwelltime(hour)
    attGNAME= "GNAME"
    attlen = "seg_length(km)"

    velocity = 65 #(km/h)
    Endu = 8 #hour (capacity of fly plane)

    output_path= os.path.join(cwd,'output','sequence_loc.geojson')
    optimal_path = os.path.join(cwd,'output','output_loc.geojson')
    

    with open(input_path) as f:
        data = json.load(f)
        latlong = []
        for feature in data['features']:
            geom = feature['geometry']['coordinates']
            latlong.append(geom)   
    
    x1 = list(list(zip(*latlong))[0])
    y1 = list(list(zip(*latlong))[1])
    d = pd.DataFrame({'x':x1,'y':y1})
    
    print(d.values, d.index)# 
    dis_mat=pd.DataFrame(distance_matrix(d.values,d.values), index=d.index,columns=d.index)#find distance matrix
    dis_mat = dis_mat.values.tolist()
    
    data = create_data_model(dis_mat)

    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    routing = pywrapcp.RoutingModel(manager)


    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        seqpoint = print_solution(manager, routing, solution)
        
    print(seqpoint)
    seqpoint = seqpoint[:-1]

    z = 0
    
    with open(input_path) as f:
        data = json.load(f)
    for feature in data['features']:
        feature['properties'][attSeq]=seqpoint[z]
        z = z+1

    with open(output_path, 'w') as f:#write sequence in geojson
        json.dump(data, f, indent=2)
        
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
                                                        'OUTPUT':os.path.join(cwd,'output','segmentlineId_loc.geojson')})
    
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
        
   
    output = processing.run("native:fieldcalculator", {'INPUT':optimal_path,# ##find length feature
                                              'FIELD_NAME':attlen,
                                              'FIELD_TYPE':0,
                                              'FIELD_LENGTH':0,
                                              'FIELD_PRECISION':0,
                                              'FORMULA':' round($length /1000,3)',
                                              'OUTPUT':'TEMPORARY_OUTPUT'})
                                           
    output1 = processing.run("native:fieldcalculator", {'INPUT':output['OUTPUT'],# ##find reach time feature
                                              'FIELD_NAME':'reach_time',
                                              'FIELD_TYPE':0,
                                              'FIELD_LENGTH':0,
                                              'FIELD_PRECISION':0,
                                              'FORMULA':f'round(\"{attlen}\" /{velocity},3)',
                                             'OUTPUT':os.path.join(cwd,'output','output_loc.geojson')})
    
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
    
    print(overalltime,' (hour)')
        
    return jsonify(str(res),overalltime)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=2001)