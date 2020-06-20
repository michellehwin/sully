# import flask dependencies
import firebase_admin
from flask import Flask, request, make_response, jsonify
from firebase_admin import credentials, firestore, initialize_app
import os
import requests
import json
from df_response_lib import *
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
        for doc in docs:
            storedata = doc.to_dict()
            storeList.append(storedata)
            print(storedata["name"])
            return {
                "payload": {
                    "google": {
                        "expectUserResponse": True,
                        "noInputPrompts": [

                        ],
                        "richResponse": {
                            "items": [
                                {
                                    "simpleResponse": {
                                        "textToSpeech": "Welcome to this Basic Card",
                                        "displayText": "Welcome to this Basic Card"
                                    }
                                },
                                {
                                    "basicCard": {
                                        # "buttons": [
                                        #     {
                                        #         "title": "Button Title",
                                        #         "openUrlAction": {
                                        #             "url": "https://some.url"
                                        #         }
                                        #     }
                                        # ],
                                        "formattedText": storedata["contact"] + "\n" + storedata["address"],
                                        # "image": {
                                        #     "url": "http://some_image.jpg",
                                        #     "accessibilityText": "Accessibility text describing the image"
                                        # },
                                        "title": storedata["name"]
                                    }
                                }
                            ],
                            # "suggestions": [
                            #     {
                            #         "title": "Aléatoire"
                            #     },
                            #     {
                            #         "title": "Top"
                            #     }
                            # ]
                        }
                    }
                }
            }
        print(storeList)
    # return a fulfillment response
    if(category != None and action != None):
        return {'fulfillmentText': 'This is a response from webhook. params: ' + category + action}
    return{'fulfillmentText': 'This is a response from webhook.'}

# create a route for webhook


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(jsonify(results()))


# run the app
if __name__ == '__main__':
    app.run()
