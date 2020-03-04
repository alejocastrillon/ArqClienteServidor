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

    def __init__(self, host, ident, next, prev):
        self.host = host
        self.ident = ident
        self.next = next
        self.prev = prev

serverSocket = zmq.Context().socket(zmq.REP)
nextServer = zmq.Context().socket(zmq.REQ)
node = None

#Get ip 
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
    serverSocket.bind("tcp://*:{}".format(port))
    ident = integerHash(hashString(getDistributedString()))
    host = "tcp://{ip}:{port}".format(ip = getIp(), port = port)
    print("Inicializando nodo con id: %s" % ident)
    return Node(host, ident, Node(host, ident, None), Node(host, ident, None))


def receiveRequestConnection(connectingHost, hostId):
    hostId = int(hostId, 10)
    nextHost = None
    nextId = None
    prevHost = None
    prevId = None
    if node.ident < hostId:
        if node.next.ident == node.ident:
            node.next = Node(connectingHost, hostId, None)
            prevHost = node.host.encode('utf-8')
            prevId = str(node.ident).encode('utf-8')
            nextHost = connectingHost.encode('utf-8')
            nextId = str(hostId).encode('utf-8')
        else:
            if node.next.ident > hostId:
                otherNode = node.next
                node.next = Node(connectingHost, hostId, otherNode)
                nextHost = otherNode.host.encode('utf-8')
                nextId = str(otherNode.ident).encode('utf-8')
                prevHost = node.host.encode('utf-8')
                prevId = str(node.ident).encode('utf-8')
                #serverSocket.send_multipart(('next'.encode('utf-8'), otherNode.host, otherNode.ident))
            else:
                nextServer.connect("tcp://{}".format(node.next.host))
                nextServer.send_multipart(('connect'.encode('utf'), connectingHost.encode('utf-8'), hostId.encode('utf-8')))
                response = nextServer.recv_multipart()
                nextHost = response[0]
                nextId = response[1]
                prevHost = response[2]
                prevId = response[3]
    else:
        pass
    serverSocket.send_multipart((nextHost, nextId, prevHost, prevId))

def sendRequestConnection(hostConnect, port):
    serverSocket.bind("tcp://*:{}".format(port))
    socketConnection = zmq.Context().socket(zmq.REQ)
    socketConnection.connect("tcp://{}".format(hostConnect))
    host = "{h}:{p}".format(h = getIp(), p = port)
    ident = integerHash(hashString(getDistributedString()))
    socketConnection.send_multipart(('connect'.encode('utf-8'), host.encode('utf-8'), str(ident).encode('utf-8')))
    message = socketConnection.recv_multipart()
    return Node(host, ident, Node(message[0].decode('utf-8'), message[1].decode('utf-8')))

if not os.path.exists("uploadedFiles"):
    os.mkdir("uploadedFiles")    

if len(sys.argv) == 2:
    node = initializeNode(sys.argv[1])
elif len(sys.argv) == 4:
    if sys.argv[2] == 'connect':
        node = sendRequestConnection(sys.argv[3], sys.argv[1])

print(node)

while True:
    message = serverSocket.recv_multipart()
    print(message)
    action = message[0].decode('utf-8')
    if action == 'connect':
        receiveRequestConnection(message[1].decode('utf-8'), message[2].decode('utf-8'))
    else:
        pass