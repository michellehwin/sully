# import flask dependencies
import firebase_admin
from flask import Flask, request, make_response, jsonify
from firebase_admin import credentials, firestore, initialize_app
import os
import requests
from df_response_lib import *

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
    print(action)
    parameters = req.get('queryResult').get('parameters').get('zip-code')
    print(parameters)

    if (action == "questionnaire"):
        print(req.get('queryResult').get('outputContexts'))

    if (action == "DefaultWelcomeIntent.DefaultWelcomeIntent-next.DefaultWelcomeIntent-next-custom"):
        zipParams = {"zipcode": parameters}
        zipAPI = requests.get("https://us-zipcode.api.smartystreets.com/lookup?auth-id=508c10e2-e9eb-07b9-be72-2dab43c695f8&auth-token=aiA3a3D873JPzo9mLPm3", params = zipParams)
        cityJSON = zipAPI.json()
        city = cityJSON[0]["city_states"][0]["city"]
        cities_ref = db.collection(u'cities')
        docs = cities_ref.stream()
        for doc in docs:
            print(f'{doc.id} => {doc.to_dict()}')
        
        # returns city name from zipcode
    #     return{'outputContexts': {
    #   "name": "await_questionnare",
    #   "parameters": {
    #     "city": city
    #   }
    # }}


    # return a fulfillment response
    # return {'fulfillmentText': 'This is a response from webhook.' + parameters + action}

# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(jsonify(results()))

# run the app
if __name__ == '__main__':
   app.run()
