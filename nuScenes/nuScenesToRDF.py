# Purpose: Creates a knowledge graph for the nuScenes dataset in Turtle format
#          For the large nuScenes dataset, it will create multiple files that can be concatenated 
#
# How to use:
#   python nuScenesToRDF.py -f <input-folder> -d <dataset-name> 
#
#   E.g.:  python nuScenesToRDF.py -f 'C:\Data\v1.0-trainval\' -d 'nuscenes_v1.0-trainval'
#          python nuScenesToRDF.py -f '.\v1.0-trainval\' -d 'nuscenes-kg'
#
#   Notes: 
#     - The input folder is the directoy where the nuScenes data are extracted, e.g. C:\Data\v1.0-trainval
#     - The dataset-name is the name of the target RDF TTL file(s)
#
# Python version used: 3.8

import os, time
import sys, getopt
import pandas as pd
from pandas.core.algorithms import isin
from pandas.core.arrays import boolean
from pandas.io.pytables import attribute_conflict_doc
import rdflib
from rdflib import URIRef, BNode, Literal, Namespace, Graph
from rdflib.namespace import FOAF, DCTERMS, XSD, RDF, SDO
from pathlib import Path

path = '' 
dataset = ''
try:
    opts, args = getopt.getopt(sys.argv[1:],"f:d:",["folder=", "dataset="])
except getopt.GetoptError:
    print("nuScenesToRDF.py -f <input-folder> -d <dataset-name>")
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-f", "--folder"):
        path = arg
    elif opt in ("-d", "--dataset"):
        dataset = arg

if len(path) == 0 or len(dataset) == 0:
    print("nuScenesToRDF.py -f <input-folder> -d <dataset-name>")
    sys.exit(2)

processTime = time.process_time()
actualTime = time.time()

rdf = Graph()
NS = Namespace('http://www.nuscenes.org/nuScenes/')
rdf.bind("nus", NS)
rdf_index = 1
number = 1 # File number number
max_num_triples_per_file = 2500000

# RDF Serialization 
def rdf_serialization():
    global rdf, number
    print(f"serializing ... ('{dataset}_{number}_rdf.ttl')")
    rdf.serialize(destination=f'{dataset}_{number}_rdf.ttl', format='ttl')
    rdf = Graph()
    rdf.bind("nus", NS)
    number += 1

def batch_rdf_serialization(triple_count):
    global rdf_index 
    rdf_index += triple_count
    if rdf_index > max_num_triples_per_file:
        rdf_serialization()
        rdf_index = 0

