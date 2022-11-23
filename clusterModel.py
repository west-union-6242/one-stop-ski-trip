from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
import numpy as np
import csv
import urllib.request, json

url1 = "https://api.weather.gov/points/{},{}"

with open("data/resort.csv", encoding="utf-8") as resorts:
    reader = csv.DictReader(resorts)
    count = 0
    for row in reader:
        print("name:", row["resort_name"], "lat:", row["lat"], "lon:", row["lon"])
        forecast = -1
        with urllib.request.urlopen(url1.format(row["lat"], row["lon"])) as url:
            grid = json.load(url)
            forecast = grid["properties"]["forecast"]
            print("url:", forecast)
        if forecast != -1:
            with urllib.request.urlopen(forecast) as url:
                weather = json.load(url)
                print(weather["properties"]["periods"])
        count += 1
        if count > 0:
            break

iris = load_iris()

accuracy = 0
while accuracy < 50:
    km = KMeans(3)
    km.fit(iris.data)
    print(km.cluster_centers_)
    print(iris.target)
    print(km.labels_)
    matches = (iris.target == km.labels_)
    print(matches)
    accuracy = np.sum(matches) / len(matches) * 100
print("accuracy:", accuracy)

