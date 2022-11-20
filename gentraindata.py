
import pyautogui as pg
import pyperclip as pc
from datetime import datetime as dt
import time
import re
import os
import csv

def extractprice(url):
    t1 = dt.now()
    pg.leftClick(279, 1053, 1, 1)
    time.sleep(5)
    pg.typewrite(url)
    pg.press("enter")
    time.sleep(15)
    pg.leftClick(44, 156, 1, 1)
    time.sleep(1)
    pg.hotkey("ctrl", "a")
    time.sleep(1)
    pg.hotkey("ctrl", "c")
    time.sleep(1)
    #pg.leftClick(44, 156, 1, 1)
    #pg.leftClick(1097, 22, 1, 1)
    pg.hotkey("alt", "f4")
    time.sleep(1)
    t2 = dt.now()
    print("timediff:", str(t2 - t1))
    return pc.paste()

mystr = ""
folder = "C:/temp/one-stop-ski-trip/data/hotel"
for fn in os.listdir(folder):
    f = os.path.join(folder, fn)
    if os.path.isfile(f):
        with open(f, encoding = "utf8") as csvfile:
            csvread = csv.reader(csvfile, delimiter=",")
            lcount = 0
            for row in csvread:
                try:
                    if lcount > 0 and mystr == "": #non empty
                        url = row[-1]
                        mystr = extractprice(url)
                        mystr = re.sub(r'[^a-zA-Z0-9$ ]', '?', mystr)
                        mystr = mystr.lower()
                        try:
                            idx = mystr.index("night")
                            print("found night")
                        except Exception as ex:
                            print("notfound night")
                    row.append(mystr) #indent
                    with open("trainingdata.csv", "a") as ofile:
                        csvwrite = csv.writer(ofile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
                        csvwrite.writerow(row)
                except Exception as e:
                    pass
                if lcount > 10:
                    break
                lcount += 1

