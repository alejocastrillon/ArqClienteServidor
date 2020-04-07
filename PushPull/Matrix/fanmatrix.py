import zmq
import sys
import ast

context = zmq.Context()

matrixA = [[1, 2, -3], [4, 0, -2]]
matrixB = [[3, 1], [2, 4], [-1, 5]]

workers = context.socket(zmq.PUSH)
workers.bind("tcp://*:5557")

sink = context.socket(zmq.PUSH)
sink.connect("tcp://localhost:5558")

def  main():
    indexRow = 0
    if len(matrixA[0]) == len(matrixB):
        for rowA in matrixA:
            indexColumn = 0
            while indexColumn < len(matrixA):
                columnB = []
                for rowB in matrixB:
                    columnB.append(rowB[indexColumn])
                workers.send_multipart((str(rowA).encode('utf-8'), str(columnB).encode('utf-8'), str(indexRow).encode('utf-8'), str(indexColumn).encode('utf-8'), str(len(matrixA)).encode('utf-8'), str(len(matrixB[0])).encode('utf-8')))
                indexColumn += 1
            indexRow += 1
    else:
        sys.stderr.write("La cantidad de columnas en la matriz A debe ser igual a la cantidad de filas en la matriz B")
        raise SystemError(1)


if __name__ == "__main__":
    print("Para lanzar la tarea, asegurese que los workers esten habilitados. Si es asi, presione la tecla ENTER")
    _=input()
    print("Enviando tareas")
    main()