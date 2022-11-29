
from apify_client import ApifyClient
from datetime import datetime
import os
import csv
import urllib.request, json

def apify_download(token, taskid, addr):
    try:
        apify_client = ApifyClient(token)
        task_client = apify_client.task(taskid)
        task = task_client.get()
        task["input"]["locationQuery"] = addr
        print("Location:", task["input"]["locationQuery"])
        task_client.update(task_input=task["input"])
        task_client = apify_client.task(taskid)
        task_call = task_client.call()
        dataset_client = apify_client.dataset(task_call["defaultDatasetId"])
        csv = dataset_client.download_items(item_format="csv")
        fname = "dataset_airbnb-scraper-task_"
        fname += str(datetime.now()).replace(" ", "_").replace(":", "-").replace(".", "-") + "_"
        fname += addr.lower().replace(",", "_").replace(" ", "").replace(".", "") + ".csv"
        with open(fname, "wb") as csvfile:
            csvfile.write(csv)
    except Exception as e:
        print("apify_download catch:", e)

req = "https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&key=<token>"

f = "data/resort.csv"
with open(f, encoding = "utf8") as infile:
    reader = csv.DictReader(infile)
    count = 0
    for row in reader:
        if count >= 0:
            print("count:", count, "resort_name:", row["resort_name"], "lat:", row["lat"], "lon:", row["lon"])
            with urllib.request.urlopen(req.format(row["lat"], row["lon"])) as url:
                resp = json.load(url)
                addr_comp = resp["results"][0]["address_components"]
                cid = -1
                for idx in range(len(addr_comp)):
                    if "country" in addr_comp[idx]["types"]:
                        cid = idx
                        break
                if cid != -1:
                    addr = addr_comp[cid-2]["long_name"] + ", " + addr_comp[cid-1]["long_name"] + ", " + addr_comp[cid]["long_name"]
                    print(addr)
                    apify_download("<token>", "<task>", addr)
        count += 1

