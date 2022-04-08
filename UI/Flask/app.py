'''
COVIBOT PLATFORM: 

OBJETIVO:
	AI platform:
		- Poder desplegar modelos de ia con el agente de escucha de twitter(buscar expandirse en el futuro) en la nube
			- Categorización de oferta y demanda.
			- Analisis de categorizacion de oferta y demanda
		- Agregar,previsualiza y estudiar dinámicamente columnas en la bd y commitear changes

	Interfaz:
		- Poder analizar, guardar, contactar automáticamente las publicaciones interesantes al usuario

	Registro:
		- Admin
		- Usuario
			- Ofrecedor.
			- Necesitador.
			- Ambos

TODO: 
	- Train new models
	- Nginx Routing
	- Cool Scrolling
	- Finish Security

IN PROGRESS:
	- Full Quering

DONE:
	- Interface Template


'''

# imports for flask
from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify,send_from_directory,make_response
from flask_mail import Mail, Message
#For File Management
from werkzeug.utils import secure_filename
from types import SimpleNamespace as Namespace
#Object Json Generator
from collections import namedtuple
import json
#Object Json Generator


#Twitter
# Imports from the Tweepy API
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
# To check if the file exist
import os.path
# Another imports to parse the json
import json
from urllib3.exceptions import ProtocolError




# imports for firebase
from firebase_admin import credentials, firestore, auth
import firebase_admin.db as rtdb
import firebase_admin
import firebase
from google.cloud import storage
from google.oauth2 import service_account

import sys#DEBUG
import os#DEBUG

# custom lib
import firebase_user_auth

# realtime communication
from flask_socketio import SocketIO, emit, send

import requests
import datetime
import random


CONFIG = {

}


##EJEMPLOS
# posts = db.child("extraction").shallow().limit_to_first(5).get()  #Funciona
# posts = db.child("extraction").order_by_key().get()			   #Funciona
# posts = db.child("extraction").order_by_child("rt_OgFavCount").limit_to_first(5).get()#.val()
#SIRVE PARA PROBAR COMO GUARDAR FILES
# blob = bucket.blob('my-test-file.txt')
# blob.upload_from_string('this is test content!')
#SIRVE PARA PROBAR COMO GUARDAR FILES
##EJEMPLOS


#Sessions, init flask
app = Flask(__name__)
app.secret_key = b'\xbd\x93K)\xd3\xeeE_\xfb0\xa6\xab\xa5\xa9\x1a\t'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["FLASK_ENV"] = "development"
app.config["FLASK_DEBUG"] = "1"
socketio = SocketIO(app, cors_allowed_origins="*")




# LOCAL AUTH
from firebase_admin import credentials
cred = credentials.Certificate(CONFIG)
default_app = firebase_admin.initialize_app(cred,{"databaseURL":"https://colabotz.firebaseio.com",'storageBucket': 'colabotz.appspot.com'})
#AUTH STORAGE
credentials = service_account.Credentials.from_service_account_info(CONFIG)
client = storage.Client(project='colabotz', credentials=credentials)
bucket = client.get_bucket('colabotz.appspot.com')
# LOCAL AUTH 




#USER AUTH
WEB_API_KEY = "AIzaSyDVpxOSaZH08jzKvQJhssW06sloEHz5voc"
user_auth = firebase_user_auth.initialize(WEB_API_KEY)
#USER AUTH


#Db references
db = firestore.client()
# users collection reference 
users_coll = db.collection(u"users")


#Twitter API
CON_KEY = ""
CON_KEY_SECRET = ""
ACC_TOKEN = ""
ACC_TOKEN_SECRET = ""
# Validate the Credentials
Auth = OAuthHandler(CON_KEY, CON_KEY_SECRET)
# Validate the Acces Tokens
Auth.set_access_token(ACC_TOKEN, ACC_TOKEN_SECRET)
api = tweepy.API(Auth)


