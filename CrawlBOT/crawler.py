from twython import Twython, TwythonRateLimitError
import pickle
import csv
from googletrans import Translator
from termcolor import colored,cprint
import time
from fireo.models import Model,TextField,NumberField
import random

#solo para hacer pruebas locales, en cgloud se autentifica automáticamente
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keyfile.json"
#solo para hacer pruebas locales, en cgloud se autentifica automáticamente


class Post(Model):
    content = TextField()
    urgency = NumberField()
    category = TextField()

CONSUMER_KEY = "CkulBfQE91jOJBNIuMb1TUbWt"
CONSUMER_SECRET = "aWAm88ju62F7CnK8s7fS5r8eDj6mXGEWnhSMKP5aMJiz5WGVfs"
OAUTH_TOKEN = "2796790086-9ffNbN5qpRrMd3B6eSKx0dBQhgHk7kEjDLqRAA1"
OAUTH_TOKEN_SECRET = "wYQzqIaMgSXICG5Zh7FDE3EBgW5R45paax763eTfyxt9E"
twitter = Twython(
    CONSUMER_KEY, CONSUMER_SECRET,
    OAUTH_TOKEN, OAUTH_TOKEN_SECRET)


total_posts = []
posts = []
translated = []
translator = Translator()

TEST_LIMIT = None#queries por id
TIME_LIMIT = 900#segundos


def getUrgency(string):
    return random.random()

def getCategory(string):
    return random.choice(['Salud','Educación','Información Oficial','Ocio','Laborales'])


file = open('dataset.tsv')
read = csv.reader(file, delimiter='\t')
for i,post in enumerate(read):
    memo = ''
    try:
        posts.append(twitter.show_status(id=post[0])['text'])
        cprint(colored("Ingested",'green'))
        if TEST_LIMIT != None:
            if i%TEST_LIMIT == 0:
                raise TwythonRateLimitError(f'Alcanzado Límite de prueba de {TEST_LIMIT}'.format(TEST_LIMIT),'01')
    except Exception as e:

        if type(e).__name__ == 'TwythonRateLimitError':       
            start_time = time.time()
            elapsed = time.time() - start_time
            while (elapsed < TIME_LIMIT) :
                
                elapsed = time.time() - start_time
                translated = []
                for t in posts:
                    try:
                        esp = translator.translate(t,dest = 'es').text
                        
                        translated.append(esp)
                        
                        #Clasificacion
                        p = Post()
                        p.content = esp
                        p.category = getCategory(esp)
                        p.urgency = getUrgency(esp)
                        p.save()
                        #EndClasificacion
                        
                    except Exception as ex: cprint(f'Translation error: {ex}'.format(ex),'red')
                
                if e != memo:
                    memo = e
                    elapsed = time.time() - start_time
                    cprint(f"Guardado Terminado {elapsed}, esperando nuevo acceso".format(elapsed),'white','on_green')
                                
                total_posts.extend(translated)        
                posts = []
        
        else:
            cprint(colored(e,'white','on_red'))

with open('parrot.pkl', 'wb') as f:
    pickle.dump(total_posts, f)