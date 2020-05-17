import json

users = {}
cont = 0
with open("combined_data_1.txt", "r") as file:
    for line in file:
        line = line[:-1]
        if line[-1] != ":":
            sp = line.split(",")
            user = sp[0]
            if not(user in users):
                print("No esta {user}".format(user= user))
                users[user] = cont
                cont += 1

print(users)

with open('myusers.json', 'w') as outfile:
    json.dump(users, outfile)