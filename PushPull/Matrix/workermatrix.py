import zmq
import sys
import ast

context = zmq.Context()

work = context.socket(zmq.PULL)
work.connect("tcp://localhost:5557")

sink = context.socket(zmq.PUSH)
sink.connect("tcp://localhost:5558")

def main():
    while True:
        s = work.recv_multipart()
        print(s)
        sumatory = 0
        for i in range(len(ast.literal_eval(s[0].decode('utf-8')))):
            sumatory += ast.literal_eval(s[0].decode('utf-8'))[i] * ast.literal_eval(s[1].decode('utf-8'))[i]
        print(sumatory)
        sink.send_multipart((str(sumatory).encode('utf-8'), s[2], s[3], s[4], s[5]))

if __name__ == "__main__":
    main()