
import time
import zmq
import os
import hashlib
import sys
import json
import socket

context = zmq.Context()
mySocket = context.socket(zmq.REP)
index = None
port = None


def getIp(): 
    try: 
        hostIp = socket.gethostbyname(socket.getfqdn()) 
        return hostIp
    except: 
        print("Unable to get Hostname and IP") 

def registerServer(port, capacity):
    proxySocket = zmq.Context().socket(zmq.REQ)
    proxySocket.connect("tcp://localhost:8888")
    proxySocket.send_multipart(('registry'.encode('utf-8'), "{host}:{port}".format(host = getIp(), port = port).encode('utf-8'), str(capacity).encode('utf-8')))
    response = proxySocket.recv().decode('utf-8')
    if response == 'ok':
        print('Servidor registrado')
        mySocket.bind("tcp://*:{port}".format(port = port))
    else:
        print('No se pudo registrar el servidor')

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

#Recibe el archivo y lo guarda en el servidor
def receiveFile(title, content, sha256file, iterator):
    if not(str(title) in index):
        index[str(title)] = []
        index[str(title)].append(sha256file)
    else:
        index[str(title)].append(sha256file)

    route = "uploadedFiles/{sha256file}".format(sha256file = sha256file)
    if not(os.path.exists(route)):
        file = open('index.json', 'w')
        json.dump(index, file)
        file.close()
        proxySocket = zmq.Context().socket(zmq.REQ)
        proxySocket.connect("tcp://localhost:8888")
        if content != b'':
            f = open(route, 'wb')
            f.write(content)
            f.close()
            f = open(route, 'rb')
            sha256 = hashlib.sha256(f.read()).hexdigest()
            f.close()
            if sha256file == sha256:
                mySocket.send_string('ok')
            else:
                mySocket.send_string('error_file')
        else:
            print('Finish')
            mySocket.send_string('ok')
    else:
        mySocket.send_string('error_file_created')
    

#Retorna la lista de archivos que existe en el servidor
def listFolder():
    items = 'Archivos en el servidor:'
    for x in index.keys():
        print(x)
        items = items + '\n' + x
    mySocket.send_string(items)

#Envia archivo desde el servidor al cliente
def sendFile(sha256):
    route = "uploadedFiles/%s" % str(sha256)
    if os.path.exists(route):
        f = open(route, 'rb')
        print('Existe')
        dataFile = f.read()
        sha256 = hashlib.sha256(dataFile).hexdigest()
        mySocket.send_multipart((dataFile, sha256.encode('utf-8')))
    else:
        print('No existe %s' % str(sha256))
        mySocket.send_multipart((''.encode('utf-8'), ''.encode('utf-8')))

if len(sys.argv) != 3:
    sys.stderr.write("Se debe usar: python server.py [port] [capacity]")
    raise SystemExit(1)

hostname = socket.gethostname()    
IPAddr = socket.gethostbyname(hostname)    
print("Your Computer Name is:" + hostname)    
print("Your Computer IP Address is:" + IPAddr)
port = sys.argv[1]
registerServer(sys.argv[1], sys.argv[2])

if not os.path.exists("uploadedFiles"):
    os.mkdir("uploadedFiles")
while True:
    message = mySocket.recv_multipart()
    accion = message[0].decode('utf-8')
    if accion == 'upload':
        receiveFile(message[1].decode('utf-8'), message[2], message[3].decode('utf-8'), message[4].decode('utf-8'))
    elif accion == 'list':
        listFolder()
    elif accion == 'download':
        sendFile(message[1].decode('utf-8'))
    print("Peticion recibida: %s" % accion)
    time.sleep(1)
