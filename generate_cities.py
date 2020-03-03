#! /usr/bin/env python3
import json
import mysql.connector

database = mysql.connector.connect(user="root", password="3motionTweets_", host="192.168.2.101", port="3307", database="EmotionTweets_")
cursor = database.cursor()

addCityRequest = "INSERT INTO Ville (nom, region, lat, lon) VALUES ( %s, %s, %s, %s )"

with open('fr.json') as doc :

    data = json.load(doc)

    for element in data :

        adding = (element["city"], element["admin"], element["lat"], element["lng"])
        cursor.execute(addCityRequest, adding)
        database.commit()

cursor.close()
database.close()
