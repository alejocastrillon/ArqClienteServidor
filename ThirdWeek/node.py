import zmq
import os
import hashlib
import sys
import json
import random
import string

serverSocket = zmq.Context().socket(zmq.REP)
myHost = None
hostConnection = None

def getDistributedString():
    chars = []
    chars.extend(string.ascii_lowercase)
    chars.extend(string.ascii_uppercase)
    chars.extend(string.digits)
    return ''.join(random.choice(chars) for x in range(25))

def hashString(string):
    return hashlib.sha256(string.encode()).hexdigest()[:8]

def integerHash(hash):
    return int(hash, 16)

if len(sys.argv) <= 2:
    sys.stderr.write("Se debe especificar una acción\n")
    raise SystemExit(1)
else:
    accion = sys.argv[1]
    if accion == "principal":
        if len(sys.argv) == 3:
            myHost = sys.argv[2]
            serverSocket.bind("tcp://*:{}".format(myHost))
            print(integerHash(hashString(getDistributedString())))
        else:
            sys.stderr.write("Se debe especificar el host")
            raise SystemError(1)
    elif accion == "connect":
        if len(sys.argv) != 3:
            sys.stderr.write("Se debe usar: python node.py connect [host]")
            raise SystemExit(1)
        else:
            print(integerHash(hashString(getDistributedString())))