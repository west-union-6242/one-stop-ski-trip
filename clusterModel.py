from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
import numpy as np
import csv
import urllib.request, json
import time

download = True
delay = 1
retry = 9
infile = "data/resort.csv"
outfile = "public/resort_weather.csv"

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

km = KMeans(5)
km.fit(dataf[:,[-1,-2,-3,-4,-5,-6,-7]])
print(km.cluster_centers_)
print(km.labels_)

