import zmq
import math
import copy
import random
import os
import matplotlib.pyplot as plt
import copy
import numpy as np
import time

def quantityOfFiles():
    i = 0
    for file in os.listdir('./dataFiles'):
        if 'part' in file:
            i += 1
    return i

def parseLine(data):
    data = data[:-1]
    cluster = {}
    listItems = data.split(',')
    for items in listItems:
        items = items[1:-1].split(' ')
        #cluster[items[0]] = int(items[1]) + random.randint(0, 100)
        cluster[items[0]] = random.randint(1, 5)
    return cluster

class Fan:
    
    def __init__(self, k):
        self.k = k
        self.numberTasks = 1000
        self.maximeIteration = 30
        self.numberTotalTasks = quantityOfFiles()
        self.context = zmq.Context()
        self.sinkPush = self.context.socket(zmq.PUSH)
        self.sinkPull = self.context.socket(zmq.PULL)
        self.workers = self.context.socket(zmq.PUSH)
        self.sinkPush.connect('tcp://localhost:7556')
        self.sinkPull.bind('tcp://*:7558')
        self.workers.bind('tcp://*:7555')
        self.nFeatures = 4499
        self.clusters = self.generateClusters()
        self.tolerance = 3 * math.pi / 180

    def run(self):
        iteration = 0
        finished = False
        newClusters = copy.deepcopy(self.clusters)
        normaClusters = [np.linalg.norm(cluster) for cluster in self.clusters]
        while not finished:
            print('Iteracion {}'.format(iteration))
            dataSink = {
                'numberTasks': self.numberTasks,
                'totalTasks': self.numberTotalTasks,
                'clusters': len(self.clusters),
                'nFeatures': self.nFeatures
            }
            self.sinkPush.send_json(dataSink)
            for i in range(self.numberTotalTasks):
                dataWork = {
                    'clusters': newClusters,
                    'normaClusters': normaClusters,
                    'nFeatures': self.nFeatures,
                    'part': i
                }
                self.workers.send_json(dataWork)
            response = self.sinkPull.recv_json()
            newClusters = response['clusters']
            inertia = response['inertia']
            print('Inercia: {}'.format(inertia))
            if self.compare(newClusters, normaClusters):
                finished = True
                return inertia
            elif iteration > self.maximeIteration:
                print('Limite de iteraciones')
                self.sinkPush.send_json({
                    'finished': 'true'
                })
                return inertia
            else:
                self.clusters = copy.deepcopy(newClusters)
                normaClusters = [np.linalg.norm(cluster) for cluster in self.clusters]
                iteration += 1

    def coss(self, point, centroId, normaPoint, normaCentroId):
        dot = point.dot(centroId.T)
        sim = dot / (normaPoint * normaCentroId)
        if abs(sim - 1.0) <= 1e-4:
            sim = 1.0
        elif abs(sim + 1.0) <= 1e-4:
            sim = -1.0
        sim = np.arccos(sim)
        return sim

    def compare(self, newClusters, normaClusters):
        distance = 0
        for i in range(len(newClusters)):
            normCentroId = np.linalg.norm(newClusters[i])
            distance += self.coss(np.asarray(newClusters[i]), np.asarray(self.clusters[i]), normaClusters[i], normCentroId)
        distance = distance / len(newClusters)
        print(f"Average Distance in degrees {distance * 180 / np.pi}")
        print(distance, self.tolerance)
        return distance < self.tolerance

    def validateIndex(self, indices, dataIndex):
        if dataIndex in indices:
            self.validateIndex(indices, [random.randint(0, self.numberTotalTasks - 1), random.randint(1, 998)])
        else:
            return dataIndex;

    def closeConnection(self):
        self.sinkPull.close()
        self.workers.close()
        self.context.destroy()


    def createCentroId(self, point):
        centroid = [0] * (self.nFeatures + 1)
        for key in point.keys():
            centroid[int(key)] = point[key]
        return centroid

    def generateClusters(self):
        dataIndex = []
        for _ in range(self.k):
            dataIndex.append(self.validateIndex(dataIndex, [random.randint(0, self.numberTotalTasks - 1), random.randint(1, 998)]))
        clusters = []
        for data in dataIndex:
            with open(f"dataFiles/part{data[0]}.txt", "r") as file:
                for _ in range(data[1]):
                    file.readline()
                line = self.createCentroId(parseLine(file.readline()))
            clusters.append(line)
        return clusters

    """ def generateClusters(self):
        clusters = []
        
        for i in range(self.k):

            clus = random.randint(0,self.numberTotalTasks - 1)
            with open(f"dataFiles/part{clus}.txt", "r") as file:
                for _ in range((random.randint(1, 100))-1):
                    file.readline()
                line = parseLine(file.readline())
            clusters.append(line)
        return clusters
 """
    
if __name__ == '__main__':
    print('Para lanzar la tarea, asegurese que los workers esten habilitados. Si es asi, presione la tecla ENTER')
    input()
    print('Enviando tareas')
    numberClusters = [125, 175]
    inertiaValues = []
    for kCluster in numberClusters:
        fan = Fan(kCluster)
        data = copy.deepcopy(fan.run())
        fan.closeConnection()
        del fan
        print('Inercia Resultante {}:'.format(kCluster), data)
        inertiaValues.append(data)
    print(numberClusters)
    print(inertiaValues)
    plt.plot(numberClusters, inertiaValues, 'ro')
    plt.ylabel('Inercia')
    plt.xlabel('Centroides')
    plt.show()
