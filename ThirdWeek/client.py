import zmq
import sys
import json
import os
import hashlib

PS = 1024*1024*5

def clear(): 
    if os.name == 'nt': 
        _ = os.system('cls') 
    else: 
        _ = os.system('clear') 


def upload(fileName, ipNode):
    if not os.path.isfile(fileName):
        sys.stderr.write("Not exists this file")
        raise SystemExit(1)
    socket = zmq.Context().socket(zmq.REQ)
    ipNode = "tcp://%s" % ipNode
    socket.connect(ipNode)
    generalHash = hashlib.sha256()
    dataHash = {
        "name": fileName,
        "parts": []
    }
    iterator = 0
    file = open(fileName, "rb")
    while True:
        file.seek(iterator * PS)
        dataFile = file.read(PS)
        if not dataFile:
            dataHash["generalHash"] = generalHash.hexdigest()
            d = {
                "action": "uploadIndex",
                "name": generalHash.hexdigest()
            }
            socket.send_json(d)
            message = socket.recv_multipart()
            send = False
            while not send:
                if message[0].decode('utf-8') == "ok":
                    socket.send_json(json.dumps(dataHash))
                    print(socket.recv())
                    send = True
                else:
                    socket.disconnect(ipNode)
                    ipNode = message[1].decode('utf-8')
                    socket.connect(ipNode)
                    socket.send_json(d)
                    message = socket.recv_multipart()
            clear()
            print('Upload file {file} succesfully sha {sha} '.format(file=fileName, sha=generalHash.hexdigest()))
            break
        else:
            generalHash.update(dataFile)
            shapart = hashlib.sha256(dataFile).hexdigest()
            d = {
                "action": "upload",
                "name": shapart
            }
            socket.send_json(d)
            message = socket.recv_multipart()
            send = False
            dataHash["parts"].append(shapart)
            while not send:
                if message[0].decode('utf-8') == "ok":
                    socket.send_multipart((dataFile, shapart.encode('utf-8')))
                    socket.recv()
                    send = True
                else:
                    socket.disconnect(ipNode)
                    ipNode = message[1].decode('utf-8')
                    socket.connect(ipNode)
                    socket.send_json(d)
                    message = socket.recv_multipart()
            clear()
            print('Upload file {fileName} part {iterator} succesfully'.format(fileName = fileName, iterator = iterator))
        iterator += 1

def download(fileObject, ipNode):
    d = {
        "action": "downloadIndex",
        "name": fileObject
    }
    ipNode = "tcp://%s" % ipNode
    index = {}
    socket = zmq.Context().socket(zmq.REQ)
    socket.connect(ipNode)
    socket.send_json(d)
    message = socket.recv_multipart()
    findIndex = False
    while not findIndex:
        if message[0].decode('utf-8') == "found":
            index = json.loads(message[1].decode('utf-8'))
            findIndex = True
            i = 1
            generalHash = hashlib.sha256()
            for file in index["parts"]:
                d = {
                    "action": "download",
                    "name": file
                }
                findPart = False
                socket.send_json(d)
                message = socket.recv_multipart()
                while not findPart:
                    if message[0].decode("utf-8") == "found":
                        shapart = hashlib.sha256(message[1]).hexdigest()
                        generalHash.update(message[1])
                        if shapart == message[2].decode('utf-8'):
                            fileWrite = open(index["name"], 'ab')
                            fileWrite.write(message[1])
                            fileWrite.close()
                            findPart = True
                            clear()
                            print("Donwloading file {name} part {i}/{part}".format(name=index["name"], i=i, part=len(index["parts"])))
                            i += 1
                        else:
                            clear()
                            sys.stderr.write("Corrupted file")
                            break;
                    else:
                        socket.disconnect(ipNode)
                        ipNode = message[1].decode('utf-8')
                        socket.connect(ipNode)
                        socket.send_json(d)
                        message = socket.recv_multipart()
            if generalHash.hexdigest() == index["generalHash"]:
                clear()
                print("File %s download succesfully" % index["name"])
            else:
                clear()
                print("File %s is corrupted" % index["name"])
                os.remove(index["name"])
        else:
            socket.disconnect(ipNode)
            ipNode = message[1].decode('utf-8')
            print(ipNode)
            socket.connect(ipNode)
            socket.send_json(d)
            message = socket.recv_multipart()
            
def main():
    action = sys.argv[1]
    fileObject = sys.argv[2]
    node = sys.argv[3]
    if len(sys.argv) != 4:
        sys.stderr.write("Se debe de usar python client.py [accion] [shafile | nombreArchivo] [ipNodo]")
        raise SystemError(1)
    if action == "upload":
        upload(fileObject, node)
    elif action == "download":
        download(fileObject, node)

main()