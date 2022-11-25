from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
import numpy as np
import csv
import urllib.request, json
import time
import os.path as osp
import pandas as pd
import matplotlib.pyplot as plt

download = False
output = False
delay = 1
retry = 9
maxcluster = 10
bestcluster = 5
infile = "data/resort.csv"
outfile = "public/resort_weather.csv"
outfile2 = "public/resort_cluster.csv"

#download weather
if download:
    dataf = np.array([])
    with open(infile, encoding="utf-8") as resorts:
        reader = csv.reader(resorts)
        count = 0
        for row in reader:
            bad = 1
            while bad > 0:
                if count > 0:
                    try:
                        print("name:", row[0], "lat:", row[14], "lon:", row[15])
                        url_format = "https://api.weather.gov/points/{},{}"
                        time.sleep(delay)
                        with urllib.request.urlopen(url_format.format(row[14], row[15])) as url:
                            grid = json.load(url)
                            forecast = grid["properties"]["forecast"]
                            time.sleep(delay)
                            with urllib.request.urlopen(forecast) as url:
                                weather = json.load(url)
                                periods = weather["properties"]["periods"]
                                for i in range(len(periods)):
                                    if periods[i]["isDaytime"]:
                                        row.append(periods[i]["temperature"])
                        delay = 1
                        bad = 0
                    except:
                        delay = 20
                        bad += 1
                        if (bad > retry):
                            for i in range(7):
                                row.append(77)
                            bad = 0
                        pass
                else:
                    bad = 0
            if len(row) == 23:
                if len(dataf)==0:
                    dataf = np.array([row])
                else:
                    dataf = np.append(dataf, [row], axis=0)
            count += 1
    print(dataf.shape)
    with open(outfile, mode="w", encoding="utf-8") as ofile:
        csvwrite = csv.writer(ofile, delimiter=",", quotechar="\"", lineterminator="\n", quoting=csv.QUOTE_ALL)
        for i in range(dataf.shape[0]):
            csvwrite.writerow(dataf[i].tolist())

#elbow/silhouete methods
km = None
xx = []
yy = []
for i in range(maxcluster):
    if osp.exists(outfile):
        dataf = (pd.read_csv(outfile, header=None, delimiter=",")).to_numpy()
        #print(dataf.shape)
        km = KMeans(i+1)
        km.fit(dataf[:,[-1,-2,-3,-4,-5,-6,-7]])
        #print(km.cluster_centers_)
        #print(km.labels_)
        sse = 0
        for j in range(dataf.shape[0]):
            sse = np.sum((dataf[j,[-1,-2,-3,-4,-5,-6,-7]]-km.cluster_centers_[int(km.labels_[j])])**2)
        print("sse:", i+1, sse)
        xx.append(i+1)
        yy.append(sse)
    else:
        print("file not exists:", outfile)
        exit(0)
plt.plot(xx, yy)
plt.xlabel("Number of Clusters")
plt.ylabel("SSE")
plt.title("Weather Analysis")
plt.show()

#output clusters
if output:
    is_sorted = lambda a: np.all(a[:-1] <= a[1:])
    ordered = False
    while not ordered:
        km = KMeans(bestcluster)
        km.fit(dataf[:,[-1,-2,-3,-4,-5,-6,-7]])
        print(km.cluster_centers_)
        print(km.labels_)
        l = []
        for i in range(km.cluster_centers_.shape[0]):
            l.append(np.average(km.cluster_centers_[i]))
        print(l)
        if is_sorted(np.array(l)):
            ordered = True
    with open(outfile2, mode="w", encoding="utf-8") as ofile:
        csvwrite = csv.writer(ofile, delimiter=",", quotechar="\"", lineterminator="\n", quoting=csv.QUOTE_ALL)
        for i in range(dataf.shape[0]):
            l = dataf[i].tolist()
            for j in range(km.cluster_centers_.shape[1]):
                l.append(km.cluster_centers_[int(km.labels_[i]),j])
            l.append(np.average(km.cluster_centers_[int(km.labels_[i])]))
            l.append(km.labels_[i])
            csvwrite.writerow(l)


