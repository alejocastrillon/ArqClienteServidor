#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

print("Ingrese la operación")
s = input()
socket.send_string(s)

#  Get the reply.
message = socket.recv()
print("Received reply [ %s ]" % (message))