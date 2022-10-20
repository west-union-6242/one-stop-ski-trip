#pip install flask
#python project.py

from flask import Flask
from flask import send_from_directory
import dbaccess
import csv
import json

app = Flask(__name__)

@app.route("/")
def default():
    return send_from_directory("html", "index.html")

@app.route("/gethotel")
def gethotel():
    headings = ["id", "address", "lat", "lon", "name", "numberOfGuests", "roomType", "stars", "url"]
    result = None
    try:
        db = dbaccess.dataproc()
        conn = db.create_connection("westunion.db")
        curr = conn.execute("select * from airbnb order by id limit 10")
        result = [dict((x, y) for x, y in zip(headings, row)) for row in curr.fetchall()]
        db.close()
    except Exception as e:
        print("error in loading database:", e)
    return json.dumps(result)

@app.route("/reload")
def reload():
    try:
        db = dbaccess.dataproc()
        db.create_connection("westunion.db")
        db.execute_query("drop table if exists airbnb;")
        db.execute_query("drop table if exists resort;")
        db.execute_query("create table airbnb (id integer primary key autoincrement, address varchar(256), lat float, lon float, name varchar(64), numberOfGuests int, roomType varchar(16), stars float, url varchar(256));")

        with open("data/airbnb.csv", encoding = "utf8") as csvfile:
            csvread = csv.reader(csvfile, delimiter=",")
            lcount = 0
            for row in csvread:
                if lcount > 0:
                    for i in range(len(row)):
                        if row[i] == "" and i not in {0, 3, 230, 232}:
                            row[i] = 0
                        if i in {0, 3, 230, 232}:
                            row[i] = row[i].replace("'", "")
                    sql = "insert into airbnb (address, lat, lon, name, numberOfGuests, roomType, stars, url) values ('{}',{},{},'{}',{},'{}',{},'{}');".format(row[0], row[1], row[2], row[3], row[4], row[230], row[231], row[232])
                    db.execute_query(sql)
                lcount += 1

        db.close()
    except Exception as e:
        print("error in loading database:", e)
    return "<p>done</p>"

if __name__ == '__main__':
    app.run(debug=False)

