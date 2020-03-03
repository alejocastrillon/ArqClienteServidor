import zmq
import os
import hashlib
import sys
import json
import random
import string
import socket
import getmac

class Node:

    def __init__(self, host, ident, next):
        self.host = host
        self.ident = ident
        self.next = next

serverSocket = zmq.Context().socket(zmq.REP)
nextServer = zmq.Context().socket(zmq.REQ)
node = None

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
    return getmac.get_mac_address() + ''.join(random.choice(chars) for x in range(25))

def hashString(string):
    return hashlib.sha256(string.encode()).hexdigest()[:8]

def integerHash(hash):
    return int(hash, 16)

def initializeNode(port):
    print(port)
    ident = integerHash(hashString(getDistributedString()))
    host = "tcp://{ip}:{port}".format(ip = getIp(), port = port)
    node = Node(host, ident, None)
    print("Inicializado nodo con id: %s" % node.ident)
    serverSocket.bind("tcp://*:{}".format(port))

def receiveRequestConnection(connectingHost, hostId):
    print(connectingHost)
    hostId = int(hostId, 10)
    print(hostId)

def sendRequestConnection(hostConnect, port):
    print(hostConnect)
    socketConnection = zmq.Context().socket(zmq.REQ)
    socketConnection.connect("tcp://{}".format(hostConnect))
    host = "{h}:{p}".format(h = getIp(), p = port)
    socketConnection.send_multipart(('connect'.encode('utf-8'), host.encode('utf-8'), str(integerHash(hashString(getDistributedString()))).encode('utf-8')))
    iden = socketConnection.recv_string()

if not os.path.exists("uploadedFiles"):
    os.mkdir("uploadedFiles")    

if len(sys.argv) == 2:
    initializeNode(sys.argv[1])
elif len(sys.argv) == 4:
    if sys.argv[2] == 'connect':
        sendRequestConnection(sys.argv[3], sys.argv[1])

while True:
    message = serverSocket.recv_multipart()
    print(message)
    action = message[0].decode('utf-8')
    if action == 'connect':
        receiveRequestConnection(message[1].decode('utf-8'), message[2].decode('utf-8'))
    else:
        pass