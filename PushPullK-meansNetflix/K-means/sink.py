import sys
import time
import zmq


class Sink:
    def __init__(self):
        self.context = zmq.Context()
        self.send = self.context.socket(zmq.PUSH)
        self.send.connect('tcp://localhost:7557')
        self.recv = self.context.socket(zmq.PULL)
        self.recv.bind('tcp://*:7556')

    def start(self):
        while True:
            message = self.recv.recv_json()
            if 'finished' in message:
                return
            if 'totalTasks' in message:
                self.clusters = message['clusters']
                assign = [{'dataset': [], 'inertia': 0} for i in range(self.cluster)]
            for task in range(message['totalTasks']):
                response = self.recv.recv_json()
                messageClus = response['assign']
                part = response['part']
                for c in range(len(messageClus)):
                    for p in messageClus[c].pop('dataset'):
                        assign[c]['dataset'].append(p+(part*message['numberTasks']))
                    assign[c]['inertia'] += messageClus[c].pop('inertia')
                    for p in messageClus[c]:
                        a = assign[c].get(p)
                        if a:
                            assign[c][p][0] += messageClus[c][p][0]
                            assign[c][p][1] += messageClus[c][p][1]
                        else:
                            assign[c][p] = [messageClus[c][p][0], messageClus[c][p][1]]

            clusters = self.newAssignment(assign)
            self.sender.send_json({
                'clusters': clusters
            })

    def newAssignment(self, newClusters):
        clus = [{} for i in range(self.clusters)]
        for c in range(len(newClusters)):
            clus[c]['dataset'] = newClusters[c].pop("dataset")
            clus[c]['inertia'] = newClusters[c].pop('inertia')
            for p in newClusters[c]:
                clus[c][p] = newClusters[c][p][0]/newClusters[c][p][1]
        return clus

if __name__ == '__main__':
    sink = Sink()
    sink.start()