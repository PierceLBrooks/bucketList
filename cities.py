
import re
import os
import sys
import csv
import json
import math
import mmds
import random
import logging
import traceback
import numpy as np

def get_distance(left, right):
    distance = 0.0
    for i in range(len(left)):
        distance += (left[i]-right[i])**2.0
    return distance**0.5

try:
    if (__name__ == "__main__"):
        print(str(sys.argv))
        if (len(sys.argv) > 4):
            dimensions = int(sys.argv[2])
            if (dimensions < 2):
                sys.exit()
            bounds = []
            minimums = []
            maximums = []
            for i in range(dimensions):
                bounds.append(int(sys.argv[3+i]))
                minimums.append(math.inf)
                maximums.append(-math.inf)
            cities = []
            with open(sys.argv[1], "r") as descriptor:
                lines = descriptor.readlines()
                descriptor.close()
                for line in lines:
                    city = line.strip()
                    if (city in cities):
                        continue
                    cities.append(city)
            roads = {}
            for city in cities:
                if not (city in roads):
                    roads[city] = {}
                for other in cities:
                    if not (other in roads):
                        roads[other] = {}
                    if (city == other):
                        roads[city][other] = True
                        continue
                    if (float(random.randint(0, len(cities))) < (float(len(cities))**0.5)*0.5):
                        roads[city][other] = True
                        roads[other][city] = True
                    else:
                        roads[city][other] = False
                        roads[other][city] = False
            if not (os.path.exists(sys.argv[1]+".csv")):
                positions = {}
                for city in cities:
                    position = []
                    for dimension in range(dimensions):
                        position.append(float(random.randint(0, bounds[dimension])))
                    positions[city] = position
                distances = {}
                for city in cities:
                    for other in cities:
                        left = positions[city]
                        right = positions[other]
                        distance = get_distance(left, right)
                        print(city+" -> "+other+" = "+str(distance))
                        if not (city in distances):
                            distances[city] = {}
                        if not (other in distances):
                            distances[other] = {}
                        distances[city][other] = distance
                        distances[other][city] = distance
                with open(sys.argv[1]+".csv", "w") as descriptor:
                    descriptor.write("left,right,distance\n")
                    for key in distances:
                        for other in distances:
                            descriptor.write(key+","+other+","+str(distances[key][other])+"\n")
                    descriptor.close()
            distances = {}
            with open(sys.argv[1]+".csv", "r") as descriptor:
                reader = csv.DictReader(descriptor)
                for row in reader:
                    left = row["left"]
                    right = row["right"]
                    distance = row["distance"]
                    if not (left in distances):
                        distances[left] = {}
                    distances[left][left] = 0
                    if not (right in distances[left]):
                        distances[left][right] = float(distance)
                    temp = left
                    left = right
                    right = temp
                    if not (left in distances):
                        distances[left] = {}
                    distances[left][left] = 0
                    if not (right in distances[left]):
                        distances[left][right] = float(distance)
                descriptor.close()
            target = os.path.join(os.getcwd(), sys.argv[0]+".tsv")
            with open(target, "w") as descriptor:
                columns = []
                rows = []
                line = ""
                for key in distances:
                    column = key.strip()
                    line += column+"\t"
                    #columns.append(column)
                descriptor.write("\t"+line.strip()+"\n")
                for key in distances:
                    row = key.strip()
                    line = row+"\t"
                    rows.append(row)
                    for other in distances:
                        if (other == key):
                            line += "0.0\t"
                            continue
                        if not (other in distances[key]):
                            line += "1.0\t"
                            continue
                        line += str(distances[key][other])+"\t"
                    descriptor.write(line.strip()+"\n")
                descriptor.close()
            frame = mmds.read_dm(target)
            space = mmds.Space(frame, dimensions)
            print(str(space.ndim))
            active = space.active
            target += ".csv"
            with open(target, "w") as descriptor:
                descriptor.write(active.to_csv())
                descriptor.close()
            vectors = []
            cities = []
            size = 0
            with open(target, "r") as descriptor:
                reader = csv.DictReader(descriptor)
                for row in reader:
                    keys = list(row.keys())
                    if (len(keys) < 2):
                        continue
                    key = keys[0]
                    keys = keys[1:]
                    size = len(keys)
                    vector = []
                    for i in range(len(keys)):
                        if (i > dimensions):
                            break
                        vector.append(float(row[keys[i]]))
                        if (vector[i] > maximums[i]):
                            maximums[i] = vector[i]
                        if (vector[i] < minimums[i]):
                            minimums[i] = vector[i]
                    vectors.append(vector)
                    cities.append(row[key])
            for i in range(len(vectors)):
                vector = vectors[i]
                for j in range(len(vector)):
                    vector[j] = ((vector[j]-minimums[j])/(maximums[j]-minimums[j]))*float(bounds[j])
                vectors[i] = vector
            target += ".dot"
            writes = []
            with open(target, "w") as descriptor:
                descriptor.write("graph G {\n")
                for i in range(len(cities)):
                    descriptor.write("\t"+cities[i]+" [pos=\""+str(int(vectors[i][0]))+","+str(int(vectors[i][1]))+"\"]\n")
                    road = 0
                    for city in cities:
                        if (city == cities[i]):
                            continue
                        if (roads[city][cities[i]]):
                            road += 1
                            if ((city+cities[i] in writes) or (cities[i]+city in writes)):
                                continue
                            writes.append(city+cities[i])
                            descriptor.write("\t"+cities[i]+" -- "+city+"\n")
                    if (road == 0):
                        descriptor.write("\t"+cities[i]+" -- "+cities[random.randint(0, len(cities)-1)]+"\n")
                descriptor.write("}\n")
                descriptor.close()
except:
    logging.error(traceback.format_exc())

