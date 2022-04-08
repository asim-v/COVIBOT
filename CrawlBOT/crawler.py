import csv

# Imports from the Tweepy API
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
# To check if the file exist
import os.path
# Another imports to parse the json
import json
from urllib3.exceptions import ProtocolError


#Conexión a la BD.
import pyrebase
config = {

}
firebase = pyrebase.initialize_app(config)
db = firebase.database()


CON_KEY = ""
CON_KEY_SECRET = ""
ACC_TOKEN = ""
ACC_TOKEN_SECRET = ""


#CLASE TWEET
class myTweet():
    def __init__(self, ogTweet):
        """
        It is the constructor to my version of the tweet object.
        Parameters:
        - ogTweet: The tweet object.
        """
        # Get tweet data
        self.__getTweetData(ogTweet)
        # Get if it is a retweet or not
        self.__getRetweet(ogTweet)
        # Get user information
        self.__getUserData(ogTweet)
        # Get all the data from the entities
        self.__getFromEntities(ogTweet)
        # Get the place data
        self.__getFromPlace(ogTweet)

    def __getTweetData(self, ogTweet):
        """
        Private function to get data about the tweet object.
        Parameters:
        - ogTweet: The tweet object.
        """
        if ogTweet != None:
            self.tw_id_str = ogTweet['id_str']
            self.tw_truncated = ogTweet['truncated']
            self.tw_created_at = ogTweet['created_at']
            self.tw_coordinates = ogTweet['coordinates']
            self.tw_is_quote_status = ogTweet['is_quote_status']
            self.tw_in_reply_to_user_id_str = ogTweet['in_reply_to_user_id_str']
            self.tw_in_reply_to_status_id_str = ogTweet['in_reply_to_status_id_str']

            # If the text has more than 140 chars, the full text is inside
            # the extended_tweet object.
            if 'extended_tweet' in ogTweet:
                self.tw_text = ogTweet['extended_tweet']['full_text']
            else:
                self.tw_text = ogTweet['text']

    def __getRetweet(self, ogTweet):
        """
        Private function to get if the received tweet is a retweet or not.
        Parameters:
        - ogTweet: The tweet object.
        """
        if 'retweeted_status' in ogTweet:
            self.rt_isRetweet = True
            self.rt_OgTweetID = ogTweet['retweeted_status']['id_str']
            self.rt_OgRetwCount = ogTweet['retweeted_status']['retweet_count']
            self.rt_OgFavCount = ogTweet['retweeted_status']['favorite_count']
        else:
            self.rt_isRetweet = False
            self.rt_OgTweetID = ""
            self.rt_OgRetwCount = 0
            self.rt_OgFavCount = 0

    def __getUserData(self, ogTweet):
        """
        Private function to get information from the tweet's author
        Parameters:
        - ogTweet: The tweet object.
        """
        if ogTweet != None:
            # User information
            self.usr_name = ogTweet['user']['name']
            self.usr_id_str = ogTweet['user']['id_str']
            self.usr_verified = ogTweet['user']['verified']
            self.usr_location = ogTweet['user']['location']
            self.usr_screenname = ogTweet['user']['screen_name']
            self.usr_listedcount = ogTweet['user']['listed_count']
            self.usr_friendscount = ogTweet['user']['friends_count']
            self.usr_statusescount = ogTweet['user']['statuses_count']
            self.usr_followerscount = ogTweet['user']['followers_count']
            self.usr_favouritescount = ogTweet['user']['favourites_count']

    def __getFromEntities(self, ogTweet):
        """
        Private function to get the list of the hashtags, media files or urls
        that are used on the tweet
        Parameters:
        - ogTweet: The tweet object.
        """
        self.ent_urls = ""
        self.ent_media = ""
        self.ent_hashtags = ""

        if 'media' in ogTweet['entities']:
            for media in ogTweet['entities']['media']:
                self.ent_media += media['expanded_url'] + " | "

        for hasht in ogTweet['entities']['hashtags']:
            self.ent_hashtags += hasht['text'] + " | "

        for url in ogTweet['entities']['urls']:
            self.ent_urls += url['url'] + " | "

        self.ent_urls = self.ent_urls[:-3]
        self.ent_media = self.ent_media[:-3]
        self.ent_hashtags = self.ent_hashtags[:-3]

    def __getFromPlace(self, ogTweet):
        """
            Private function that checks if the tweet has information
            about the place the tweet was made from.

            Parameters:
                - ogTweet: The tweet object.
        """
        # Check if the place object exists or not and save it if so
        if ogTweet['place'] != None:
            self.geo_name = ogTweet['name']
            self.geo_country = ogTweet['country']
            self.geo_full_name = ogTweet['full_name']
            self.geo_place_type = ogTweet['place_type']
            self.geo_country_code = ogTweet['country_code']
            self.geo_bounding_box = ogTweet['bounding_box']
        else:
            self.geo_name = ""
            self.geo_country = ""
            self.geo_full_name = ""
            self.geo_place_type = ""
            self.geo_country_code = ""
            self.geo_bounding_box = {}
    def serialize(self):
        """
        It returns the object as a dictionary
        """
        return self.__dict__
#CLASE TWEET




#IsTopic
def IsTopic(text):
	# Save Model Using Pickle
	import pandas
	from sklearn import model_selection
	from sklearn.linear_model import LogisticRegression
	import pickle
	import numpy as np
	# load the model from disk
	loaded_model = pickle.load(open('engine.sav', 'rb'))
	return loaded_model.score([text],['EnTopico'])




