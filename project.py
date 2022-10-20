#pip install flask
#python project.py

from flask import Flask
from flask import send_from_directory
import dbaccess

app = Flask(__name__)

@app.route("/")
def default():
    return send_from_directory("html", "index.html")

@app.route("/gethotel")
def gethotel():
    return "<p>gethotel</p>"

@app.route("/reload")
def reload():
    try:
        db = dbaccess.dataproc()
        db.create_connection("westunion.db")
        db.execute_query("drop table if exists airbnb;")
        db.execute_query("drop table if exists resort;")
        db.close()
    except Exception as e:
        print("error in drop query", e)
    return "<p>done</p>"

if __name__ == '__main__':
    app.run(debug=False)