# Start with building a dictionary for category_token and category
# categoryDict{category_token: category} 
file = os.path.join(path,'category.json')
categoryDict = {}
if os.path.isfile(file):
    print(file)
    df = pd.read_json(file)
    for entry in df.itertuples():
        categoryToken = entry.token
        categoryName = entry.name
        if(categoryName == "human.pedestrian.adult"):
            categoryDict[categoryToken] = "Adult"
        elif(categoryName == "human.pedestrian.child"):
            categoryDict[categoryToken] = "Child"
        elif(categoryName == "human.pedestrian.wheelchair"):
            categoryDict[categoryToken] = "Wheelchair"
        elif(categoryName == "human.pedestrian.stroller"):
            categoryDict[categoryToken] = "Stroller"
        elif(categoryName == "human.pedestrian.personal_mobility"):
            categoryDict[categoryToken] = "PersonalMobility"
        elif(categoryName == "human.pedestrian.police_officer"):
            categoryDict[categoryToken] = "PoliceOfficer"
        elif(categoryName == "human.pedestrian.construction_worker"):
            categoryDict[categoryToken] = "ConstructionWorker"
        elif(categoryName == "animal"):
            categoryDict[categoryToken] = "Animal"
        elif(categoryName == "vehicle.car"):
            categoryDict[categoryToken] = "Car"
        elif(categoryName == "vehicle.motorcycle"):
            categoryDict[categoryToken] = "Motorcycle"
        elif(categoryName == "vehicle.bicycle"):
            categoryDict[categoryToken] = "Bicycle"
        elif(categoryName == "vehicle.bus.bendy"):
            categoryDict[categoryToken] = "BusBendy"
        elif(categoryName == "vehicle.bus.rigid"):
            categoryDict[categoryToken] = "BusRigid"
        elif(categoryName == "vehicle.truck"):
            categoryDict[categoryToken] = "Truck"
        elif(categoryName == "vehicle.construction"):
            categoryDict[categoryToken] = "ConstructionVehicle"
        elif(categoryName == "vehicle.emergency.ambulance"):
            categoryDict[categoryToken] = "EmergencyAmbulance"
        elif(categoryName == "vehicle.emergency.police"):
            categoryDict[categoryToken] = "EmergencyPolice"
        elif(categoryName == "vehicle.trailer"):
            categoryDict[categoryToken] = "Trailer"
        elif(categoryName == "movable_object.barrier"):
            categoryDict[categoryToken] = "Barrier"
        elif(categoryName == "movable_object.trafficcone"):
            categoryDict[categoryToken] = "TrafficCone"
        elif(categoryName == "movable_object.pushable_pullable"):
            categoryDict[categoryToken] = "PushablePullable"
        elif(categoryName == "movable_object.debris"):
            categoryDict[categoryToken] = "Debris"
        elif(categoryName == "static_object.bicycle_rack"):
            categoryDict[categoryToken] = "BicycleRack"
        #print(categoryToken, categoryDict[categoryToken])
    #print(categoryDict)

# Create a dictionary for the instances 
# instanceDict{instance_token: category} using: instanceDict{instance_token: categoryDict{category_token}
file = os.path.join(path,'instance.json')
instanceDict = {}
if os.path.isfile(file):
    print(file)
    df = pd.read_json(file)
    for entry in df.itertuples(): 
        instanceToken = entry.token
        categoryToken = entry.category_token
        categoryName = categoryDict[categoryToken]
        #print("CategoryName Token: ", categoryName, categoryToken)
        instanceDict[instanceToken] = categoryName
        #print(instanceToken, instanceDict['instanceToken'] )

