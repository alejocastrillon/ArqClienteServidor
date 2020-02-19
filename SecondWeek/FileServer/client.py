
import zmq
import sys
import os.path
import hashlib

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#Subida de archivo al servidor
def uploadFile(fileName):
    if os.path.exists(fileName):
        print('ok')
        file = open(fileName, 'rb')
        dataFile = file.read()
        sha256 = hashlib.sha256(dataFile).hexdigest()
        print(sha256)
        socket.send_multipart(('upload'.encode("utf-8"), fileName.encode("utf-8"), dataFile, sha256.encode('utf-8')))
        message = socket.recv()
        if message.decode('utf-8') == 'ok':
            print('Subida del archivo %s exitosa' % fileName)
        else:
            print("No se pudo subir el archivo %s" % fileName)
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
    print(content)
    if title != b'' and content != b'':
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