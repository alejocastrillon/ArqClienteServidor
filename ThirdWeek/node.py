import zmq
import sys
import random
import string
import uuid
import hashlib
import os
import json

def getMac(): 
    try: 
        mac = uuid.getnode()
        return mac
    except: 
        print("Unable to get MAC") 

def getDistributedString():
    chars = []
    chars.extend(string.ascii_lowercase)
    chars.extend(string.ascii_uppercase)
    chars.extend(string.digits)
    return str(getMac()) + ''.join(random.choice(chars) for x in range(25))

def hashString(string):
    return hashlib.sha256(string.encode()).hexdigest()[:8]

def integerHash(hash):
    return int(hash, 16)

class Node:

    def __init__(self, ip, port):
        self.IDENT = integerHash(hashString(getDistributedString()))
        self.ip = ip
        self.port = port
        self.socket = zmq.Context().socket(zmq.REP)
        self.next = None
        self.previous = None
        self.range = [None, None]
        self.host = "{ip}:{port}".format(ip=self.ip, port=self.port)

    def download(self, fileName):
        try:
            nameId = int(fileName[:8], 16)
        except ValueError:
            self.socket.send_multipart(('Nombre incorrecto'.encode('utf-8')))
        if self.range[0] >= self.range[1]:
            if self.range[0] < nameId or nameId <= self.range[1]:
                if os.path.isfile("uploadedFiles/%s" % fileName):
                    file = open("uploadedFiles/%s" % fileName, 'rb')
                    data = file.read()
                    self.socket.send_multipart(('found'.encode('utf-8'), data, hashlib.sha256(data).hexdigest().encode('utf-8')))
                else:
                    self.socket.send_multipart(('notfound'.encode('utf-8')))
            else:
                if nameId > self.range[1]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.next.encode('utf-8')))
                elif nameId <= self.range[0]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.previous.encode('utf-8')))
        else:
            if self.range[0] < nameId <= self.range[1]:
                if os.path.exists("uploadedFiles/%s" % fileName):
                    file = open("uploadedFiles/%s" % fileName, 'rb')
                    data = file.read()
                    self.socket.send_multipart(('found'.encode('utf-8'), data, hashlib.sha256(data).hexdigest().encode('utf-8')))
                else:
                    print('No se encontro el archivo %s' % fileName)
                    self.socket.send_multipart(('notfound'.encode('utf-8'), ''.encode('utf-8')))
            else:
                if nameId > self.range[1]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.next.encode('utf-8')))
                elif nameId <= self.range[0]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.previous.encode('utf-8')))
    
    def downloadIndex(self, fileName):
        try:
            nameId = int(fileName[:8], 16)
        except ValueError:
            self.socket.send_multipart(('Nombre incorrecto'.encode('utf-8')))
        if self.range[0] >= self.range[1]:
            if self.range[0] < nameId or nameId <= self.range[1]:
                if os.path.isfile("uploadedFiles/%s.json" % fileName):
                    file = open("uploadedFiles/%s.json" % fileName, 'r')
                    data = file.read()
                    self.socket.send_multipart(('found'.encode('utf-8'), data.encode('utf-8')))
                else:
                    self.socket.send_multipart(('notfound'.encode('utf-8'), ''.encode('utf-8')))
            else:
                if nameId > self.range[1]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.next.encode('utf-8')))
                elif nameId <= self.range[0]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.previous.encode('utf-8')))
        else:
            if self.range[0] < nameId <= self.range[1]:
                if os.path.exists("uploadedFiles/%s.json" % fileName):
                    file = open("uploadedFiles/%s.json" % fileName, 'r')
                    data = file.read()
                    self.socket.send_multipart(('found'.encode('utf-8'), data.encode('utf-8')))
                else:
                    self.socket.send_multipart(('notfound'.encode('utf-8'), ''.encode('utf-8')))
            else:
                if nameId > self.range[1]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.next.encode('utf-8')))
                elif nameId <= self.range[0]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.previous.encode('utf-8')))

    def transferFiles(self, name):
        if os.path.isfile("uploadedFiles/%s" % name):
            data = open("uploadedFiles/%s" % name, "rb").read()
            sha = hashlib.sha256(data).hexdigest()
            self.socket.send_multipart(('ok'.encode('utf-8'), sha.encode('utf-8'), data))
        else:
            self.socket.send_multipart(('notfound'.encode('utf-8'), 'No existe el archivo'.encode('utf-8')))

    def uploadFile(self, fileName):
        try:
            nameId = int(fileName[:8], 16)
        except ValueError:
            self.socket.send_multipart(('Nombre incorrecto'.encode('utf-8')))
        print(nameId)
        if self.range[0] >= self.range[1]:
            if self.range[0] < nameId or nameId <= self.range[1]:
                self.socket.send_multipart(('ok'.encode('utf-8'), self.host.encode('utf-8')))
                message = self.socket.recv_multipart()
                if hashlib.sha256(message[0]).hexdigest() == message[1].decode('utf-8'):
                    file = open("uploadedFiles/%s" % message[1].decode('utf-8'), 'wb')
                    file.write(message[0])
                    file.close()
                    self.socket.send_string('ok')
                else:
                    self.socket.send_string('badfile')
            else:
                if nameId > self.range[1]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.next.encode('utf-8')))
                elif nameId <= self.range[0]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.previous.encode('utf-8')))
        else:
            if self.range[0] < nameId <= self.range[1]:
                self.socket.send_multipart(('ok'.encode('utf-8'), self.host.encode('utf-8')))
                message = self.socket.recv_multipart()
                if hashlib.sha256(message[0]).hexdigest() == message[1].decode('utf-8'):
                    file = open("uploadedFiles/%s" % message[1].decode('utf-8'), 'wb')
                    file.write(message[0])
                    file.close()
                    self.socket.send_string('ok')
                else:
                    self.socket.send_string('badfile')
            else:
                if nameId > self.range[1]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.next.encode('utf-8')))
                elif nameId <= self.range[0]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.previous.encode('utf-8')))


    def uploadIndex(self, fileName):
        print('Entro index')
        try:
            nameId = int(fileName[:8], 16)
        except ValueError:
            self.socket.send_multipart(('Nombre incorrecto'.encode('utf-8')))
        if self.range[0] >= self.range[1]:
            if self.range[0] < nameId or nameId <= self.range[1]:
                self.socket.send_multipart(('ok'.encode('utf-8'), self.host.encode('utf-8')))
                message = self.socket.recv_json()
                file = open("uploadedFiles/%s.json" % fileName, 'w')
                file.write(message)
                file.close()
                self.socket.send_string('ok')
            else:
                if nameId > self.range[1]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.next.encode('utf-8')))
                elif nameId <= self.range[0]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.previous.encode('utf-8')))
        else:
            if self.range[0] < nameId <= self.range[1]:
                self.socket.send_multipart(('ok'.encode('utf-8'), self.host.encode('utf-8')))
                message = self.socket.recv_json()
                file = open("uploadedFiles/%s.json" % fileName, 'w')
                file.write(message)
                file.close()
                self.socket.send_string('ok')
            else:
                if nameId > self.range[1]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.next.encode('utf-8')))
                elif nameId <= self.range[0]:
                    self.socket.send_multipart(('question'.encode('utf-8'), self.previous.encode('utf-8')))
        
    def connectingServer(self, address, nodeAddress):
        d = {
            "action": "connect",
            "address": address,
            "id": self.IDENT
        }
        r = {
            "action": "next",
            "next": nodeAddress
        }
        while True:
            server = zmq.Context().socket(zmq.REQ)
            server.connect(r["next"])
            server.send_json(d)
            r = server.recv_json()
            if r["state"] == "ok":
                self.previous = r["previous"]
                self.next = r["next"]
                self.range[0] = r["lowestHash"]
                self.range[1] = self.IDENT
                server.close()
                break;
            else:
                server.close()
        transactionSocket = zmq.Context().socket(zmq.REQ)
        transactionSocket.connect(self.next)
        for file in r["files"]:
            d = {
                "action": "transferServer",
                "name": file
            }
            print(file)
            transactionSocket.send_json(d)
            message = transactionSocket.recv_multipart()
            if message[0].decode('utf-8') == "ok":
                if message[1].decode('utf-8') == file:
                    fwrite = open("uploadedFiles/%s" % file, "wb")
                    fwrite.write(message[2])
                    fwrite.close()
                    print("Transfering file %s" % file)
                else:
                    print("Corrupted file")
            else:
                print("Connection error")
        transactionSocket.disconnect(self.next)

    def addServer(self, nodeAddress, nodeId):
        d = {"files":[]}
        if self.range[0] >= self.range[1]:
            if self.range[0] < nodeId or nodeId <= self.range[1]:
                for file in os.listdir("uploadedFiles"):
                    idFile = int(file[:8], 16)
                    if idFile > self.range[0] and idFile <= nodeId and nodeId > self.range[0]:
                        d["files"].append(file)
                    elif (idFile <= self.range[1] or idFile > self.range[0]) and (nodeId < self.range[1]):
                        d["files"].append(file)
                d["state"] = "ok"
                d["lowestHash"] = self.range[0]
                self.range[0] = nodeId
                if self.next != None and self.previous != None:
                    d["next"] = "tcp://%s" % self.host
                    d["previous"] = self.previous
                    sc = zmq.Context().socket(zmq.REQ)
                    sc.connect(self.previous)
                    data = {
                        "action": "next",
                        "address": nodeAddress
                    }
                    sc.send_json(data)
                    message = sc.recv()
                    if message.decode('utf-8') == "ok":
                        print("Next server updating {ident} con ip {address}".format(ident= nodeId, address= nodeAddress))
                    sc.close()
                    self.previous = nodeAddress
                else:
                    d["next"] = "tcp://%s" % self.host
                    d["previous"] = "tcp://%s" % self.host
                    self.next = nodeAddress
                    self.previous = nodeAddress
            else:
                d["state"] = "next"
                if nodeId > self.range[1]:
                    d["next"] = self.next
                elif nodeId <= self.range[0]:
                    d["next"] = self.previous
        else:
            if self.range[0] < nodeId <= self.range[1]:
                for file in os.listdir("uploadedFiles"):
                    idFile = int(file[:8], 16)
                    if idFile <= nodeId:
                        d["files"].append(file)
                d["state"] = "ok"
                d["lowestHash"] = self.range[0]
                self.range[0] = nodeId
                d["next"] = "tcp://%s" % self.host
                d["previous"] = self.previous
                sc = zmq.Context().socket(zmq.REQ)
                sc.connect(self.previous)
                data = {
                    "action": "next",
                    "address": nodeAddress
                }
                sc.send_json(data)
                message = sc.recv()
                if message.decode('utf-8') == "ok":
                    print("Nodo {ident} conectado con ip {ip}".format(ident= nodeId, ip=nodeAddress))
                sc.close()
                self.previous = nodeAddress
            else:
                d["state"] = "next"
                if nodeId > self.range[1]:
                    d["next"] = self.next
                elif nodeId <= self.range[0]:
                    d["next"] = self.previous
        self.socket.send_json(d)