# Continue with the other files
for f in os.listdir(path):
    if not f.endswith(".json"):
        continue
    file = os.path.join(path,f)
    if os.path.isfile(file):
        print(file)
        df = pd.read_json(file)

        # MAP
        if(f == 'map.json'):
            # for entry in data:  
            for entry in df.itertuples(): 
                #token = entry['token']
                #mapFileName = entry['filename'] 
                #logTokens = entry['log_tokens']
                token = entry.token
                mapFileName = entry.filename
                logTokens = entry.log_tokens

                mapURI = NS[f"Map_{token}"]
                rdf.add((rdflib.URIRef(mapURI), rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), rdflib.URIRef(NS['Map'])))
                rdf.add((rdflib.URIRef(mapURI), rdflib.URIRef(NS["hasFilename"]), Literal(mapFileName))) 
                for trip in logTokens:
                    rdf.add((rdflib.URIRef(mapURI), rdflib.URIRef(NS["hasTrip"]), rdflib.URIRef(NS[f"Trip_{trip}"])))

        # Trip (log) 
        elif(f == 'log.json'):
            # for entry in data:  
            for entry in df.itertuples(): 
                token = entry.token
                logfile = entry.logfile
                vehicle = entry.vehicle
                date_captured = entry.date_captured
                location = entry.location

                tripURI = NS[f"Trip_{token}"]
                rdf.add((rdflib.URIRef(tripURI), rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), rdflib.URIRef(NS['Trip'])))
                rdf.add((rdflib.URIRef(tripURI), rdflib.URIRef(NS["hasLogfile"]), Literal(logfile)))
                rdf.add((rdflib.URIRef(tripURI), rdflib.URIRef(NS["hasEgoVehicle"]), rdflib.URIRef(NS[f"Vehicle_{vehicle}"])))
                rdf.add((rdflib.URIRef(tripURI), rdflib.URIRef(NS["hasDate"]), Literal(date_captured)))
                rdf.add((rdflib.URIRef(tripURI), rdflib.URIRef(NS["hasLocation"]), rdflib.URIRef(NS[f"Location_{location}"])))
                rdf.add((rdflib.URIRef(NS[f"Vehicle_{vehicle}"]), rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), rdflib.URIRef(NS['EgoVehicle'])))
                rdf.add((rdflib.URIRef(NS[f"Location_{location}"]), rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), rdflib.URIRef(NS['Location'])))

        # Sequence (scene)
        elif(f == 'scene.json'):
            # for entry in data:  
            for entry in df.itertuples(): 
                token = entry.token
                log_token = entry.log_token
                nbr_samples = entry.nbr_samples
                first_sample_token = entry.first_sample_token
                last_sample_token = entry.last_sample_token
                name = entry.name
                description = entry.description

                sequenceURI = NS[f"Sequence_{token}"]
                rdf.add((rdflib.URIRef(sequenceURI), rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), rdflib.URIRef(NS['Sequence'])))
                rdf.add((rdflib.URIRef(NS[f"Trip_{log_token}"]), rdflib.URIRef(NS["hasSequence"]), rdflib.URIRef(sequenceURI)))              
                rdf.add((rdflib.URIRef(sequenceURI), rdflib.URIRef(NS["hasNbrScenes"]), Literal(nbr_samples, datatype=XSD.int)))
                rdf.add((rdflib.URIRef(sequenceURI), rdflib.URIRef(NS["hasFirstScene"]), rdflib.URIRef(NS[f"Scene_{first_sample_token}"])))
                rdf.add((rdflib.URIRef(sequenceURI), rdflib.URIRef(NS["hasLastScene"]), rdflib.URIRef(NS[f"Scene_{last_sample_token}"])))
                rdf.add((rdflib.URIRef(sequenceURI), rdflib.URIRef(NS["hasName"]), Literal(name)))
                rdf.add((rdflib.URIRef(sequenceURI), rdflib.URIRef(NS["hasDescription"]), Literal(description)))

        # Scene (sample)
        elif(f == 'sample.json'):
            # for entry in data:  
            for entry in df.itertuples(): 
                sceneToken = entry.token
                timestamp = entry.timestamp
                prev = entry.prev
                next = entry.next
                sequenceToken = entry.scene_token

                sceneURI = NS[f"Scene_{sceneToken}"]
                rdf.add((rdflib.URIRef(sceneURI), rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), rdflib.URIRef(NS['Scene'])))
                rdf.add((rdflib.URIRef(sceneURI), rdflib.URIRef(NS["hasTimestamp"]), Literal(timestamp, datatype=XSD.dateTime)))
                rdf.add((rdflib.URIRef(sceneURI), rdflib.URIRef(NS["hasPreviousScene"]), rdflib.URIRef(NS[f"Scene_{prev}"])))
                rdf.add((rdflib.URIRef(sceneURI), rdflib.URIRef(NS["hasNextScene"]), rdflib.URIRef(NS[f"Scene_{next}"])))
                rdf.add((rdflib.URIRef(NS[f"Sequence_{sequenceToken}"]), rdflib.URIRef(NS["hasScene"]), rdflib.URIRef(sceneURI)))

        # Participant
        elif(f == 'sample_annotation.json'):
            # for entry in data:  
            for entry in df.itertuples(): 
                token = entry.token  # this is the sample annotation token
                sceneToken = entry.sample_token
                instanceToken = entry.instance_token
                visibility = entry.visibility_token
                attributes = entry.attribute_tokens
                translation = entry.translation
                size = entry.size
                rotation = entry.rotation
                nbrLidar = entry.num_lidar_pts
                nbrRadar = entry.num_radar_pts

                category = instanceDict[instanceToken]

                participantURI = NS[f"Participant_{instanceToken}"]
                participantSnapshotURI = NS[f"ParticipantSnapshot_{token}"]
                rdf.add((rdflib.URIRef(NS[f"Scene_{sceneToken}"]), rdflib.URIRef(NS["hasParticipant"]), rdflib.URIRef(participantSnapshotURI)))             
                rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasVisibility"]), Literal(visibility, datatype=XSD.int)))
                rdf.add((rdflib.URIRef(participantURI), rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), rdflib.URIRef(NS[category])))  # called multiple times, but rdf.add is idempotent
                rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["isSnapshotOf"]), rdflib.URIRef(participantURI)))

                # State (attribute)
                for att in attributes:  #### Can there be more than one attribute (states) ????
                    if(att == "cb5118da1ab342aa947717dc53544259"):
                        rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasState"]), rdflib.URIRef(NS["VehicleMoving"])))   #???
                    elif(att == "c3246a1e22a14fcb878aa61e69ae3329"):
                        rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasState"]), rdflib.URIRef(NS["VehicleStopped"])))
                    elif(att == "58aa28b1c2a54dc88e169808c07331e3"):
                        rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasState"]), rdflib.URIRef(NS["VehicleParked"])))
                    elif(att == "a14936d865eb4216b396adae8cb3939c"):
                        rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasState"]), rdflib.URIRef(NS["CycleWithRider"])))
                    elif(att == "5a655f9751944309a277276b8f473452"):
                        rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasState"]), rdflib.URIRef(NS["CycleWithoutRider"])))
                    elif(att == "03aa62109bf043afafdea7d875dd4f43"):
                        rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasState"]), rdflib.URIRef(NS["PedestrianSittingLyingDown"])))
                    elif(att == "4d8821270b4a47e3a8a300cbec48188e"):
                        rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasState"]), rdflib.URIRef(NS["PedestrianStanding"])))
                    elif(att == "ab83627ff28b465b85c427162dec722f"):
                        rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasState"]), rdflib.URIRef(NS["PedestrianMoving"])))
                    else:
                        print("Error, unknown state for attribute pattern: ", att)

                # Translation
                elements = ""
                for element in translation:
                    elements = elements+str(element)+", "
                rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS[f"hasTranslation"]), Literal(elements[:-2])))
                # Size
                elements = ""
                for element in size:
                    elements = elements+str(element)+", "
                rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS[f"hasSize"]), Literal(elements[:-2])))
                # Rotation
                elements = ""
                for element in rotation:
                    elements = elements+str(element)+", "
                rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS[f"hasRotation"]), Literal(elements[:-2])))
                # Num Lidar Points
                rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasNumLidarPts"]), Literal(nbrLidar, datatype=XSD.int)))
                # Num Radar Points
                rdf.add((rdflib.URIRef(participantSnapshotURI), rdflib.URIRef(NS["hasNumRadarPts"]), Literal(nbrRadar, datatype=XSD.int)))
                batch_rdf_serialization(8)

        # Data (sample data)
        elif(f == 'sample_data.json'):
            # for entry in data:  
            for entry in df.itertuples(): 
                token = entry.token 
                sceneToken = entry.sample_token 
                #egoPoseToken = entry['ego_pose_token 
                calibToken = entry.calibrated_sensor_token 
                timestamp = entry.timestamp 
                fileformat = entry.fileformat 
                isKeyFrame = entry.is_key_frame 
                height = entry.height 
                width = entry.width 
                filename = entry.filename 
                
                dataURI = NS[f"Data_{token}"]
                rdf.add((rdflib.URIRef(dataURI), rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), rdflib.URIRef(NS['Data'])))
                rdf.add((rdflib.URIRef(NS[f"Scene_{sceneToken}"]), rdflib.URIRef(NS["hasData"]), rdflib.URIRef(dataURI)))
                rdf.add((rdflib.URIRef(NS[f"Calibration_{calibToken}"]), rdflib.URIRef(NS["hasObservation"]), rdflib.URIRef(dataURI)))
                rdf.add((rdflib.URIRef(dataURI), rdflib.URIRef(NS["hasTimestamp"]), Literal(timestamp)))
                rdf.add((rdflib.URIRef(dataURI), rdflib.URIRef(NS["hasFileformat"]), Literal(fileformat)))
                rdf.add((rdflib.URIRef(dataURI), rdflib.URIRef(NS["isKeyframe"]), Literal(isKeyFrame, datatype=XSD.boolean)))
                rdf.add((rdflib.URIRef(dataURI), rdflib.URIRef(NS["hasPixelHeight"]), Literal(height, datatype=XSD.int)))
                rdf.add((rdflib.URIRef(dataURI), rdflib.URIRef(NS["hasPixelWidth"]), Literal(width, datatype=XSD.int)))
                rdf.add((rdflib.URIRef(dataURI), rdflib.URIRef(NS["hasFilename"]), Literal(filename)))
                batch_rdf_serialization(10)

        # Ego Pose
        elif(f == 'ego_pose.json'):
            # for entry in data:  
            for entry in df.itertuples(): 
                token = entry.token 
                translation = entry.translation 
                rotation = entry.rotation 

                # ego_pose and sample_data share the same token-numbers -> translation and rotation are added to sample data using ego-pose token.
                dataURI = NS[f"Data_{token}"] 

                # Translation
                elements = ""
                for element in translation:
                    elements = elements+str(element)+", "
                rdf.add((rdflib.URIRef(dataURI), rdflib.URIRef(NS[f"hasTranslation"]), Literal(elements[:-2])))
                # Rotation
                elements = ""
                for element in rotation:
                    elements = elements+str(element)+", "
                rdf.add((rdflib.URIRef(dataURI), rdflib.URIRef(NS[f"hasRotation"]), Literal(elements[:-2])))
                batch_rdf_serialization(5)

        # Calibration (calibrated_sensor)
        elif(f == 'calibrated_sensor.json'):
            for entry in df.itertuples(): 
                token = entry.token 
                sensorToken = entry.sensor_token 
                translation = entry.translation 
                rotation = entry.rotation 
                camIntrinsic = entry.camera_intrinsic 

                calibURI = NS[f"Calibration_{token}"] 
                rdf.add((rdflib.URIRef(calibURI), rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), rdflib.URIRef(NS['Calibration'])))
                rdf.add((rdflib.URIRef(NS[f"Sensor_{sensorToken}"]), rdflib.URIRef(NS["hasCalibration"]), rdflib.URIRef(calibURI)))

                # Translation
                elements = ""
                for element in translation:
                    elements = elements+str(element)+", "
                rdf.add((rdflib.URIRef(calibURI), rdflib.URIRef(NS[f"hasTranslation"]), Literal(elements[:-2])))
                # Rotation
                elements = ""
                for element in rotation:
                    elements = elements+str(element)+", "
                rdf.add((rdflib.URIRef(calibURI), rdflib.URIRef(NS[f"hasRotation"]), Literal(elements[:-2])))
                # Camera Intrinsic: [3 x 3]
                elements = ""
                for element in camIntrinsic:
                    elements = elements+str(element)+", "
                if(elements):
                    rdf.add((rdflib.URIRef(calibURI), rdflib.URIRef(NS[f"hasCameraIntrinsic"]), Literal(elements[:-2])))
        # Sensor
        elif(f == 'sensor.json'):
            for entry in df.itertuples(): 
                token = entry.token 
                channel = entry.channel 
                modality = entry.modality 

                sensorURI = NS[f"Sensor_{token}"] 
                rdf.add((rdflib.URIRef(sensorURI), rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), rdflib.URIRef(NS['Sensor'])))
                rdf.add((rdflib.URIRef(sensorURI), rdflib.URIRef(NS[f"hasChannel"]), Literal(channel)))
                rdf.add((rdflib.URIRef(sensorURI), rdflib.URIRef(NS[f"hasModality"]), Literal(modality)))

# write final triples 
rdf_serialization()

print("Processing time: ", (time.process_time() - processTime))
print("Absolut time (Minutes):    ", ((time.time() - actualTime)/60))
