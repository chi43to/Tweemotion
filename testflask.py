#!/usr/bin/env python3
import tweepy
from pyFeel import Feel
from flask import *
import mysql.connector
import time
from datetime import datetime
import json

DATABASE = mysql.connector.connect(user="", password="", host="", port="3307", database="")
CURSOR = DATABASE.cursor(buffered=True)
CURSOR2 = DATABASE.cursor(buffered=True)

APP = Flask(__name__)
APP.config['SECRET_KEY'] = ''

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

def get_emotions(region):
    get_villes_query = "SELECT nom FROM Ville WHERE region = %s"
    get_emotions_from_ville_query = "SELECT emotionJson FROM Tweet WHERE idVille = %s"
    
    city_emotions = {}

    CURSOR.execute(get_villes_query, (region,))

    for resultat in CURSOR :

        CURSOR2.execute(get_emotions_from_ville_query, (resultat[0],))
        emotions_dic = {'angry': 0.0, 'disgust': 0.0, 'fear': 0.0, 'joy': 0.0, 'positivity': 0.0, 'sadness': 0.0, 'surprise': 0.0}
        
        for emotions in CURSOR2 :
            buff = json.loads(emotions[0])
            
            for key in buff :        
                emotions_dic[key] += buff[key]
        
        city_emotions[resultat[0]] = emotions_dic

    return city_emotions

def get_feel(region):

    cursorUser = DATABASE.cursor(buffered=True)
    cursorTweet = DATABASE.cursor(buffered=True)

    getCityQuery = ("SELECT nom, lat, lon FROM Ville WHERE region= %s")
    getUserIdQuery = ("SELECT userId FROM User WHERE twitterId =%s")
    insertTweetQuery = ("INSERT IGNORE INTO Tweet (idUser, date, text, idVille, emotionJson) VALUES (%s, %s, %s, %s, %s)")
    insertUserQuery = ("INSERT IGNORE INTO User (twitterId, username) VALUES (%s, %s)")

    cityList = (region, )
    CURSOR.execute(getCityQuery, cityList)

    for (nom, lat, lon) in CURSOR :

        for tweet in tweepy.Cursor(api.search, geocode=""+str(lat)+","+str(lon)+",30km", lang='fr').items(5):

            currentUser = (tweet.user.id, tweet.user.screen_name)
            cursorUser.execute(insertUserQuery, currentUser)
            DATABASE.commit()

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(str(tweet.created_at), '%Y-%m-%d %H:%M:%S'))
            feels = Feel(tweet.text)
            var = feels.emotions()
            var = json.dumps(var)
            tweetBuf = (tweet.user.id, timestamp, tweet.text, nom, var)
            cursorTweet.execute(insertTweetQuery, tweetBuf)
            DATABASE.commit()


@APP.route('/', methods=['GET', 'POST'])
def form():
    get_region_query = "SELECT nom FROM Region"
    get_ville_coords = "SELECT lat, lon FROM Ville WHERE nom = %s"

    CURSOR.execute(get_region_query)
    regions = ["---Choisissez une région---"]
    
    for nom in CURSOR:
        
        if nom[0] != '':
            regions.append(nom[0])
    
    if request.method == 'POST':
        region = request.form['region-list']
        mode = request.form['mode']
        
        if region != "---Choisissez une région---" :
            
            if mode == 'generate' :
                emotions = get_emotions(region)
            
                for ville in emotions :    
                    emotions[ville]['anger'] = emotions[ville].pop('angry')
            
                return emotions

            else :
                get_feel(region)
                print("tweets were added to the database from region : {}".format(region))
                return render_template('template2.html', regions=regions)

        else:
            return render_template('index.html', regions=regions)
    
    else:
        return render_template('index.html', regions=regions)

APP.run(debug=True, host='0.0.0.0')
