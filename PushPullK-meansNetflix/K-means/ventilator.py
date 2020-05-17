import zmq
import math
import copy
import random
import os
import matplotlib.pyplot as plt
import numpy as np
import time

def quantityOfFiles():
    i = 0
    for file in os.listdir('./dataFiles'):
        if 'part' in file:
            i += 1
    return i

def calculateNorm(d):
    n = [None for _ in range(len(d))]
    count = 0
    for i in d:
        value = 0
        for j in i:
            value += pow(j, 2)
        n[count] = math.sqrt(value)
        count += 1
    return n

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
        self.maximeIteration = 1000
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
        self.tolerance = 3
        self.inertiasCluster = []

    def run(self):
        iteration = 0
        finished = False
        newClusters = copy.deepcopy(self.clusters)
        normaClusters = calculateNorm(newClusters)
        while not finished:
            #print(newClusters)
            print('Inercia: {}'.format(self.calculateInertia()))
            print('Iteracion {}'.format(iteration))
            dataSink = {
                'numberTasks': self.numberTasks,
                'totalTasks': self.numberTotalTasks,
                'clusters': len(self.clusters)
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
            newnormaClusters = calculateNorm(newClusters)
            self.inertiasCluster = response['inertias']
            if self.compare(newClusters, normaClusters, newnormaClusters):
                finished = True
                self.closeConnection()
                return self.calculateInertia()
            elif iteration > self.maximeIteration:
                print('Limite de iteraciones')
                self.sinkPush.send_json({
                    'finished': 'true'
                })
                self.closeConnection()
                return self.calculateInertia()
                break
            else:
                self.clusters = copy.deepcopy(newClusters)
                normaClusters = calculateNorm(self.clusters)
                iteration += 1
        print('Finished')
        print(self.clusters)
        self.closeConnection()
        return self.calculateInertia()

    def coss(self, point, centroId, normaPoint, normaCentroId):
        dot = 0
        for key in range(self.nFeatures + 1):
            dot += point[key] * centroId[key]
        sim = dot / (normaPoint * normaCentroId)
        if sim > 1:
            sim = 1
        elif sim < -1:
            sim = -1
        sim = np.arccos(sim)
        return sim

    def compare(self, newClusters, normaClusters, newnormaClusters):
        prom = 0
        for i in range(len(newClusters)):
            prom += self.coss(newClusters[i], self.clusters[i], newnormaClusters[i], normaClusters[i])
        prom = (((prom / len(newClusters)) * 180) / math.pi)
        print(prom)
        if prom < self.tolerance:
            return True
        return False

    def calculateInertia(self):
        totalInertia = 0
        for inertia in self.inertiasCluster:
            totalInertia += inertia
        return totalInertia

    def validateIndex(self, indices, dataIndex):
        if dataIndex in indices:
            self.validateIndex(indices, [random.randint(0, self.numberTotalTasks - 1), random.randint(1, 999)])
        else:
            return dataIndex;

    def closeConnection(self):
        self.workers.close()
        self.sinkPull.close()
        self.context.destroy()


    def createCentroId(self, point):
        centroid = [0] * (self.nFeatures + 1)
        for key in point.keys():
            centroid[int(key)] = point[key]
        return centroid

    def generateClusters(self):
        dataIndex = []
        for _ in range(self.k):
            dataIndex.append(self.validateIndex(dataIndex, [random.randint(0, self.numberTotalTasks - 1), random.randint(1, 999)]))
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
    numberClusters = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
    inertiaValues = []
    for kCluster in numberClusters:
        fan = Fan(20)
        data = fan.run()
        print('Inercia Resultante {}:'.format(kCluster), data)
        inertiaValues.append(data)
    print(numberClusters)
    print(inertiaValues)
    plt.plot(numberClusters, inertiaValues)
    plt.ylabel('Inercia')
    plt.xlabel('Centroides')
    plt.show()
