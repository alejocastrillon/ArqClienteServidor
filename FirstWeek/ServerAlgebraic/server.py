#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    operacion = message.split()
    print(operacion)
    resultado = None
    if(operacion[1] == b'+'):
        resultado = float(operacion[0]) + float(operacion[2])
    elif (operacion[1] == b'-'):
        resultado = float(operacion[0]) - float(operacion[2])
    elif (operacion[1] == b'*'):
        resultado = float(operacion[0]) * float(operacion[2])
    elif (operacion[1] == b'/'):
        resultado = float(operacion[0]) / float(operacion[2])
    elif (operacion[1] == b'^'):
        resultado = pow(float(operacion[0]), float(operacion[2]))
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send_string(str(resultado))

