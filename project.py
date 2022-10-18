#pip install flask
#python -m flask --app project --debug run

from flask import Flask
from flask import send_from_directory

app = Flask(__name__)

@app.route("/")
def default():
    return send_from_directory("html", "index.html")

@app.route("/gethotel")
def gethotel():
    return "<p>gethotel</p>"

if __name__ == '__main__':
    app.run(debug=True)
