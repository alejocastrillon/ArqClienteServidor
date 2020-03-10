import zmq
import os
import hashlib
import sys
import json
import socket

#Conseguir ip del servidor
""" def getIp(): 
    try: 
        hostIp = socket.gethostbyname(socket.getfqdn()) 
        return hostIp
    except: 
        print("Unable to get Hostname and IP")  """

#Registro del servidor
def registerServer(host, proxyHost):
    proxySocket = zmq.Context().socket(zmq.REQ)
    proxySocket.connect("tcp://{}".format(proxyHost))
    proxySocket.send_multipart(('registry'.encode('utf-8'), "{}".format(host).encode('utf-8')))
    response = proxySocket.recv().decode('utf-8')
    if response == 'ok':
        print('Servidor registrado')
        return True
    else:
        print('No se pudo registrar el servidor')
        return False

#Recibe el archivo y lo guarda en el servidor
def receiveFile(title, content, sha256file, iterator, mySocket):
    route = "uploadedFiles/{sha256file}".format(sha256file = sha256file)
    if not(os.path.exists(route)):
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
            mySocket.send_string('ok')
    else:
        mySocket.send_string('error_file_created')

#Envia archivo desde el servidor al cliente
def sendFile(sha256, mySocket):
    route = "uploadedFiles/%s" % str(sha256)
    if os.path.exists(route):
        f = open(route, 'rb')
        dataFile = f.read()
        sha256 = hashlib.sha256(dataFile).hexdigest()
        mySocket.send_multipart((dataFile, sha256.encode('utf-8')))
    else:
        mySocket.send_multipart((''.encode('utf-8'), ''.encode('utf-8')))

if len(sys.argv) != 3:
    sys.stderr.write("Se debe usar: python server.py [host] [proxyHost]")
    raise SystemExit(1)

def main(host):
    context = zmq.Context()
    mySocket = context.socket(zmq.REP)
    mySocket.bind("tcp://*{}".format(host[host.index(":"):]))
    if not os.path.exists("uploadedFiles"):
        os.mkdir("uploadedFiles")
    while True:
        message = mySocket.recv_multipart()
        accion = message[0].decode('utf-8')
        if accion == 'upload':
            receiveFile(message[1].decode('utf-8'), message[2], message[3].decode('utf-8'), message[4].decode('utf-8'), mySocket)
        elif accion == 'download':
            sendFile(message[1].decode('utf-8'), mySocket)

if __name__ == "__main__":
    if registerServer(sys.argv[1], sys.argv[2]):
        main(sys.argv[1])