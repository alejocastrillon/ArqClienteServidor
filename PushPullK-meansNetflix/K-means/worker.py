import zmq
import math

def calculateNorm(d):
    n = [None for _ in range(len(d))]
    count = 0
    for i in d:
        value = 0
        if 'dataset' in i:
            i.pop('dataset')
        if 'inertia' in i:
            i.pop('inertia')
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
            resultAssign = self.assignment(data, message['clusters'])
            self.sink.send_json({'assign': resultAssign, 'part': message['part']})

    def assignment(self, data, clusters):
        matrixWorker = [{'dataset': [], 'inertia': 0} for _ in range(len(clusters))]
        pointsNorm = calculateNorm(data)
        clustersNorm = calculateNorm(clusters)
        print(clustersNorm)
        for p, point in enumerate(data):
            positionCluster = 0
            miniDistance = 0.0-2.0
            for j, cluster in enumerate(clusters):
                distance = self.coss(point, cluster, pointsNorm[p], clustersNorm[j])
                if distance > miniDistance:
                    positionCluster = j
                    miniDistance = distance
            for value in point:
                ass = matrixWorker[positionCluster].get(value)
                if ass:
                    matrixWorker[positionCluster][value][0] += point[value]
                    matrixWorker[positionCluster][value][1] += 1
                else:
                    matrixWorker[positionCluster][value] = [point[value], 1]
            matrixWorker[positionCluster]['dataset'].append(p)
            if miniDistance > 1:
                miniDistance = 1
            #print(f"Distance {miniDistance} ->Arccos {math.acos(miniDistance)}")
            matrixWorker[positionCluster]['inertia'] += miniDistance
        #print([f"Cluster {i} = {len(matrixWorker[i]['dataset'])}, inercia = {matrixWorker[i]['inertia']}" for i in range(len(matrixWorker))])
        return matrixWorker

    def coss(self, point, anotherPoint, normaPoint, normaAnotherPoint):
        data = point if len(point) <= len(anotherPoint) else anotherPoint
        dot = 0
        for key in data.keys():
            dot += int(point.get(key, 0)) * int(anotherPoint.get(key, 0))
        sim = dot / (normaPoint * normaAnotherPoint)
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