#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
import os

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def receiveFile(title, content):
    route = "uploadedFiles/%s" % str(title)
    f = open(route, 'wb')
    f.write(content)
    f.close()

def listFolder():
    objects = []
    for (dirpath, dirnames, filenames) in os.walk("uploadedFiles"):
        for file in filenames:
            socket.send_string(file)

while True:
    if not os.path.exists("uploadedFiles"):
        os.mkdir("uploadedFiles")
    #  Wait for next request from client
    message = socket.recv_multipart()
    accion = message[0]
    if accion == b'upload':
        receiveFile(message[1], message[2])
    elif accion == b'list':
        listFolder()
    
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

