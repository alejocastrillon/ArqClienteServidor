import zmq
import os
import hashlib
import sys
import json
import random
import string
import socket
import getmac
import copy

class Node:

    def __init__(self, host, ident, next):
        self.host = host
        self.ident = ident
        self.next = next

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

def initializeNode(port, serverSocket, rango):
    serverSocket.bind("tcp://*:{}".format(port))
    ident = integerHash(hashString(getDistributedString()))
    rango = [0, ident, ident, pow(2, 256)]
    print(rango)
    host = "tcp://{ip}:{port}".format(ip = getIp(), port = port)
    print("Inicializando nodo con id: %s" % ident)
    return Node(host, ident, Node(host, ident, None))


def receiveRequestConnection(connectingHost, idHost, serverSocket, node, rango):
    idHost = int(idHost, 10)
    if idHost > node.ident:
        if node.next.ident <= node.ident:
            nextNode = copy.deepcopy(node.next)
            node.next.ident = idHost
            node.next.host = connectingHost
            print(len(rango))
            rango[len(rango) - 2] = idHost
            print(rango)
            serverSocket.send_multipart(('next'.encode('utf-8'), nextNode.host.encode('utf-8'), str(nextNode.ident).encode('utf-8')))
        else:
            serverSocket.send_multipart(('question'.encode('utf-8'), node.next.host.encode('utf-8')))
    else:
        nextNode = copy.deepcopy(node.next)
        node.next.ident = idHost
        node.next.host = connectingHost
        serverSocket.send_multipart(('next'.encode('utf-8'), nextNode.host.encode('utf-8'), str(nextNode.ident).encode('utf-8')))
    print(node.next.ident)

def receiveRequestDisconnect(idHost, nextId, nextHost, serverSocket, node):
    idHost = int(idHost, 10)
    nextId = int(nextId, 10)
    if node.next.ident == idHost:
        node.next.ident = nextId
        node.next.host = nextHost
        print(node.next.ident)
        serverSocket.send_multipart(('ok'.encode('utf-8'), ''.encode('utf-8')))
    else:
        print('disconnect %s' % node.next.host)
        serverSocket.send_multipart(('question'.encode('utf-8'), node.next.host.encode('utf-8')))

def disconnectNode(socketConnection, node):
    print(node.next.host)
    if node.ident != node.next.ident:
        socketConnection.connect("tcp://{}".format(node.next.host))
        socketConnection.send_multipart(('disconnect'.encode('utf-8'), str(node.ident).encode('utf-8'), str(node.next.ident).encode('utf-8'), node.next.host.encode('utf-8')))
        message = socketConnection.recv_multipart()
        while message[0].decode('utf-8') == 'question':
            socketConnection.connect("tcp://{}".format(message[1].decode('utf-8')))
            socketConnection.send_multipart(('disconnect'.encode('utf-8'), str(node.ident).encode('utf-8'), str(node.next.ident).encode('utf-8'), node.next.host.encode('utf-8')))
            message = socketConnection.recv_multipart()

def sendRequestConnection(hostConnect, port, serverSocket, socketConnection):
    serverSocket.bind("tcp://*:{}".format(port))
    socketConnection.connect("tcp://{}".format(hostConnect))
    host = "{h}:{p}".format(h = getIp(), p = port)
    ident = integerHash(hashString(getDistributedString()))
    print(ident)
    socketConnection.send_multipart(('connect'.encode('utf-8'), host.encode('utf-8'), str(ident).encode('utf-8')))
    message = socketConnection.recv_multipart()
    while(message[0].decode('utf-8') == 'question'):
        socketConnection.connect("tcp://{}".format(message[1].decode('utf-8')))
        host = "{h}:{p}".format(h = getIp(), p = port)
        socketConnection.send_multipart(('connect'.encode('utf-8'), host.encode('utf-8'), str(ident).encode('utf-8')))
        message = socketConnection.recv_multipart()
    print(message[2].decode('utf-8'))
    return Node(host, ident, Node(message[1].decode('utf-8'), int(message[2].decode('utf-8'), 10), None))

def main():
    serverSocket = zmq.Context().socket(zmq.REP)
    socketConnection = zmq.Context().socket(zmq.REQ)
    node = None
    rango = []
    if not os.path.exists("uploadedFiles"):
        os.mkdir("uploadedFiles")    
    if len(sys.argv) == 2:
        node = initializeNode(sys.argv[1], serverSocket, rango)
    elif len(sys.argv) == 4:
        if sys.argv[2] == 'connect':
            node = sendRequestConnection(sys.argv[3], sys.argv[1], serverSocket, socketConnection)
    print(node)
    while True:
        try:
            message = serverSocket.recv_multipart()
            print(message)
            action = message[0].decode('utf-8')
            if action == 'connect':
                receiveRequestConnection(message[1].decode('utf-8'), message[2].decode('utf-8'), serverSocket, node, rango)
            elif action == 'disconnect':
                receiveRequestDisconnect(message[1].decode('utf-8'), message[2].decode('utf-8'), message[3].decode('utf-8'), serverSocket, node)
            elif action == 'ok':
                serverSocket.send_multipart(('ok'.encode('utf-8'), ''.encode('utf-8')))
        except KeyboardInterrupt:
            disconnectNode(socketConnection, node)
            sys.exit()

if __name__ == "__main__":
    main()