def main():
    ip = sys.argv[1]
    port = sys.argv[2]
    node = Node(ip, port)
    if not os.path.exists("uploadedFiles"):
        os.mkdir("uploadedFiles")
    if len(sys.argv) == 3:
        node.range[0] = node.IDENT
        node.range[1] = node.IDENT
    elif len(sys.argv) == 4:
        node.connectingServer("tcp://{ip}:{port}".format(ip=ip, port=port), "tcp://{}".format(sys.argv[3]))
    else:
        sys.stderr.write("Para inicializar el nodo principal: python node.py [ip] [port]\nPara agregar nodo: python node.py [ip] [port] [ip_connect:port_connect]")
        raise SystemExit(1)
    node.socket.bind("tcp://*:%s" % port)
    print(node.IDENT)
    while True:
        print(node.next)
        message = node.socket.recv_json()
        if message["action"] == "connect":
            node.addServer(message["address"], message["id"])
        elif message["action"] == "previous":
            node.previous = message["address"]
            node.socket.send("ok".encode("utf-8"))
            print(node.previous)
        elif message["action"] == "next":
            node.next = message["address"]
            node.socket.send("ok".encode("utf-8"))
            print(node.next)
        elif message["action"] == "upload":
            node.uploadFile(message["name"])
        elif message["action"] == "download":
            node.download(message["name"])
        elif message["action"] == "transferServer":
            node.transferFiles(message["name"])
        elif message["action"] == "uploadIndex":
            node.uploadIndex(message["name"])
        elif message["action"] == "downloadIndex":
            node.downloadIndex(message["name"])
main()