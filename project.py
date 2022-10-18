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

if __name__ == '__main__':
    db = dbaccess.dataproc()
    conn = db.create_connection("westunion.db")
    try:
        conn.execute("drop table if exists airbnb;")
        conn.execute("drop table if exists resort;")
    except Exception as e:
        print("error in drop query", e)
    app.run(debug=False)

