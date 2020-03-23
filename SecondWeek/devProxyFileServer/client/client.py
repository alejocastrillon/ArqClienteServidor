
import zmq
import sys
import os.path
import hashlib
import random
import json

#head -c 1G </dev/urandom >myfile
PS = 1024*1024*2


def clear(): 
    if os.name == 'nt': 
        _ = os.system('cls') 
    else: 
        _ = os.system('clear') 

#Subida de archivo al servidor
def uploadFile(fileName, proxySocket, socket):
    if os.path.exists(fileName):
        generalHash = hashlib.sha256()
        dataIndex = []
        proxySocket.send_multipart(('index'.encode('utf-8'), ''.encode('utf-8')))
        servers = json.loads(proxySocket.recv_json())
        file = open(fileName, 'rb')
        iterator = 0
        iteratorServer = 0
        while True:
            if iteratorServer == len(servers):
                iteratorServer = 0
            obj = {}
            socket.connect("tcp://{host}".format(host = servers[iteratorServer]['host']))
            file.seek(iterator * PS)
            dataFile = file.read(PS)
            if not dataFile:
                socket.send_multipart(('upload'.encode("utf-8"), fileName.encode("utf-8"), b'', generalHash.hexdigest().encode('utf-8'), str(iterator).encode('utf-8')))
                message = socket.recv()
                if message.decode('utf-8') == 'ok':
                    obj['host'] = ''
                    obj['sha256file'] = generalHash.hexdigest()
                    dataIndex.append(obj)
                    proxySocket.send_multipart(('add_file'.encode('utf'), fileName.encode('utf-8'), json.dumps(dataIndex).encode('utf-8')))
                    proxySocket.recv_string()
                    clear()
                    print('Subida del archivo {fileName} exitosa'.format(fileName = fileName))
                else:
                    print("No se pudo subir el archivo %s" % fileName)
                break
            else:
                generalHash.update(dataFile)
                sha256 = hashlib.sha256(dataFile).hexdigest()
                socket.send_multipart(('upload'.encode("utf-8"), fileName.encode("utf-8"), dataFile, sha256.encode('utf-8'), str(iterator).encode('utf-8')))
                message = socket.recv()
                if message.decode('utf-8') == 'ok':
                    obj['host'] = servers[iteratorServer]['host']
                    obj['sha256file'] = sha256
                    dataIndex.append(obj)
                    clear()
                    print('Subida del archivo {fileName} parte {iterator} exitosa'.format(fileName = fileName, iterator = iterator))
                    iterator += 1
                elif message.decode('utf-8') == 'error_file':
                    print("No se pudo subir el archivo %s" % fileName)
                    break
                elif message.decode('utf-8') == 'error_file_created':
                    print('El archivo ya existe')
                    break
            iteratorServer += 1
    else:
        sys.stderr.write("El archivo %s no existe \n" % fileName)
        raise SystemExit(1)

#Peticion de listar archivos del servidor
def listFolder(proxySocket):
    proxySocket.send_multipart(('list'.encode("utf-8"), b''))
    message = proxySocket.recv()
    print(message.decode('utf-8'))

#Descarga de archivo del servidor al cliente
def downloadFile(fileName, proxySocket, socket):
    proxySocket.send_multipart(('download'.encode('utf-8'), fileName.encode('utf-8')))
    files = json.loads(proxySocket.recv_json())
    generalHash = hashlib.sha256()
    if len(files) == 0:
        print('No existe el archivo')
    else:
        for file in files:
            if file['host'] != '':
                socket.connect("tcp://{host}".format(host = file['host']))
                socket.send_multipart(('download'.encode('utf-8'), file['sha256file'].encode('utf-8')))
                response = socket.recv_multipart()
                content = response[0]
                f = open(fileName, 'ab')
                f.write(content)
                f.close()
                sha256 = hashlib.sha256(content).hexdigest()
                generalHash.update(content)
                if sha256 == response[1].decode('utf-8'):
                    clear()
                    print("Descarga del archivo {title} exitosa parte {index}/{length}".format(title = fileName, index = files.index(file) + 1, length = len(files) - 1))
                else:
                    print("El archivo %s no existe en el servidor" % fileName)
            else:
                if generalHash.hexdigest() == file['sha256file']:
                    clear()
                    print("Descarga del archivo exitosa")
                else:
                    print("Archivo corrupto")

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    proxySocket = zmq.Context().socket(zmq.REQ)
    proxySocket.connect("tcp://{}:8888".format(sys.argv[1]))
    if len(sys.argv) < 3:
        sys.stderr.write("Se debe usar: python client.py [hostProxy] [accion] [nombre_archivo]")
        raise SystemExit(1)
    accion = sys.argv[2]
    fileName = None
    if len(sys.argv) == 4:
        fileName = sys.argv[3]
    if accion == 'upload':
        uploadFile(fileName, proxySocket, socket)
    elif accion == 'list':
        listFolder(proxySocket)
    elif accion == 'download':
        downloadFile(fileName, proxySocket, socket)

if __name__ == "__main__":
    main()