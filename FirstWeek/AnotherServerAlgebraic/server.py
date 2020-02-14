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
operators = []
resultado = 0
firstOperator = True

while True:
    #  Wait for next request from client
    message = socket.recv()
    if message == b'+' or message == b'-' or message == b'*' or message == b'/' or message == b'^':
        resultado = 0
        for x in range(0, len(operators), 2):
            a = operators[x]
            b = 0
            print(a)
            if x + 1 < len(operators):
                b = operators[x + 1]
            print(b)
            if message == b'+':
                resultado = resultado + a + b
            elif message == b'-':
                if firstOperator:
                    resultado = a - b
                else:
                    resultado = resultado - a - b
            elif message == b'*':
                if firstOperator:
                    resultado = a * b
                else:
                    resultado = resultado * (a * b)
            elif message == b'/':
                if firstOperator:
                    resultado = a / b
                else:
                    resultado = resultado / (a / b)
            elif message == b'^':
                if firstOperator:
                    resultado = pow(a, b)
                else:
                    resultado = pow(resultado, pow(a, b))
            firstOperator = False
    else:
        operators.append(float(message))
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send_string(str(resultado))

