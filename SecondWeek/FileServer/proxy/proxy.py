import zmq
import os
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:8888")

indexServers = None
index = None

def loadIndexServers():
    index = []
    if not os.path.exists('indexservers.json'):
        file = open('indexservers.json', 'w')
        json.dump(index, file)
        file.close()
    else:
        file = open('indexservers.json')
        index = json.load(file)
        file.close
    return index

def loadIndex():
    myIndex = {}
    if not os.path.exists('index.json'):
        file = open('index.json', 'w')
        data  = {}
        json.dump(data, file)
        file.close()
    else:
        file = open('index.json')
        myIndex = json.load(file)
        file.close()
    return myIndex

index = loadIndex()
indexServers = loadIndexServers()

def addFile(title, sha256file, host):
    index = loadIndex()
    obj = {}
    if not(str(title) in index):
        index[str(title)] = []
        obj['host'] = host
        obj['sha256file'] = sha256file
        index[str(title)].append(obj)
    else:
        obj['host'] = host
        obj['sha256file'] = sha256file
        index[str(title)].append(obj)
    file = open('index.json', 'w')
    json.dump(index, file)
    file.close()
    socket.send_string('ok')
    index = loadIndex()

def downloadFile(fileName):
    index = loadIndex()
    if fileName in index:
        listObjects = index[fileName]
        socket.send_json(json.dumps(listObjects))
    else:
        socket.send_string('0')

def registryServer(host, capacity):
    if host != None and capacity != None:
        if not(existsServer(host)):
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
    socket.send_json(json.dumps(indexServers))

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
    elif accion == 'add_file':
        addFile(message[1].decode('utf-8'), message[2].decode('utf-8'), message[3].decode('utf-8'))
    elif accion == 'download':
        downloadFile(message[1].decode('utf-8'))
    print(message)