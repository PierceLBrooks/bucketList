
import re
import os
import sys
import csv
import json
import mmds
import random
import logging
import traceback

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
            for i in range(dimensions):
                bounds.append(int(sys.argv[2+i]))
            cities = []
            with open(sys.argv[1], "r") as descriptor:
                lines = descriptor.readlines()
                descriptor.close()
                for line in lines:
                    city = line.strip()
                    if (city in cities):
                        continue
                    cities.append(city)
            print(str(cities))
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
            space = mmds.Space(frame)
            print(str(space.ndim))
            active = space.active
            target += ".csv"
            with open(target, "w") as descriptor:
                descriptor.write(active.to_csv())
                descriptor.close()
            vectors = {}
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
                        vector.append(float(row[keys[i]]))
                    vectors[row[key]] = vector
except:
    logging.error(traceback.format_exc())

