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
                self.nFeatures = message['nFeatures']
                sumPoints = np.zeros((self.clusters, self.nFeatures + 1))
                inertia = 0
                sizes = [0] * self.clusters
            for task in range(message['totalTasks']):
                response = self.recv.recv_json()
                sumPointsTemp = np.asarray(response['sumPoints'])
                inertiaTemp = response['inertias']
                sizesTemp = response['sizes']
                inertia += inertiaTemp
                for c in range(self.clusters):
                    sumPoints[c] += sumPointsTemp[c]
                    sizes[c] += sizesTemp[c]
            clusters = self.newAssignment(sumPoints, sizes)
            self.send.send_json({
                'clusters': clusters,
                'inertia': inertia
            })

    def newAssignment(self, newClusters, sizes):
        for i in range(self.clusters):
            newClusters[i] = newClusters[i] / sizes[i]
        return np.ndarray.tolist(newClusters)

if __name__ == '__main__':
    sink = Sink()
    sink.start()