# Variable to know if the output file already exists or not
FILE_EXISTS = False
# Variable to count how many tweets were mined
TWEETS_COUNT = 0


def Get_Authentication():
    """
    Get the authentication of the twitter app
    """

    # Validate the Credentials
    Auth = OAuthHandler(CON_KEY, CON_KEY_SECRET)
    # Validate the Acces Tokens
    Auth.set_access_token(ACC_TOKEN, ACC_TOKEN_SECRET)
    return Auth


class MyStreamListener(StreamListener):
    """
    Class in charge of getting the tweets
    """

    def on_error(self, status):
        # status 420 is a warning to stop doing this
        if status == 420:
            return False
        # Print the error status
        print(status)

    def on_data(self, data):
        try:
            # Get the global variables
            global FILE_EXISTS
            global TWEETS_COUNT

            # Loads the tweet object
            parsed = json.loads(data)

            # Create the tweet object with the info we need and return the json
            Tweet = myTweet(parsed).serialize()
            #SAVES DATA
            if IsTopic(Tweet['tw_text']):
                #UPDATES DB STATE
                db.child("test").push(Tweet)
                StrNum = str(int(db.child("status").child("count").get().val())+1)
                db.child("status").update({"count":StrNum})
                # Plus one to the counter
                TWEETS_COUNT += 1

            # Print in the terminal
            if TWEETS_COUNT % 30 == 0:
                print('.')
            else:
                print('.', end=' ')
            return True

        except BaseException as e:
            print("->Error on data: %s" % str(e))   # Catch the error

        return True


if __name__ == '__main__':

    keyWords = ['guantes','cubrebocas','cofias', 'lentes' , 'clínicas','seguro social',
                'botiquín médico','doctora', 'enfermero','mircroempresas','sobrevivir a la cuarentena',
                'personal de salud','centro de acopio','adultos mayores','situacion vulnerable', 'salud mental', 'nutricion','resilencia',
                'acompañamiento','psicosocial','confinamiento en casa','tercera edad','mantenerte seguro',
                'test', 'apoyo', 'ayuda en casa','voluntario','salud','caretas',
                'emergencia','hospital','pandemia','higiene','provisiones','soporte','comida saludable','necesito','necesidades','caridad'
                'donar','donación','ofrecemos','donativo','suministros','servicios','bienestar','positivo','personal','vulnerable','vacuna',
                'soporte','recuperados','respiradores','hospital','emergencia','urgencia','urgente','compromiso',
               ]
    
    location = [-117.38,14.69,-86.83,32.53] #--> Mexico?
    filename = 'junio_14_20'

    print("====== Running App ======")
    try:
    # Start to the listen tweets
        auth = Get_Authentication()
        
        #Se conecta a la api de twitter para extraer con la ventana de 15 minutos
        api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_delay=5, retry_errors=5,tweet_mode='extended')
        while True:            
            try:
                myStreamListener = MyStreamListener()
                myStream = Stream(api.auth, myStreamListener)        
                print("\n>> Listening tweets")
                myStream.filter(languages=["es"], track=keyWords, stall_warnings=True,locations=location)
            except:
                continue
    # To stop the program
    except KeyboardInterrupt:
        print("\n\n>> Mining finished.")
        print(str(TWEETS_COUNT) +
              " tweets were written")
    except Exception as err:
        # Print if there is an error
        print("\n\n>> Mining finished.")
        print(str(TWEETS_COUNT) +
              " tweets were written in the TweetsExtract.csv file")
        print(err)



# total_posts = []
# post_batch = []

# TEST_LIMIT = None#queries por id
# TIME_LIMIT = 900#segundos


# def getUrgency(string):
#     return random.random()

# def getCategory(string):
#     return random.choice(['Salud','Educación','Información Oficial','Ocio','Laborales'])


# file = open('dataset.tsv')
# read = csv.reader(file, delimiter='\t')
# for i,post in enumerate(read):
#     memo = ''
#     try:
#         text = twitter.show_status(id=post[0])['text']
#         if detect(text) == 'es':
#             post_batch.append(text)
#             cprint(colored("Ingested",'green'))
#         else:cprint(colored("Not Spanish",'yellow'))
#         if TEST_LIMIT != None:
#             if i%TEST_LIMIT == 0:
#                 raise TwythonRateLimitError(f'Alcanzado Límite de prueba de {TEST_LIMIT}'.format(TEST_LIMIT),'01')
#     except Exception as e:

#         if type(e).__name__ == 'TwythonRateLimitError':       
#             start_time = time.time()
#             elapsed = time.time() - start_time
#             while (elapsed < TIME_LIMIT) :
                
#                 elapsed = time.time() - start_time
#                 for t in post_batch:
#                     try:                        
#                         #Clasificacion
#                         p = Post()
#                         p.content = t
#                         # p.category = getCategory(t)
#                         # p.urgency = getUrgency(t)
#                         p.save()
#                         #EndClasificacion
#                     except Exception as ex: cprint(f'Translation error: {ex}'.format(ex),'red')
                
#                 if e != memo:
#                     memo = e
#                     elapsed = time.time() - start_time
#                     cprint(f"Guardado Terminado {elapsed}, esperando nuevo acceso".format(elapsed),'white','on_green')
                                
#                 total_posts.extend(post_batch)        
#                 post_batch = []
        
#         else:
#             cprint(colored(e,'white','on_red'))
