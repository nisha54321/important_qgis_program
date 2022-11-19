import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
from scipy.spatial import distance_matrix
import json
import sys

from math import sin, cos, sqrt, atan2, radians
import os

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
    print(route_distance)
    plan_output.append(manager.IndexToNode(index))
    return plan_output

def dist(x, y):
    """Function to compute the distance between two points x, y"""

    lat1 = radians(x[0])
    lon1 = radians(x[1])
    lat2 = radians(y[0])
    lon2 = radians(y[1])

    R = 3958#3798,6373,3958,3440.0652

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return round(distance, 4)

def calculate_tsp():
    cwd = sys.argv[1]
    input_path = sys.argv[2]
    
    
    #input_path = '/home/bisag/Downloads/TSP-ILP-main/55.geojson'
    #cwd = os.getcwd()
    attid ='Sno'#serial no
    attSeq = 'seq'#seq field
    attSensor = 'Sensor'
    attSector = 'Sector'
    atttime = 'DT'#dwelltime(hour)
    attGNAME= "GNAME"
    attlen = "seg_length(km)"

    #velocity = 65 #(km/h)
    Endu = 8 #hour (capacity of fly plane)
    
    opsave ='output'

    output_path= os.path.join(cwd,opsave,'sequence.geojson')
    if os.path.exists(output_path):
        os.remove(output_path)
    
    latlong = []
    idList,seqList ,timelist,attSensorList,attSectorList,attGNAMEList = [],[],[],[],[],[]

    with open(input_path) as f:
        data = json.load(f)
        for feature in data['features']:
            geom = feature['geometry']['coordinates']
            latlong.append(geom) 
            
            id = feature['properties'][attid]
            timeval = feature['properties'][atttime]
            sen = feature['properties'][attSensor]
            sec = feature['properties'][attSector]
            gn = feature['properties'][attGNAME]
            
            idList.append(id)
            timelist.append(timeval)
            attSensorList.append(sen)
            attSectorList.append(sec)
            attGNAMEList.append(gn)
            
    x1 = list(list(zip(*latlong))[0])
    y1 = list(list(zip(*latlong))[1])


    d = pd.DataFrame({'x':x1,'y':y1})
    
    d[['x','y']] = (np.radians(d.loc[:,['x','y']]))
    
    df = pd.DataFrame({'x':x1,'y':y1,attid:idList,atttime:timelist,attSensor:attSensorList,attSector:attSectorList,attGNAME:attGNAMEList})

   
    dis_mat=pd.DataFrame(distance_matrix(d.values,d.values), index=d.values,columns=d.values)#find distance matrix
    dis_mat = dis_mat.values.tolist()
    
    d_list =dis_mat[:]##because miles
    for i in range(len(dis_mat)):
        for j in range(len(dis_mat[i])):
            d_list[i][j] = dis_mat[i][j] * 3959#69#3959#3440.0652#miles,6371 km
    # print(d_list)       
    data = create_data_model(d_list)

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
        
    #print(seqpoint)
    data1 = seqpoint[:-1]

    geos = []

    k = 0
    for i in data1:
        p = df.iloc[[i]]
        
        dis_mat = p.values.tolist()

        dis_mat =dis_mat[0]
        
        poly = {
            "type": "Feature",
            'properties': {
            'Sno': dis_mat[2],
            'DT': dis_mat[3],
            'Sensor': str(dis_mat[4]),
            'Sector': str(dis_mat[5]),
            'GNAME': str(dis_mat[6]),
            attSeq: k
            },
            
            "geometry": {
                    "type": "Point",
                    "coordinates": [
                    dis_mat[0],dis_mat[1]
                    ]
                }
        }
        geos.append(poly)
        
        k = k+1
        
    geometries = {
        "type": "FeatureCollection",
        "name": "location2",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": geos
    }

    #output_path = '/home/bisag/Downloads/TSP-ILP-main/test.geojson'
    with open(output_path, 'w') as f:
        json.dump(geometries, f, indent=2)
        
    return output_path
        
        
    # resalgo = processing.run("qgis:pointstopath",#create path
    #                                         {'INPUT':output_path,
    #                                         'CLOSE_PATH':True,
    #                                         'ORDER_FIELD':attSeq,
    #                                         'GROUP_FIELD':'',
    #                                         'DATE_FORMAT':'',
    #                                         'OUTPUT':'TEMPORARY_OUTPUT'})

        
    # resalgo1 = processing.run("native:explodelines",##single part to multipart (line segement)
    #                 {'INPUT':resalgo['OUTPUT'],
    #                 'OUTPUT':'TEMPORARY_OUTPUT'})

    # opres = processing.run("native:addautoincrementalfield", {'INPUT':resalgo1['OUTPUT'],
    #                                                     'FIELD_NAME':'AUTO',
    #                                                     'START':1,
    #                                                     'GROUP_FIELDS':[],'SORT_EXPRESSION':'','SORT_ASCENDING':True,'SORT_NULLS_FIRST':False,
    #                                                     'OUTPUT':os.path.join(cwd,opsave,'segmentlineId_loc.geojson')})

    # ###add information of point to line segment (path) 
    # with open(output_path) as f:#read sequence data
    #     data = json.load(f)
        
    # idList,seqList ,timelist,attSensorList,attSectorList,attGNAMEList = [],[],[],[],[],[]

    # for feature in data['features']:
    #     id = feature['properties'][attid]
    #     seq = feature['properties'][attSeq]
    #     timeval = feature['properties'][atttime]
    #     sen = feature['properties'][attSensor]
    #     sec = feature['properties'][attSector]
    #     gn = feature['properties'][attGNAME]
        
    #     idList.append(id)
    #     seqList.append(seq)
    #     timelist.append(timeval)
    #     attSensorList.append(sen)
    #     attSectorList.append(sec)
    #     attGNAMEList.append(gn)
        
        
    # idtime = {idList[i]: timelist[i] for i in range(len(idList))}
    # idsen = {idList[i]: attSensorList[i] for i in range(len(idList))}
    # idsec = {idList[i]: attSectorList[i] for i in range(len(idList))}
    # idgname = {idList[i]: attGNAMEList[i] for i in range(len(idList))}
    # print(seqList)

    # latlong2 = [idList[i]for i in seqList]

    # res = list(zip(latlong2, latlong2[1:] + latlong2[:1]))#id and seq

    # with open(opres['OUTPUT']) as f:##add id to line segment
    #     data = json.load(f)
        
    # z = 0
    # for feature in data['features']:
    #     print(feature['properties'])
    #     feature['properties']['fromto']=str(res[z])
    #     feature['properties'][atttime]=idtime[res[z][0]]
    #     feature['properties'][attSensor]=idsen[res[z][0]]
    #     feature['properties'][attSector]=idsec[res[z][0]]
    #     feature['properties'][attGNAME]=idgname[res[z][0]]
    #     feature['properties']['begin']=str(res[z][0])
    #     feature['properties']['end']=str(res[z][1])
        
    #     z = z+1
        
    # with open(optimal_path, 'w+') as f:
    #     json.dump(data, f, indent=2)
        

    # output = processing.run("native:fieldcalculator", {'INPUT':optimal_path,# ##find length feature
    #                                             'FIELD_NAME':attlen,
    #                                             'FIELD_TYPE':0,
    #                                             'FIELD_LENGTH':0,
    #                                             'FIELD_PRECISION':0,
    #                                             'FORMULA':' round($length /1000,3)',
    #                                             'OUTPUT':'TEMPORARY_OUTPUT'})
                                            
    # output1 = processing.run("native:fieldcalculator", {'INPUT':output['OUTPUT'],# ##find reach time feature
    #                                             'FIELD_NAME':'reach_time',
    #                                             'FIELD_TYPE':0,
    #                                             'FIELD_LENGTH':0,
    #                                             'FIELD_PRECISION':0,
    #                                             'FORMULA':f'round(\"{attlen}\" /{velocity},3)',
    #                                             'OUTPUT':os.path.join(cwd,opsave,'result.geojson')})

    # with open(output1['OUTPUT']) as f:##add id to line segment
    #     data = json.load(f)
        
    # rech_t,dtime = [],[]
    # for feature in data['features']:
    #     r=feature['properties']['reach_time']
    #     d =feature['properties'][atttime]
    #     rech_t.append(float(0.0 if r is None else r))
    #     dtime.append(float(0.0 if d is None else d))#value nonetype so error
        
    # overalltime = sum(rech_t)+sum(dtime)

    # if overalltime>24:
    #     pass

    # print(overalltime,' (hour)')
    
if __name__ == "__main__":
    calculate_tsp()
