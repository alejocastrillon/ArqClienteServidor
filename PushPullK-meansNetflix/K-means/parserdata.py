import json
import statistics
with open("myusers.json", "r") as fu:
    users = json.load(fu)
    dataUser = [int(key) for key in users.keys()]
    desvest = statistics.stdev(dataUser)
    media = statistics.median(dataUser)
    print(desvest, media)

print("Usuarios cargados")
ratings = [None for _ in range(len(users))]
movie = 0
with open("combined_data_1.txt", "r") as file:
    for line in file:
        line = line[:-1]
        if line[-1] == ":":
            movie = int(line[:-1])
            print(f"\rPelicula {movie}", end="")
        else:
            sp = line.split(",")
            user = sp[0]
            rate = int(sp[1])
            user_id = users[user]
            if not ratings[user_id]:
                ratings[user_id] = {}
            ratings[user_id][movie] = rate
print("")
print("########################\n###Archivo terminado###\n########################")

del users
contador = 0
quantityLines = 1000
for us in ratings:
    if contador % quantityLines == 0:
        if "f" in locals():
            f.close()
        f = open(f"dataFiles/part{int(contador/quantityLines)}.txt", "w+")
    c = ""
    for m in us:
        c += f"({m} {us[m]}),"
    c = c[:-1]+"\n"
    f.write(c)
    print(f"\rLinea {contador}",end="")
    contador += 1
print("\nTerminado")