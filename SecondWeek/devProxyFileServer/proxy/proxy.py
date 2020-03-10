import zmq
import os
import json

#Carga el archivo de indice de los servidores registrados
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

#Carga el archivo de indice de los archivos subidos
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


#Retorna la lista de archivos que existe en el servidor
def listFolder(index, socket):
    items = 'Archivos en el servidor:'
    for x in index.keys():
        items = items + '\n' + x
    socket.send_string(items)

#Agrega al indice de archivos un archivo subido con su sha
def addFile(title, listObject, socket):
    index = loadIndex()
    index[str(title)] = json.loads(listObject)
    file = open('index.json', 'w')
    json.dump(index, file)
    file.close()
    socket.send_string('ok')
    index = loadIndex()

#Envia las rutas donde están las partes del archivo
def downloadFile(fileName, socket):
    index = loadIndex()
    if fileName in index:
        listObjects = index[fileName]
        socket.send_json(json.dumps(listObjects))
    else:
        socket.send_string('0')

#Registra el servidor como un nodo
def registryServer(host, indexServers, socket):
    if host != None:
        if not(existsServer(host, indexServers)):
            obj = {}
            obj["host"] = host
            indexServers.append(obj)
            file = open('indexservers.json', 'w')
            json.dump(indexServers, file)
        socket.send_string('ok')
    else:
        socket.send_string('error')

#Retorna el indice de servidores
def returnServerEnableList(indexServers, socket):
    socket.send_json(json.dumps(indexServers))

#Determina si un servidor está registrado
def existsServer(host, indexServers):
    for detail in indexServers:
        if detail['host'] == host:
            return True
    return False

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:8888")
    index = loadIndex()
    indexServers = loadIndexServers()
    while True:
        message = socket.recv_multipart()
        accion = message[0].decode('utf-8')
        if accion == 'registry':
            registryServer(message[1].decode('utf-8'), indexServers, socket)
        elif accion == 'index':
            returnServerEnableList(indexServers, socket)
        elif accion == 'add_file':
            addFile(message[1].decode('utf-8'), message[2].decode('utf-8'), socket)
        elif accion == 'download':
            downloadFile(message[1].decode('utf-8'), socket)
        elif accion == 'list':
            listFolder(index, socket)

if __name__ == "__main__":
    main()