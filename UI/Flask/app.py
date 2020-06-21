from flask import Flask, render_template, request, session , redirect, url_for,send_from_directory
from markupsafe import escape
from flask_session import Session
import json
import firebase_admin 
from firebase_admin import firestore
from collections import namedtuple
from firebase_admin import db

##EJEMPLOS
# posts = db.child("extraction").shallow().limit_to_first(5).get()  #Funciona
# posts = db.child("extraction").order_by_key().get()               #Funciona
# posts = db.child("extraction").order_by_child("rt_OgFavCount").limit_to_first(5).get()#.val()
##EJEMPLOS


#Sessions, init flask
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["FLASK_ENV"] = "development"
app.config["FLASK_DEBUG"] = "1"
Session(app)

# LOCAL AUTH
from firebase_admin import credentials
cred = credentials.Certificate('keyfile.json')
firebase_admin.initialize_app(cred,{"databaseURL":"https://colabotz.firebaseio.com"})
# LOCAL AUTH 

##STATIC
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)
@app.route('/images/<path:path>')
def send_img(path):
    return send_from_directory('static/images', path)
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)
@app.route('/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('static/fonts', path)
@app.route('/favicons/<path:path>')
def send_icons(path):
    return send_from_directory('static/favicons', path)



def GetPosts(sortby = 'rt_OgRetwCount',limit=1000):       
    
    # Importa database module.    
    ref = db.reference('extraction') #Establece ref a grupo de posts
    snapshot = ref.order_by_child(sortby).limit_to_last(limit).get()  #Posts más retwiteados    
    
    # Parsea JSON en un objeto correspondiente por cada keys del dict.
    total_posts = []
    def _json_object_hook(d): return namedtuple("tweet", d.keys())(*d.values())
    def json2obj(x): 
        data = str(x).replace('False','"False"').replace('True','"True"').replace("'",'"')
        return json.loads(data, object_hook=_json_object_hook)
    for post in snapshot:
        #print(json.dumps(snapshot[post], indent=4, sort_keys=True))    #PrettyPrint
        try:total_posts.append(json2obj(snapshot[post]))
        except:pass
    return (total_posts[::-1],snapshot) #Obtiene la lista de objetos y el json

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['email'] = request.form['email']
        session['password'] = request.form['password']
        return redirect(url_for('dashboard'))
    # return '''
    #     <form method="post">
    #         <p><input type=text name=email></p>
    #         <p><input type=text name=password></p>
    #         <p><input type=submit value=Login></p>
    #     </form>
    # '''
    return render_template('sign-in-img.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/signup')
def signup():
    return render_template('sign-up-img.html')

@app.route('/forgot')
def forgot():
    return render_template('forget-pass-img.html')


@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if session.get("posts") is None:
        session["posts"] = [GetPosts()[1]]
    # if request.method == "POST":
    #     note = request.form.get("note")
    #     session["notes"].append(note)#Only append the note to the specific session
        
    return render_template("index.html",posts=GetPosts()[0])



