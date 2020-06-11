from fireo.models import Model
from fireo.fields import TextField,NumberField
from flask import Flask, render_template

#solo para hacer pruebas
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keyfile.json"
#solo para hacer pruebas


class Post(Model):
    content = TextField()
    urgency = NumberField()
    category = TextField()


posts = Post.collection.fetch()

app = Flask(__name__)
@app.route('/')
def index():
    return render_template("index.html",error = 0,posts = posts)

user = Post.collection.delete()