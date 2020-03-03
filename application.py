#!/usr/bin/env python3
import json
#import requests
from bs4 import BeautifulSoup
import tweepy
from pyFeel import Feel
from flask import *
import logging
import mysql.connector
import time
from datetime import datetime

database = mysql.connector.connect(user="", password="", host="", port="", database="")
cursor = database.cursor(buffered=True)
print(database)

#Instanciation de Flask application
application = Flask(__name__)
application.config['SECRET_KEY']=''

#Module pour nous aider avec la debuggage
handler = logging.FileHandler('logs.txt')
handler.setLevel(logging.ERROR)
application.logger.addHandler(handler)


#Token Access au Twitter API
ACCESS_TOKEN = '-'
ACCESS_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET =  ''

#Connection au twitter API
oath = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
oath.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(oath,wait_on_rate_limit=True)


#On essaie de se connecter au twitter
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error")

#get_coordinates('Montpellier')
#for (lat, lon) in cursor:
#    print("lat: {}, lon: {}".format(lat, lon))

#Cette fonction pren
def get_coordonnes(region):
    regions_dict= {}
    coordinates = {}

    #on ouvre le fichier json
    with open('fr.json') as json_file:
        data = json.load(json_file)

        #1.On cree coordinates dictionnary ou pour chaque ville, on associe
        #un liste avec lat lng. Ex: {Montpellier: ["lat",20,"lng",40]}

        #2.On cree regions_dict ou on associe les cles Region et values une liste des Villes
        #On obtient par exemple  {Hauts-de-France: [Lyon , Amiens, etc]} 
        for ville in data:
            coordinates.setdefault(ville["city"],[]).append("lat")
            coordinates.setdefault(ville["city"],[]).append(ville["lat"])
            coordinates.setdefault(ville["city"],[]).append("lng")
            coordinates.setdefault(ville["city"],[]).append(ville["lng"])
            regions_dict.setdefault(ville["admin"],[]).append(ville["city"])

    #Donnes temporaires
    qq = {}
    fin = {}

    #Ca associe pour chaque region du dictionnaire "regions", leur villes,
    #ltd et lng. Ex
    for chaque_region,chaque_ville in regions_dict.items():
        fin[chaque_region] = {}
        for each in chaque_ville:
            it = iter(coordinates[each])
            res_dict = dict(zip(it,it))
            qq[each] = res_dict
            fin[chaque_region][each]=qq[each]
    

    #fin contient toutes les regions avec toutes les villes et leur ltd, lng.
    #on renvoi les villes du region demandee.
    return fin[region]


def get_feel(region):

    cursorUser = database.cursor(buffered=True)
    cursorTweet = database.cursor(buffered=True)

    getCityQuery = ("SELECT nom, lat, lon FROM Ville WHERE region= %s")
    getUserIdQuery = ("SELECT userId FROM User WHERE twitterId =%s")
    insertTweetQuery = ("INSERT IGNORE INTO Tweet (idUser, date, text, idVille, emotionJson) VALUES (%s, %s, %s, %s, %s)")
    insertUserQuery = ("INSERT IGNORE INTO User (twitterId, username) VALUES (%s, %s)")

    cityList = (region, )
    cursor.execute(getCityQuery, cityList)

    for (nom, lat, lon) in cursor:

        for tweet in tweepy.Cursor(api.search, geocode=""+str(lat)+","+str(lon)+",30km", lang='fr').items(5):

            currentUser = (tweet.user.id, tweet.user.screen_name)
            cursorUser.execute(insertUserQuery, currentUser)
            database.commit()

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(str(tweet.created_at), '%Y-%m-%d %H:%M:%S'))
            feels = Feel(tweet.text)
            var = feels.emotions()
            var = json.dumps(var)
            tweetBuf = (tweet.user.id, timestamp, tweet.text, nom, var)
            cursorTweet.execute(insertTweetQuery, tweetBuf)
            database.commit()

            #print(timestamp)
            #print("id: {}, username: {}".format(tweet.user.id, tweet.user.screen_name))
            #print(var)

#testRegion = "Occitanie"
#get_feelTest(testRegion)


#Uses pyFeel to detect feelings in different regions
def get_feelObs(region,language,nbr):
    #Dictionnaire avec toutes les villes + leur ltd + lng du cette region
    coordonnes_dict = get_coordonnes(region)
    print(coordonnes_dict)

    #Dictionnaire pour stocker les tweets
    new = {}
    #Dictionnaire finale
    resultat ={}

    #Cherche les tweets par les villes
    for city,value in coordonnes_dict.items():
    	#On creer des dictionnaires vide pour chaque ville.
        new[city] = {}
        for tweet in tweepy.Cursor(api.search,geocode=""+coordonnes_dict[city]['lat']+","+coordonnes_dict[city]['lng']+",30km",lang=language).items(nbr):
           #Pour chaque villes, on creer dans le dict_vide:
           #tweet.id (comme cle) et tweet.text comme value:
           #Exemple: {Montpellier:{
           #"1302039120":"ce truc est jolie bla bla",
           #"12301230":"etc etc etc"}
           #}
           new[city][tweet.id] = tweet.text
    print(new)

    #On cree un nouveau dict(resultat): City --> Feelings (la somme des feelings from les tweets choisis)
    #new contient
    for key,value in new.items():
    	#Template pour chaque ville
        tmp = {'positivity': 0.0, 'joy': 0.0, 'fear': 0.0, 'sadness': 0.0, 'angry': 0.0, 'surprise': 0.0, 'disgust': 0.0}
       
        #On stocke les donnes finales ici
        resultat[key] = {}
        
        #pyFeel pour chaque tweet.text from value(qui est un dictionnaire aussi)
        for tweet_id,tweet_text in value.items():
            test = Feel(tweet_text)
            var = test.emotions()
            print(f"City {key} and id {tweet_id} has emotions: {var}")
            #On sommes les resultat des feelings pour cette ville
            for emotion,value in var.items():
                 tmp[emotion] += value

            #On ajoute dans le dict finale la ville comme cle et les feelings comme value
            resultat[key] = tmp
    #on renvoie 
    return resultat
   
'''
@application.route('/', methods=['GET','POST'])
def form():
    with open('fr.json') as json_file:
        cities = json.load(json_file)
        for city in cities:
            new_dict.setdeafault(each['admin'], []).append(each['city'])
'''

@application.route('/',methods=['GET','POST'])
def form():
    listStatus = ['en','fr','bg']
    new_dict = {}
    numbers = [5,10,20,50,100]
    #On remplit le dictionnaire new_dict avec les pour chaque région la liste des villes
    with open('fr.json') as json_file:

        data = json.load(json_file)
        for each in data:
            new_dict.setdefault(each['admin'],[]).append(each['city'])

    
    #Si on click le bouton Submit
    if request.method=='POST':
        #on prends les donnes de la forme
        reg_dict=request.form["regions_brato"]
        #b = request.form["list_status"]
        #nb = request.form["numbers"]
        #On utilise geocode pour pouvoir reagir avec Leaflet
        geocode= get_coordonnes(reg_dict)
        feelings_dict = get_feelObs(reg_dict,'fr',int(5))
        get_feel(reg_dict)
        return render_template('template.html',feelings_js=feelings_dict, geocode_js=geocode, a=reg_dict)
    else:
        return render_template('index.html',new_dict=new_dict)

if __name__=="__main__":

    application.run(debug=True, host="0.0.0.0")



