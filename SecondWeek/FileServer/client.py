#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq
import sys
import os.path
accion = None
fileName = None

context = zmq.Context()

#  Socket to talk to server
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

def uploadFile(fileName):
    if os.path.exists(fileName):
        print('ok')
        file = open(fileName, 'rb')
        dataFile = file.read()
        dataFile = dataFile
        socket.send_multipart(('upload'.encode("utf-8"), fileName.encode("utf-8"), dataFile))
        message = socket.recv()
        print("Received reply %s" % (message))
    else:
        sys.stderr.write("El archivo %s no existe \n" % fileName)
        raise SystemExit(1)

def listFolder():
    socket.send_multipart(('list'.encode("utf-8"), b''))
    message = socket.recv()
    print(message)

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