
import time
import zmq
import os
import hashlib
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
index = None

def loadIndex():
    myIndex = {}
    if not os.path.exists('index.json'):
        file = open('index.json', 'w')
        data  = {}
        json.dump(data, file)
    else:
        file = open('index.json')
        myIndex = json.load(file)
        print('Content %s' % index)
        file.close()
    return myIndex

index = loadIndex()

#Recibe el archivo y lo guarda en el servidor
def receiveFile(title, content, sha256file, iterator):
    print(index)
    if not(str(title) in index):
        index[str(title)] = []
        index[str(title)].append(sha256file)
    else:
        index[str(title)].append(sha256file)

    file = open('index.json', 'w')
    json.dump(index, file)
    file.close()
    if content != b'':
        route = "uploadedFiles/{sha256file}".format(sha256file = sha256file)
        f = open(route, 'wb')
        f.write(content)
        f.close()
        f = open(route, 'rb')
        sha256 = hashlib.sha256(f.read()).hexdigest()
        f.close()
        if sha256file == sha256:
            socket.send_string('ok')
        else:
            socket.send_string('error')
    else:
        print('Finish')
        socket.send_string('ok')
    

#Retorna la lista de archivos que existe en el servidor
def listFolder():
    items = 'Archivos en el servidor:'
    for x in index.keys():
        print(x)
        items = items + '\n' + x
    socket.send_string(items)

#Envia archivo desde el servidor al cliente
def sendFile(fileName):
    route = "uploadedFiles/%s" % str(fileName)
    if os.path.exists(route):
        f = open(route, 'rb')
        print('Existe')
        dataFile = f.read()
        sha256 = hashlib.sha256(dataFile).hexdigest()
        socket.send_multipart((fileName.encode('utf-8'), dataFile, sha256.encode('utf-8')))
    else:
        socket.send_multipart((''.encode('utf-8'), ''.encode('utf-8')))

if not os.path.exists("uploadedFiles"):
    os.mkdir("uploadedFiles")
print(index)
while True:
    message = socket.recv_multipart()
    accion = message[0]
    if accion == b'upload':
        receiveFile(message[1].decode('utf-8'), message[2], message[3].decode('utf-8'), message[4].decode('utf-8'))
    elif accion == b'list':
        listFolder()
    elif accion == b'download':
        sendFile(message[1].decode('utf-8'))
    print("Peticion recibida: %s" % message)
    time.sleep(1)
