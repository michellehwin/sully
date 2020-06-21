# import flask dependencies
import firebase_admin
from flask import Flask, request, make_response, jsonify
from firebase_admin import credentials, firestore, initialize_app
import os
import requests
import random
import json
from termcolor import colored
import colorama

colorama.init()

# initialize the flask app
app = Flask(__name__)

# default route
@app.route('/')
def index():
    return 'Hello World!'


# Initialize Firestore DB
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)

    # fetch action from json
    action = req.get('queryResult').get('action')
    print(colored("this is the action: " + action, "blue", 'on_white'))

    if (action == "questionnaire"):
        # print(req.get('queryResult').get('outputContexts'))
        category = req.get('queryResult').get('parameters').get('category')
        print(colored("this is the category: " + category, "blue", 'on_white'))

        zipCodeFromRequest = req.get('queryResult').get('outputContexts')[
            0].get('parameters').get('zip-code')
        print(colored("this is the zip code from the request: " +
                      zipCodeFromRequest, "blue", 'on_white'))

        if (zipCodeFromRequest == "77002"):
            city = "Houston"
        elif (zipCodeFromRequest == "76016"):
            city = "Arlington"
        elif (zipCodeFromRequest == "85005"):
            city="Phoenix"
        else:
            zipParams = {"zipcode": zipCodeFromRequest}
            zipAPI = requests.get(
                "https://us-zipcode.api.smartystreets.com/lookup?auth-id=508c10e2-e9eb-07b9-be72-2dab43c695f8&auth-token=aiA3a3D873JPzo9mLPm3", params=zipParams)
            cityJSON = zipAPI.json()
            city = cityJSON[0]["city_states"][0]["city"]
        print(colored("this is the city: " + city, "blue", 'on_white'))

        cities_ref = db.collection("cities").document(
            city).collection(category)
        print("this is the document id: " + cities_ref.id)
        docs = cities_ref.stream()

        storeList = []
        card = None
        i = 0
        for doc in docs:
            if (i <= 10):
                storedata = doc.to_dict()
                print("putting this into a card: " + storedata["name"])
                card = {
                    "title": storedata["name"],
                    # "openUrlAction": {
                    #     # "url": storedata["url"]
                    # },
                    "description": "Contact: " + storedata["contact"] + ',\n Address: ' + storedata["address"],
                    "footer": "Item 1 footer",
                }
                storeList.append(card)
                i+=1
            else:
                break

        finalJSON = {
            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": "Here's some local businesses!"
                                }
                            },
                            {
                                "carouselBrowse": {
                                    "items": 
                                        storeList
                                    
                                }
                            }
                        ]
                    }
                }
            }
        }
        print(finalJSON)
        return(finalJSON)

    # return default fulfillment response
    if(action != None):
        return {'fulfillmentText': 'This is a response from webhook. params: ' + action}
    return{'fulfillmentText': 'This is a response from webhook.'}


# create a route for webhook
@ app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(jsonify(results()))

