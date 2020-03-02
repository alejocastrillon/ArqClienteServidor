import zmq
import os
import hashlib
import sys
import json
import random
import string
import socket

serverSocket = zmq.Context().socket(zmq.REP)
port = None
hostConnection = None
ringServers = None

def getIp(): 
    try: 
        hostIp = socket.gethostbyname(socket.getfqdn()) 
        return hostIp
    except: 
        print("Unable to get Hostname and IP") 

def getDistributedString():
    chars = []
    chars.extend(string.ascii_lowercase)
    chars.extend(string.ascii_uppercase)
    chars.extend(string.digits)
    return ''.join(random.choice(chars) for x in range(25))

def hashString(string):
    return hashlib.sha256(string.encode()).hexdigest()[:8]

def loadRing():
    index = []
    if not os.path.exists('ringservers.json'):
        file = open('ringservers.json', 'w')
        json.dump(index, file)
        file.close()
    else:
        file = open('ringservers.json')
        index = json.load(file)
        print(index.sort())
        file.close()
    return index

ringServers = loadRing()

def integerHash(hash):
    return int(hash, 16)

def receiveRequestConnection(connectingHost):
    print('llego')
    ringServers = loadRing()
    iden = integerHash(hashString(getDistributedString()))
    ringServers[str(iden)] = {
        "host": "{}".format(connectingHost)
    }
    file = open('ringservers.json', 'w')
    json.dump(ringServers, file)
    file.close()
    ringServers = loadRing()
    serverSocket.send_string(str(iden))

def sendRequestConnection(hostConnect):
    print('entro')
    socketConnection = zmq.Context().socket(zmq.REQ)
    socketConnection.connect("tcp://{}".format(hostConnect))
    host = "{h}:{p}".format(h = getIp(), p = port)
    socketConnection.send_multipart(('connect'.encode('utf-8'), host.encode('utf-8')))
    iden = socketConnection.recv_string()

if not os.path.exists("uploadedFiles"):
    os.mkdir("uploadedFiles")    

if len(sys.argv) <= 2:
    sys.stderr.write("Se debe especificar una acción\n")
    raise SystemExit(1)
else:
    accion = sys.argv[1]
    if accion == "principal":
        if len(sys.argv) == 3:
            port = sys.argv[2]
            serverSocket.bind("tcp://*:{}".format(port))
            ringServers = loadRing()
            ringServers[str(integerHash(hashString(getDistributedString())))] = {
                "host": "{h}:{p}".format(h = getIp(), p = port)
            }
            file = open('ringservers.json', 'w')
            json.dump(ringServers, file)
            file.close()
            ringServers = loadRing()
            print(integerHash(hashString(getDistributedString())))
        else:
            sys.stderr.write("Se debe especificar el host")
            raise SystemError(1)
    elif accion == "connect":
        if len(sys.argv) != 4:
            sys.stderr.write("Se debe usar: python node.py connect [port] [host]")
            raise SystemExit(1)
        else:
            port = sys.argv[2]
            sendRequestConnection(sys.argv[3])

while True:
    message = serverSocket.recv_multipart()
    action = message[0].decode('utf-8')
    if action == 'connect':
        receiveRequestConnection(message[1].decode('utf-8'))
    else:
        pass