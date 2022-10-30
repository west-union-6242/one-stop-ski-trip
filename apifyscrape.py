
from apify_client import ApifyClient
from datetime import datetime

def apify_download(token, taskid, addr):
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
    fname += addr.lower().replace(",", "_").replace(" ", "_") + ".csv"
    with open(fname, "wb") as csvfile:
        csvfile.write(csv)

