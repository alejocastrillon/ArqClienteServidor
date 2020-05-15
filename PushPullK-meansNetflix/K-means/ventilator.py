import zmq
import math
import copy
import random
import os
import difflib
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
        self.numberTasks = 100
        self.maximeIteration = 1000
        self.numberTotalTasks = quantityOfFiles()
        self.context = zmq.Context()
        self.sinkPush = self.context.socket(zmq.PUSH)
        self.sinkPull = self.context.socket(zmq.PULL)
        self.workers = self.context.socket(zmq.PUSH)
        self.sinkPush.connect('tcp://localhost:7556')
        self.sinkPull.bind('tcp://*:7557')
        self.workers.bind('tcp://*:7555')
        self.clusters = self.generateClusters()
        self.tolerance = 10

    def run(self):
        print('Para lanzar la tarea, asegurese que los workers esten habilitados. Si es asi, presione la tecla ENTER')
        input()
        print('Enviando tareas')
        iteration = 0
        finished = False
        newClusters = copy.deepcopy(self.clusters)
        while not finished:
            #print(newClusters)
            print('Inercia: {}'.format(self.calculateInertia(newClusters)))
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
                    'part': i
                }
                self.workers.send_json(dataWork)
            response = self.sinkPull.recv_json()
            newClusters = response['clusters']
            if self.compare(newClusters):
                finished = True
                return self.calculateInertia(newClusters)
            elif iteration > self.maximeIteration:
                print('Limite de iteraciones')
                self.sinkPush.send_json({
                    'finished': 'true'
                })
                break
            else:
                self.clusters = copy.deepcopy(newClusters)
                iteration += 1
        print('Finished')
        print(self.clusters)
        return self.calculateInertia(self.clusters)

    def compare(self, newClusters):
        for i in range(len(newClusters)):
            if not 'dataset' in self.clusters[i]:
                return False;
            ratio = difflib.SequenceMatcher(newClusters[i]['dataset'], self.clusters[i]['dataset']).ratio()
            if (1-ratio)*100 > self.tolerance:
                return False;
        return True

    def calculateInertia(self, newClusters):
        inertia = 0
        for cluster in newClusters:
            for key in cluster.keys():
                if key == 'inertia':
                    inertia += cluster[key]
        return inertia

    def generateClusters(self):
        clusters = []
        for i in range(self.k):
            clus = random.randint(0,self.numberTotalTasks - 1)
            with open(f"dataFiles/part{clus}.txt", "r") as file:
                for _ in range((random.randint(1, 100))-1):
                    file.readline()
                line = parseLine(file.readline())
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
    numberClusters = [20, 15, 10, 5]
    inertiaValues = []
    for kCluster in numberClusters:
        fan = Fan(kCluster)
        #fan.run()
        inertiaValues.append(fan.run())
    print(numberClusters)
    print(inertiaValues)
