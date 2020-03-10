import zmq
import os
import hashlib
import json

def loadIndex():
    myIndex = {}
    if not os.path.exists('index.json'):
        file = open('index.json', 'w')
        data  = {}
        json.dump(data, file)
    else:
        file = open('index.json')
        myIndex = json.load(file)
        file.close()
    return myIndex

#Recibe el archivo y lo guarda en el servidor
def receiveFile(title, content, sha256file, iterator, index, socket):
    if not(str(title) in index):
        index[str(title)] = []
        index[str(title)].append(sha256file)
    else:
        index[str(title)].append(sha256file)
    route = "uploadedFiles/{}".format(sha256file)
    if not(os.path.exists(route)):
        file = open('index.json', 'w')
        json.dump(index, file)
        file.close()
        if content != b'':
            f = open(route, 'wb')
            f.write(content)
            f.close()
            f = open(route, 'rb')
            sha256 = hashlib.sha256(f.read()).hexdigest()
            f.close()
            if sha256file == sha256:
                socket.send_string('ok')
            else:
                socket.send_string('error_file')
        else:
            socket.send_string('ok')
    else:
        socket.send_string('error_file_created')
    

#Retorna la lista de archivos que existe en el servidor
def listFolder(index, socket):
    items = 'Archivos en el servidor:'
    for x in index.keys():
        items = items + '\n' + x
    socket.send_string(items)

#Envia archivo desde el servidor al cliente
def sendFile(fileName, part, index,socket):
    if fileName in index:
        listObjects = index[fileName]
        if part != None:
            if part != len(listObjects) - 1:
                route = "uploadedFiles/%s" % str(listObjects[part])
                if os.path.exists(route):
                    f = open(route, 'rb')
                    dataFile = f.read()
                    sha256 = hashlib.sha256(dataFile).hexdigest()
                    socket.send_multipart((fileName.encode('utf-8'), dataFile, sha256.encode('utf-8')))
                else:
                    socket.send_multipart((''.encode('utf-8'), ''.encode('utf-8')))
            else:
                socket.send_multipart((''.encode('utf-8'), ''.encode('utf-8'), listObjects[part].encode('utf-8')))
        else:
            socket.send_string(str(len(listObjects)))
    else:
        socket.send_string('0')

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    index = loadIndex()
    if not os.path.exists("uploadedFiles"):
        os.mkdir("uploadedFiles")
    while True:
        message = socket.recv_multipart()
        accion = message[0].decode('utf-8')
        if accion == 'upload':
            receiveFile(message[1].decode('utf-8'), message[2], message[3].decode('utf-8'), message[4].decode('utf-8'), index, socket)
        elif accion == 'list':
            listFolder(index, socket)
        elif accion == 'download':
            part = None
            if message[2].decode('utf-8') != '':
                part = int(message[2].decode('utf-8'))
            sendFile(message[1].decode('utf-8'), part, index, socket)

if __name__ == "__main__":
    main()