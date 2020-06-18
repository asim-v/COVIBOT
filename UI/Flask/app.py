from flask import Flask, render_template
from flask_session import Session
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# cred = credentials.Certificate('keyfile.json')
# firebase_admin.initialize_app(cred,{"databaseURL":"https://colabotz.firebaseio.com"})


# Import database module.
from firebase_admin import db

ref = db.reference('extraction')
#snapshot = ref.order_by_key().limit_to_first(1).get()
snapshot = ref.order_by_child('rt_OgRetwCount').limit_to_last(2).get()



print(json.dumps(snapshot, indent=4, sort_keys=True))

#posts = db.child("extraction").shallow().limit_to_first(5).get()  #Funciona
#posts = db.child("extraction").order_by_key().get()               #Funciona
#posts = db.child("extraction").order_by_child("rt_OgFavCount").limit_to_first(5).get()#.val()

app = Flask(__name__)
@app.route('/')
def index():
	return render_template("index.html")	
