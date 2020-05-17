import sys
import time
import zmq
import numpy as np


class Sink:
    def __init__(self):
        self.context = zmq.Context()
        self.send = self.context.socket(zmq.PUSH)
        self.send.connect('tcp://localhost:7558')
        self.recv = self.context.socket(zmq.PULL)
        self.recv.bind('tcp://*:7556')

    def start(self):
        while True:
            message = self.recv.recv_json()
            if 'finished' in message:
                return
            if 'totalTasks' in message:
                self.clusters = message['clusters']
                sumPoints = None
                inertias = [0] * self.clusters
                sizes = [0] * self.clusters
            for task in range(message['totalTasks']):
                response = self.recv.recv_json()
                sumPointsTemp = np.asarray(response['sumPoints'])
                if sumPoints.__class__.__name__ == 'NoneType':
                    sumPoints = np.zeros(sumPointsTemp.shape)
                inertiasTemp = response['inertias']
                sizesTemp = response['sizes']
                for c in range(self.clusters):
                    sumPoints[c] += sumPointsTemp[c]
                    inertias[c] += inertiasTemp[c]
                    sizes[c] += sizesTemp[c]
            clusters = self.newAssignment(sumPoints, sizes)
            self.send.send_json({
                'clusters': clusters,
                'inertias': inertias
            })

    def newAssignment(self, newClusters, sizes):
        for i in range(self.clusters):
            newClusters[i] = newClusters[i] / sizes[i]
        return np.ndarray.tolist(newClusters)

if __name__ == '__main__':
    sink = Sink()
    sink.start()