def GetTweet(id):	   
	'''
		Obtiene tweet de la bd y actualiza el texto con el contenido completo
	'''

	# Importa database module.	
	data = rtdb.reference("extraction").order_by_child("tw_id_str").equal_to(id).limit_to_first(1).get()

	# Parsea JSON en un objeto correspondiente por cada keys del dict.
	def json2obj(x,show = False): 		

		#twitter.com/anyuser/status/541278904204668929

		def _json_object_hook(d): return namedtuple("tweet", d.keys())(*d.values())
		data = str(dict(x)[list(x.keys())[0]])
		data = str(data).replace(': False',': "False"').replace(': True',': "True"').replace("'",'"')

		if show == True: print(json.dumps(x, indent=4, sort_keys=True))
		return json.loads(data, object_hook=_json_object_hook)
	try:
		return dict(data)[list(data.keys())[0]]
	except Exception as e:
		return e
	#print(type(snapshot[post]),snapshot[post],json2obj(snapshot[post]))


def GetPosts(sortby = 'rt_OgRetwCount',limit=50):	   
	
	# Importa database module.	
	ref = rtdb.reference('extraction') #Establece ref a grupo de posts
	snapshot = ref.order_by_child(sortby).limit_to_last(limit).get()  #Posts más retwiteados	
	
	# Parsea JSON en un objeto correspondiente por cada keys del dict.
	total_posts = []
	def _json_object_hook(d): return namedtuple("tweet", d.keys())(*d.values())
	def json2obj(x): 
		data = str(x).replace('False','"False"').replace('True','"True"').replace("'",'"')
		return json.loads(data, object_hook=_json_object_hook)
	for post in snapshot:
		#print(json.dumps(snapshot[post], indent=4, sort_keys=True))	#PrettyPrint
		try:total_posts.append(json2obj(snapshot[post]))
		except:pass#print(type(snapshot[post]),snapshot[post],json2obj(snapshot[post]))
	return (total_posts[::-1],snapshot) #Obtiene la lista de objetos y el json




@app.route('/')
def index_page():
	'''
		Pagina de inicio
	'''
	flash_msg = None
	if ("session_id" in session):
		try:
			# verify session_id
			decoded_clamis = auth.verify_session_cookie(session["session_id"])   
			#flash(decoded_clamis)
			session['email_addr'] = decoded_clamis['email']
			session['id'] = decoded_clamis['user_id']
			#session variable to indicate errors
			session["status"]  = None
				
			user_doc = users_coll.document(decoded_clamis['user_id'])
			user_details = user_doc.get().to_dict()
			connected_chats = user_details.get("connected_chats")
			session["user_name"] = user_details.get("name")

			#Gets already saved tweets
			user_doc = users_coll.document(session['id'])
			saved = [str(x) for x in user_doc.get().to_dict().get("saved_tweets")]

			return render_template("index.html",posts=GetPosts()[0],user_name = session["user_name"],active=1,title = "COVIBOT",subtitle = "count",saved=saved)
		except Exception as e:
			# if unable to verify session_id for any reason
			# maybe invalid or expired, redirect to login
			session["status"] = "Tu sesión ha expirado!, ingresa de nuevo."
			return render_template('landing.html',status=session["status"])
			#return "INDEX EXCEPTION" + str(e)

	return render_template('landing.html')   






