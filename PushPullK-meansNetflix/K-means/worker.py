import zmq
import math
import numpy as np

def calculateNorm(d):
    n = [None for _ in range(len(d))]
    count = 0
    for i in d:
        value = 0
        for j in i:
            value += pow(i[j], 2)
        n[count] = math.sqrt(value)
        count += 1
    return n

class Worker:
    
    def __init__(self):
        self.context = zmq.Context()
        self.ventilator = self.context.socket(zmq.PULL)
        self.ventilator.connect('tcp://localhost:7555')
        self.sink = self.context.socket(zmq.PUSH)
        self.sink.connect('tcp://localhost:7556')

    def run(self):
        while True:
            message = self.ventilator.recv_json()
            data = self.readFile(message['part'])
            self.nFeatures = int(message['nFeatures'])
            sumPoints, inertias, sizes = self.assignment(data, message['clusters'], message['normaClusters'])
            self.sink.send_json({
                'sumPoints': np.ndarray.tolist(sumPoints), 
                'inertias': inertias,
                'sizes': sizes,
                'part': message['part']
            })

    def assignment(self, data, clusters, normaClusters):
        clusters = np.asarray(clusters, dtype= float)        
        inertias = 0
        sizes = [0] * len(clusters)
        sumPoints = np.zeros((len(clusters), self.nFeatures + 1))
        pointsNorm = calculateNorm(data)
        for p, point in enumerate(data):
            positionCluster = None
            miniDistance = np.inf
            for j, cluster in enumerate(clusters):
                distance = self.coss(point, cluster, pointsNorm[p], normaClusters[j])
                if distance < miniDistance:
                    positionCluster = j
                    miniDistance = distance
            for key in point.keys():
                sumPoints[positionCluster][int(key)] += point[key]
            sizes[positionCluster] += 1
            inertias += miniDistance
        return (sumPoints, inertias, sizes)

    def coss(self, point, centroId, normaPoint, normaCentroId):
        dot = 0
        for key in point:
            dot += float(point.get(key, 0)) * centroId[int(key)]
        sim = dot / (normaPoint * normaCentroId)
        if abs(sim - 1.0) <= 1e-4:
            sim = 1.0
        elif abs(sim + 1.0) <= 1e-4:
            sim = -1.0
        sim = np.arccos(sim)
        return sim

    def readFile(self, part):
        dataFile = []
        file = open(f'dataFiles/part{part}.txt', 'r')
        for line in file:
            line = line[:-1]
            d = {}
            sp = line.split(',')
            for i in sp:
                i = i[1:-1].split(' ')
                d[i[0]] = int(i[1])
            dataFile.append(d)
        return dataFile

if __name__ == '__main__':
    worker = Worker()
    worker.run()
