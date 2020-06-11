from twython import Twython, TwythonRateLimitError
import csv
from langdetect import detect
from termcolor import colored,cprint
import time
import fireo
from fireo.models import Model,TextField,NumberField
import random

#solo para hacer pruebas locales, en cgloud se autentifica automáticamente
fireo.connection(from_file="keyfile.json")
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
post_batch = []

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
        text = twitter.show_status(id=post[0])['text']
        if detect(text) == 'es':
            post_batch.append(text)
            cprint(colored("Ingested",'green'))
        else:cprint(colored("Not Spanish",'yellow'))
        if TEST_LIMIT != None:
            if i%TEST_LIMIT == 0:
                raise TwythonRateLimitError(f'Alcanzado Límite de prueba de {TEST_LIMIT}'.format(TEST_LIMIT),'01')
    except Exception as e:

        if type(e).__name__ == 'TwythonRateLimitError':       
            start_time = time.time()
            elapsed = time.time() - start_time
            while (elapsed < TIME_LIMIT) :
                
                elapsed = time.time() - start_time
                for t in post_batch:
                    try:                        
                        #Clasificacion
                        p = Post()
                        p.content = t
                        # p.category = getCategory(t)
                        # p.urgency = getUrgency(t)
                        p.save()
                        #EndClasificacion
                    except Exception as ex: cprint(f'Translation error: {ex}'.format(ex),'red')
                
                if e != memo:
                    memo = e
                    elapsed = time.time() - start_time
                    cprint(f"Guardado Terminado {elapsed}, esperando nuevo acceso".format(elapsed),'white','on_green')
                                
                total_posts.extend(post_batch)        
                post_batch = []
        
        else:
            cprint(colored(e,'white','on_red'))
