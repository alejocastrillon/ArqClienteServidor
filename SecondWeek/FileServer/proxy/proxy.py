import zmq
import os
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:8888")

indexServers = None

def loadIndexServers():
    index = []
    if not os.path.exists('indexservers.json'):
        file = open('index.json', 'w')
        json.dump(index, file)
        file.close()
    else:
        file = open('indexservers.json')
        index = json.load(file)
        file.close
    return index

indexServers = loadIndexServers()

def registryServer(host, capacity):
    if host != None and capacity != None and not(existsServer(host)):
        obj = {}
        obj["host"] = host
        obj["capacity"] = capacity
        indexServers.append(obj)
        file = open('indexservers.json', 'w')
        json.dump(indexServers, file)
        socket.send_string('ok')
    else:
        socket.send_string('error')

def returnServerEnableList():
    socket.send_string(str(indexServers).encode('utf-8'))

def existsServer(host):
    for detail in indexServers:
        if detail['host'] == host:
            return True
    return False

while True:
    message = socket.recv_multipart()
    accion = message[0].decode('utf-8')
    if accion == 'registry':
        registryServer(message[1].decode('utf-8'), int(message[2].decode('utf-8')))
    elif accion == 'index':
        returnServerEnableList()