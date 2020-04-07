import sys
import zmq
import time

context = zmq.Context()

fan = context.socket(zmq.PULL)
fan.bind("tcp://*:5558")

def main(fan):
    tstart = None
    indexRow = None
    matrixResult = []
    firstElement = True
    while True:
        s = fan.recv_multipart()
        print(s)
        row = int(s[1].decode('utf-8'))
        if int(s[1].decode('utf-8')) == 0 and firstElement:
            tstart = time.time()
            firstElement = False
        if row != indexRow:
            matrixResult.append([])
            matrixResult[row].insert(int(s[2].decode('utf-8')), int(s[0].decode('utf-8')))
            indexRow = row
        else:
            matrixResult[indexRow].insert(int(s[2].decode('utf-8')), int(s[0].decode('utf-8')))
        if len(matrixResult) == int(s[3].decode('utf-8')):
            if len(matrixResult[int(s[3].decode('utf-8')) - 1]) == int(s[4].decode('utf-8')):
                print(matrixResult)
                tend = time.time()
                print("Total elapsed time: %d msec" % ((tend-tstart)*1000))
                break


if __name__ == "__main__":
    main(fan)