@app.route('/register', methods=["GET", "POST"])
def user_register():
	if (request.method == "POST"):
		user_name = request.form['userName']
		user_email = request.form['userEmail']
		user_password = request.form['userPassword']
		flash_msg = None
		try:
			user_recode = user_auth.create_user_with_email_password(user_email, user_password)
			# get idToken
			user_id_token = user_recode.get('idToken')
			# get a session cookie using id token and set it in sessions
			# this will automatically create secure cookies under the hood
			user_session_cookie = auth.create_session_cookie(user_id_token, expires_in=datetime.timedelta(days=14))		   
			session['session_id'] = user_session_cookie
			# add user document to users collection
			session["id"] = user_recode.get('localId')
			users_coll.add({"name": user_name,
							"email": user_email,
							"model_desc":'',
							"saved_tweets":[],
							"model_file":{"model_id":0,"model_name":''}
			}, user_recode.get('localId'))
			
			session["status"] = "Success"
			# if registration is valid then redirect to index page
			return redirect(url_for('index_page'))
		except requests.HTTPError as e:
			if ("EMAIL_EXISTS" in str(e)):
				flash_msg = "You have already registerd! Please log in."
			elif ("INVALID_EMAIL" in str(e)):
				flash_msg = "Please enter a valid email address"
			elif ("WEAK_PASSWORD" in str(e)):
				flash_msg = "Please use a strong password"
			else:
				flash_msg = "Something is wrong!!"+str(e)		
			session["status"] = flash_msg#+str(e)
			return render_template('sign-up-img.html',status=session["status"])
	# return to login page for GET
	return render_template('sign-up-img.html')




@app.route('/login', methods=["GET","POST"])
def user_login():
	if (request.method == "POST"):
		user_email = request.form['email']
		user_password = request.form['password']
		try:
			user_rememberme = request.form['rememberme']
			user_rememberme = True
		except:user_rememberme = False
		flash_msg = None
		try:
			user_recode = user_auth.sign_in_user_with_email_password(user_email, user_password)
			session["token"] = user_recode
		
			# get idToken
			user_id_token = user_recode.get('idToken')

			# get a session cookie using id token and set it in sessions
			# this will automatically create secure cookies under the hood
			if user_rememberme:
				user_session_cookie = auth.create_session_cookie(user_id_token, expires_in=datetime.timedelta(days=14))		   
			else:
				user_session_cookie = auth.create_session_cookie(user_id_token, expires_in=datetime.timedelta(seconds=300))		   
			session['session_id'] = user_session_cookie


			# if username passwd valid then redirect to index page
			return redirect(url_for('index_page'))

		except requests.HTTPError as e:
			if ("EMAIL_NOT_FOUND" in str(e)):
				flash_msg = "Please register before login"
			elif ("INVALID_EMAIL" in str(e)):
				flash_msg = "Please enter a valid email address"
			elif ("INVALID_PASSWORD" in str(e)):
				flash_msg = "Email or Password is wrong"
			else:
				flash_msg = "Something is wrong!!"
		flash(flash_msg)

	return render_template("sign-in-img.html",auth = False)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#	 if request.method == 'POST':
#		 session['email'] = request.form['email']
#		 session['password'] = request.form['password']
#		 return redirect(url_for('dashboard'))
#	 # return '''
#	 #	 <form method="post">
#	 #		 <p><input type=text name=email></p>
#	 #		 <p><input type=text name=password></p>
#	 #		 <p><input type=submit value=Login></p>
#	 #	 </form>
#	 # '''
#	 return render_template('sign-in-img.html')







#MODEL MANAGEMENT
def save_json(data,uid = None):
	'''
		INPUT = dict
		Guardar data json en id[default el de la sesion] de la bd, se hace la asignacion de este modo para evitar el sessionoutofcontext error
	'''
	u_id = session['id'] if (uid == None) else uid
	user_doc = users_coll.document(u_id)
	user_doc.update(data)

def save_file(file,uid = None):
	'''
		Dado objeto file, guardar en base de datos fevici en proyectos
	'''
	# gets the id of he old file to delete it
	user_doc = users_coll.document(session['id'])
	user_details = user_doc.get().to_dict()
	# return user_details   DEBUG
	try:
		model = user_details.get("model_file")['model_id']
		blob = bucket.blob(model) 
		blob.delete()
	except:pass
	# gets the old file and deletes it



	filename = ''.join([str(int(random.random()*1000000))])					
	blob = bucket.blob(filename) 
	blob.upload_from_file(file)	

	return filename


