from flask import Flask, render_template
from flask_session import Session
import pyrebase

config = {
  "apiKey": "AIzaSyDVpxOSaZH08jzKvQJhssW06sloEHz5voc",
  "authDomain": "colabotz.firebaseapp.com",
  "databaseURL": "https://colabotz.firebaseio.com",
  "storageBucket": "colabotz.appspot.com",
  "serviceAccount": "keyfile.json"
}
firebase = pyrebase.initialize_app(config)

db = firebase.database()
db.child("colabotz").child("extraction")

app = Flask(__name__)
@app.route('/')
def index():
    return render_template("index.html",error = 0)
