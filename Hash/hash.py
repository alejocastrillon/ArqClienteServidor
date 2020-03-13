M = 256   

"""
Convierte una cadena de caracteres a su equivalente en binario
"""
def binaryString(string):
    binarystring = ''
    for char in string:
        b = format(ord(char), 'b')
        while len(b) < 8:
            b = '0' + b
        binarystring = binarystring + b
    return binarystring + '1'

"""
Añade ceros al final de la cadena para completar la longitud M*2
"""
def kZero(text):
    binaryText = binaryString(text)
    size = len(binaryText)
    binarySize = "{0:b}".format(size - 1)
    k = ((M*2)-((M/8)*2)) - size
    for x in range(int(k)):
        binaryText = binaryText + '0'
    while len(binarySize) < ((M/8)*2):
        binarySize = '0' + binarySize
    return binaryText + binarySize

"""
Recorre mensaje binario en conjunto de (M/8) bits
"""
def parseMessage(binaryText):
    i = 0
    for item in range(0, len(binaryText), int(M/8)):
        print(binaryText[item:int(item+(M/8))])
        print(i)
        i += 1
        
def main():
    print("Ingresa la cadena:")
    text = input()
    binText = kZero(text)
    print("Cadena binaria %s" % binText)
    parseMessage(binText)

if __name__ == '__main__':
    main()
    