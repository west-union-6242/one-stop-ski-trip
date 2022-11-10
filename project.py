#pip install flask
#python project.py

from flask import Flask
from flask import send_from_directory
from flask import request

import sqlite3
from sqlite3 import Error

import math
import csv
import json
import random
import os
from logic.resort_recommender import resort_recommender

class dataproc():
    def create_connection(self, path):
        self.connection = None
        try:
            self.connection = sqlite3.connect(path)
            self.connection.text_factory = str
        except Error as e:
            print("Error:" + str(e))
        return self.connection

    def execute_query(self, query):
        try:
            assert query != "", "Query Blank"
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
        except Error as e:
            print("Error:" + str(e))
        return None

    def close(self):
        try:
            self.connection.close()
        except Error as e:
            print("Error:" + str(e))
        return None


app = Flask(__name__)

@app.route("/")
def default():
    return send_from_directory("html", "index.html")


@app.route('/resort-preference')
def resort_preference():
    return send_from_directory("html", 'resort-preference.html')


@app.route('/resort-recommend')
def resort_recommend():
    difficulty = request.args.get('difficulty')
    goal = request.args.get('goal')
    fav_resort = request.args.get('fav_resort')
    print('form data:', difficulty, goal, fav_resort)
    resort_recommender(difficulty, goal, fav_resort)

    return send_from_directory("html", "resort-recommend.html")


@app.route("/nearby")
def get_nearby_from_resort():
    return send_from_directory("html", "nearby.html")

@app.route("/gethotel")
def gethotel():
    result = None
    lat = 40.78130111899314
    lon = -73.96732919372586
    limit = 10
    try:
        limit = float(request.args.get('limit'))
        print("limit", limit)
        if limit > 100:
            limit = 100 #return no more than 100 max
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except Exception as e:
        #print("error process params:", e)
        pass
    try:
        #print("lat:", lat, "lon:", lon, "limit", limit)
        sinlat = math.sin(math.radians(lat))
        coslat = math.cos(math.radians(lat))
        sinlon = math.sin(math.radians(lon))
        coslon = math.cos(math.radians(lon))
        headings = ["id", "address", "lat", "lon", "name", "numberOfGuests", "roomType", "stars", "url", "price"]
        db = dataproc()
        conn = db.create_connection("westunion.db")
        curr = conn.execute("select *, ((sinlat * {}) + (coslat * {})*((sinlon * {}) + (coslon * {}))) as dist from airbnb order by dist desc limit {}".format(sinlat, coslat, sinlon, coslon, limit))
        result = [dict((x, y) for x, y in zip(headings, row)) for row in curr.fetchall()]
        db.close()
    except Exception as e:
        print("error in returning hotel json:", e)
    return json.dumps(result)

@app.route("/getstatesgeo")
def getstatesgeo():
    file = open("data/geo_data/states.json", encoding="utf8")
    data = json.load(file)
    return json.dumps(data)  

@app.route("/reload")
def reload():
    try:
        db = dataproc()
        db.create_connection("westunion.db")
        db.execute_query("drop table if exists airbnb;")
        db.execute_query("drop table if exists resort;")
        db.execute_query("create table airbnb (id integer primary key autoincrement, address varchar(256), lat float, lon float, name varchar(64), numberOfGuests int, roomType varchar(16), stars float, url varchar(256), price float, sinlat float, coslat float, sinlon float, coslon float);")

        folder = "data/hotel"
        for fn in os.listdir(folder):
            f = os.path.join(folder, fn)
            if os.path.isfile(f):
                with open(f, encoding = "utf8") as csvfile:
                    csvread = csv.reader(csvfile, delimiter=",")
                    lcount = 0
                    for row in csvread:
                        if lcount > 0:
                            for i in range(len(row)):
                                if row[i] == "" and i not in {0, 3, 5, 7}:
                                    row[i] = 0
                                if i in {0, 3, 5, 7}:
                                    row[i] = row[i].replace("'", "")
                            price = round(random.random() * 800 + 200, 2)
                            lat = float(row[1])
                            lon = float(row[2])
                            sql = "insert into airbnb (address, lat, lon, name, numberOfGuests, roomType, stars, url, price, sinlat, coslat, sinlon, coslon) values ('{}',{},{},'{}',{},'{}',{},'{}', {}, {}, {}, {}, {});".format(row[0], lat, lon, row[3], row[4], row[5], row[6], row[7], price, math.sin(math.radians(lat)), math.cos(math.radians(lat)), math.sin(math.radians(lon)), math.cos(math.radians(lon)))
                            db.execute_query(sql)
                        lcount += 1

        db.close()
    except Exception as e:
        print("error in loading database:", e)
    return "<p>done</p>"

if __name__ == '__main__':
    app.run(debug=False)


