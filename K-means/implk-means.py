import csv
import random

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cluster = -1
        self.minDist = 100000000

    def distanceWithOtherPoint(self, p):
        print(p.x)
        print(p.y)
        print(self.x)
        print(self.y)
        return pow((int(p.x) - int(self.x)), 2) + pow((int(p.y) - int(self.y)), 2)

p1 = Point(0, 0)
p2 = Point(3, 4)
print(p1.distanceWithOtherPoint(p2))


def loadData():
    dataSet = []
    with open('data.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            point = Point(row["Annual Income (k$)"], row["Spending Score (1-100)"])
            dataSet.append(point)
    return dataSet

dataSet = loadData()

def generateCluster(k):
    clusters = []
    for i in range(k):
        cluster = Point(random.randint(0, 150), random.randint(0, 150))
        clusters.append(cluster)
    return clusters

clusters = generateCluster(5)

def kMeansClustering(dataSet, iteration, centroids):
    for i in range(iteration):
        for centroid in centroids:
            for data in dataSet:
                distance = centroid.distanceWithOtherPoint(data)
                if distance < data.minDist:
                    data.minDist = distance
                    data.cluster = centroids.index(centroid)
        nPoints = []
        sumX = []
        sumY = []
        for i in range(len(centroids)):
            nPoints.append(0)
            sumX.append(0)
            sumY.append(0)
        for data in dataSet:
            nPoints[data.cluster] += 1
            sumX[data.cluster] += int(data.x)
            sumY[data.cluster] += int(data.y)
            data.minDist = 100000000
        for centroid in centroids:
            n = nPoints[centroids.index(centroid)]
            if n != 0:
                centroid.x = sumX[centroids.index(centroid)] / n
                centroid.y = sumY[centroids.index(centroid)] / n
    
    print(dir(dataSet[0]))
    print(dataSet[0].__dict__)
    with open('output.csv', mode='w') as file:
        writer = csv.DictWriter(file, fieldnames=['y', 'x', 'minDist', 'cluster'])
        writer.writeheader()
        for data in dataSet:
            writer.writerow(data.__dict__)

kMeansClustering(dataSet, 10, clusters)