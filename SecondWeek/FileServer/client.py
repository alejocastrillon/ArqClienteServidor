
import zmq
import sys
import os.path
import hashlib

#head -c 1G <dev/urandom >myfile
context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
PS = 1024*1024*2

#Subida de archivo al servidor
def uploadFile(fileName):
    if os.path.exists(fileName):
        generalHash = hashlib.sha256()
        file = open(fileName, 'rb')
        iterator = 0
        while True:
            file.seek(iterator * PS)
            dataFile = file.read(PS)
            if not dataFile:
                socket.send_multipart(('upload'.encode("utf-8"), fileName.encode("utf-8"), b'', generalHash.hexdigest().encode('utf-8'), str(iterator).encode('utf-8')))
                message = socket.recv()
                if message.decode('utf-8') == 'ok':
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
                    print('Subida del archivo {fileName} parte {iterator} exitosa'.format(fileName = fileName, iterator = iterator))
                    iterator += 1
                else:
                    print("No se pudo subir el archivo %s" % fileName)
                    break
    else:
        sys.stderr.write("El archivo %s no existe \n" % fileName)
        raise SystemExit(1)

#Peticion de listar archivos del servidor
def listFolder():
    socket.send_multipart(('list'.encode("utf-8"), b''))
    message = socket.recv()
    print(message.decode('utf-8'))

#Descarga de archivo del servidor al cliente
def downloadFile(fileName):
    socket.send_multipart(('download'.encode('utf-8'), fileName.encode('utf-8')))
    response = socket.recv_multipart()
    title = response[0].decode('utf-8')
    content = response[1]
    if title != '' and content != b'':
        f = open(title, 'wb')
        f.write(content)
        f.close()
        f = open(title, 'rb')
        sha256 = hashlib.sha256(f.read()).hexdigest()
        if sha256 == response[2].decode('utf-8'):
            print("Descarga del archivo %s exitosa" % title)
        else:
            print("El archivo %s no existe en el servidor" % fileName)
    else:
        print("El archivo %s no existe en el servidor" % fileName)

if len(sys.argv) < 2:
    sys.stderr.write("Se debe usar: python client.py [accion] [nombre_archivo]")
    raise SystemExit(1)

accion = sys.argv[1]
fileName = None

if len(sys.argv) == 3:
    fileName = sys.argv[2]
if accion == 'upload':
    uploadFile(fileName)
elif accion == 'list':
    listFolder()
elif accion == 'download':
    downloadFile(fileName)