def allowed_file(filename):
	'''
		Extensión en extensiones permitidas?
	'''
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#TWT Save
@app.route('/save/<tw_id>')
def save(tw_id):
	user_doc = users_coll.document(session['id'])
	saved_tweets = user_doc.get().to_dict().get("saved_tweets")	
	if tw_id not in saved_tweets:
		saved_tweets.append(tw_id)
		save_json({"saved_tweets":saved_tweets})

	return "sweet fam"

@app.route('/contact/<tw_id>')
def contact(tw_id):
	return jsonify(2)

@app.route('/expand/<tw_id>')
def expand(tw_id):
	return jsonify(GetTweet(tw_id))




@app.route("/update", methods=["POST"])
def update():	
	'''
		- Genera un dicionario con los formularios que se obtienen en el request con las llaves iguales al nombre del formulairo pero en mayuscula para guardarse en la bd:
		{'Nombre':nombre,...}
		- El formulario está hecho para tener dentro la información previa del usuario 
	'''
	if request.method == "POST":
		try: 

			data = {}
			form = request.form


			for field in form: 
				try:
					if request.form[field] not in ['Ingresa Valor...','','Elegir categoría primero...']:  # Solo subir si no está vacio el formulario
						data[field[0].upper()+field[1:]] = request.form[field]
				except Exception as e:return str(e)#;print(str(request.form[field]))


			if request.files['file'] and not allowed_file(request.files['file'].filename):
				save_json({"model_desc":data})
				
				session["status"] = "Se guardaron los datos pero el archivo subido no es compatible, los formatos aceptados son PDF,DOCX"
				return redirect(url_for("dashboard"))  

			else:				
				#Obtener spec para guardar
				user_doc = users_coll.document(session['id'])
				model_details = user_doc.get().to_dict().get("model_file")


				#Save file devuelve el id del archivo que se guarda con la func
				model_details["model_id"] = save_file(request.files['file'])			  
				model_details["model_name"] = request.files['file'].filename

				
				#return save_file(request.files['file']) #DEBUG
				save_json({"model_file":model_details})  #Guardar el nuevo data con el id agregado				
				save_json({"model_desc":data})  #Guardar el data parseado de los forms

				#guarda rque salio bien en status
				session["status"] = "Success"
				return redirect(url_for("dashboard"))  

		except Exception as e:return "FORM EXCEPTION: "+str(e)
	else: return 


@app.route('/settings')
def settings():
	pass

@app.route('/saved')
def saved():
	user_doc = users_coll.document(session['id'])
	saved = user_doc.get().to_dict().get("saved_tweets")	
	result = [GetTweet(x) for x in saved]
	# return str(saved)
	return render_template("saved.html",posts = result,user_name = session["user_name"],active = 2,title="Guardados",subtitle = "Aqui puedes explorar y contactar automáticamente las publicaciones que te interesa apoyar o las cuales necesites apoyo")

@app.route('/logout')
def user_logout():
	session.pop('session_id', None)
	session.clear()
	return redirect(url_for('index_page'))




@app.route('/forgot')
def forgot():
	return render_template('forget-pass-img.html')



@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
	'''
		Renderiza el proyecto con el id del usuario en la sesion actual
	'''
	model = users_coll.document(session['id']).get().to_dict()
	return str(model)
	model_desc= model["model_desc"]
	model_file = model["model_file"]
	#generates team list object for visualizing teammates
	# team_list = [team(x) for x in proj_file["project_team"]]

	return render_template("dashboard.html",posts=GetPosts()[0],model = model_desc,status = session['status'],model_file = model_file)



# @app.route("/dashboard", methods=["GET","POST"])
# def dashboard():
#	 if session.get("posts") is None:
#		 session["posts"] = [GetPosts()[1]]
#	 # if request.method == "POST":
#	 #	 note = request.form.get("note")
#	 #	 session["notes"].append(note)#Only append the note to the specific session
		
#	 return render_template("index.html",posts=GetPosts()[0])






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





if (__name__ == "__main__"):
	app.run(debug=True)
	#socketio.run(app, debug=True)	
