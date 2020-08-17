# doing necessary imports
from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import requests
import pymongo
import json
import os
from saveConversation import Conversations
from DataRequests import MakeApiRequests
from sendEmail import EMailClient
from pymongo import MongoClient

app = Flask(__name__)  # initialising the flask app with the name 'app'
hotline_no = '*08002000 / +263714734593*'

# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# processing the request from dialogflow
def processRequest(req):
    # dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo
    log = Conversations.Log()
    sessionID = req.get('responseId')
    result = req.get("queryResult")
    intent = result.get("intent").get('displayName')
    query_text = result.get("queryText")
    parameters = result.get("parameters")
    cust_name = parameters.get("cust_name")
    cust_contact = parameters.get("cust_contact")
    cust_email = parameters.get("cust_email")
    db = configureDataBase()

    if intent == 'covid_searchcountry':
        cust_country = parameters.get("geo-country")
        if(cust_country=="United States"):
            cust_country = "USA"

        fulfillmentText, deaths_data, testsdone_data = makeAPIRequest(cust_country)
        webhookresponse = "***Covid Report*** \n\n" + " New cases :" + str(fulfillmentText.get('new')) + \
                          "\n" + " Active cases : " + str(
            fulfillmentText.get('active')) + "\n" + " Critical cases : " + str(fulfillmentText.get('critical')) + \
                          "\n" + " Recovered cases : " + str(
            fulfillmentText.get('recovered')) + "\n" + " Total cases : " + str(fulfillmentText.get('total')) + \
                          "\n" + " Total Deaths : " + str(deaths_data.get('total')) + "\n" + " New Deaths : " + str(
            deaths_data.get('new')) + \
                          "\n" + " Total Test Done : " + str(deaths_data.get('total')) + "\n\n*******END********* \n "
        print(webhookresponse)
        log.saveConversations(sessionID, cust_country, webhookresponse, intent, db)
        log.saveCases( "country", fulfillmentText, db)

        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhookresponse
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "Do you want me to send the detailed report to your e-mail address? Type.. \n 1. Sure \n 2. Not now "
                            # "We have sent the detailed report of {} Covid-19 to your given mail address.Do you have any other Query?".format(cust_country)
                        ]

                    }
                }
            ]
        }
    elif intent == "Welcome" or intent == "continue_conversation" or intent == "not_send_email" or intent == "endConversation" or intent == "Fallback" or intent == "covid_faq" or intent == "select_country_option":
        fulfillmentText = result.get("fulfillmentText")
        log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
    elif intent == "send_report_to_email":
        fulfillmentText = result.get("fulfillmentText")
        log.saveConversations(sessionID, "Sure send email", fulfillmentText, intent, db)
        val = log.getcasesForEmail("country", "", db)
        print("===>",val)
        prepareEmail([cust_name, cust_contact, cust_email,val])

    elif intent == "getResults":
        if intent == "getAnyContactRisk" and intent == "getContractingRisk" and intent == "getSymptoms":
            fulfillmentText = result.get("fulfillmentText")
            allSymptoms = ['cough', 'sore throat', 'fever', 'sneezing', 'chest pains', 'shortness of breath',
                           'loss of appetite', 'loss of taste']
            extremeThreat = ['cough', 'sore throat', 'fever', 'sneezing', 'chest pains', 'shortness of breath']
            moderateThreat = ['loss of appetite', 'loss of taste', 'cough', 'sneezing']
            noThreat = ['neither of the above']
            if fulfillmentText in extremeThreat:
                if intent == "getAnyContactRisk" and intent == "getContractingRisk":
                    if fulfillmentText == "yes":
                        a = fulfillmentText
                        log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
                        return "You have extremely greater chances of having the virus. Please contact the authorities " \
                               "for further screening and please exercise self isolation. *Hotline numbers* " + hotline_no
            elif fulfillmentText in moderateThreat:
                if intent == "getAnyContactRisk" and intent == "getContractingRisk":
                    if fulfillmentText == 'maybe':
                        b = fulfillmentText
                        log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
                        return "It is advisable to contact a health specialist for further diagonistics but you are " \
                               "not " \
                               "showing severe signs of the virus. *Hotline numbers* " + hotline_no
            elif fulfillmentText in noThreat:
                if intent == "getAnyContactRisk" and intent == "getContractingRisk":
                    if fulfillmentText == "no":
                        c = fulfillmentText
                        log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
                        return "You are clear just type *precaution* for precautionary measures. "
            elif fulfillmentText in moderateThreat or fulfillmentText in noThreat:
                if intent == "getAnyContactRisk" and intent == "getContractingRisk":
                    if fulfillmentText == 'yes':
                        log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
                        return "It is advisable to contact a health specialist for further diagonistics but you are " \
                               "not " \
                               "showing severe signs of the virus. *Hotline numbers* " + hotline_no
            elif fulfillmentText in extremeThreat:
                if intent == "getAnyContactRisk" and intent == "getContractingRisk":
                    if fulfillmentText == 'no':
                        log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
                        return "It is advisable to contact a health specialist for further diagonistics but you are not " \
                               "showing severe signs of the virus. *Hotline numbers* " + hotline_no
            elif fulfillmentText in allSymptoms:
                if intent == "getAnyContactRisk":
                    if fulfillmentText == 'yes':
                        log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
                        return "You have extremely greater chances of having the virus. Please contact the authorities " \
                               "for further screening and please exercise self isolation. *Hotline numbers* " + hotline_no
                    else:
                        log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
                        return "It is advisable to contact a health specialist for further diagonistics but you are not " \
                               "showing severe signs of the virus. *Hotline numbers* " + hotline_no
            elif fulfillmentText in allSymptoms:
                if intent == "getContractingRisk":
                    if fulfillmentText == "yes":
                        log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
                        return "You have extremely greater chances of having the virus. Please contact the authorities " \
                               "for further screening and please exercise self isolation. *Hotline numbers* " + hotline_no
                    else:
                        log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
                        return "It is advisable to contact a health specialist for further diagonistics but you are not " \
                               "showing severe signs of the virus. *Hotline numbers* " + hotline_no

            else:
                log.saveConversations(sessionID, query_text, fulfillmentText, intent, db)
                return "i cannot exactly give you advice based on your answers please visit your nearest hospital for " \
                       "screening "
    elif intent == "totalnumber_cases":
        fulfillmentText = makeAPIRequest("world")

        webhookresponse = "***World wide Report*** \n\n" + " Confirmed cases :" + str(
            fulfillmentText.get('confirmed')) + \
                          "\n" + " Deaths cases : " + str(
            fulfillmentText.get('deaths')) + "\n" + " Recovered cases : " + str(fulfillmentText.get('recovered')) + \
                          "\n" + " Active cases : " + str(
            fulfillmentText.get('active')) + "\n" + " Fatality Rate : " + str(
            fulfillmentText.get('fatality_rate') * 100) + "%" + \
                          "\n" + " Last updated : " + str(
            fulfillmentText.get('last_update')) + "\n\n*******END********* \n "
        print(webhookresponse)
        log.saveConversations(sessionID, "Cases worldwide", webhookresponse, intent, db)
        #log.saveCases("world", fulfillmentText, db)

        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhookresponse
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "Do you want me to send the detailed report to your e-mail address? Type.. \n 1. Sure \n 2. Not now "
                            # "We have sent the detailed report of {} Covid-19 to your given mail address.Do you have any other Query?".format(cust_country)
                        ]

                    }
                }
            ]
        }

    elif intent == "covid_searchstate":

        fulfillmentText = makeAPIRequest("state")
        print(len(fulfillmentText))

        webhookresponse1 = ''
        webhookresponse2 = ''
        webhookresponse3 = ''
        for i in range(0,11):
            webhookresponse = fulfillmentText[i]
            # print(webhookresponse['state'])
            # js = json.loads(webhookresponse.text)

            # print(str(js.state))
            webhookresponse1 += "*********\n" + " State :" + str(webhookresponse['state']) + \
                                "\n" + " Confirmed cases : " + str(
                webhookresponse['confirmed']) + "\n" + " Death cases : " + str(webhookresponse['deaths']) + \
                                "\n" + " Active cases : " + str(
                webhookresponse['active']) + "\n" + " Recovered cases : " + str(
                webhookresponse['recovered']) + "\n*********"
        for i in range(11, 21):
            webhookresponse = fulfillmentText[i]
            # print(webhookresponse['state'])
            # js = json.loads(webhookresponse.text)

            # print(str(js.state))
            webhookresponse2 += "*********\n" + " State :" + str(webhookresponse['state']) + \
                                "\n" + " Confirmed cases : " + str(
                webhookresponse['confirmed']) + "\n" + " Death cases : " + str(webhookresponse['deaths']) + \
                                "\n" + " Active cases : " + str(
                webhookresponse['active']) + "\n" + " Recovered cases : " + str(
                webhookresponse['recovered']) + "\n*********"
        for i in range(21, 38):
            webhookresponse = fulfillmentText[i]
            # print(webhookresponse['state'])
            # js = json.loads(webhookresponse.text)

            # print(str(js.state))
            webhookresponse3 += "*********\n" + " State :" + str(webhookresponse['state']) + \
                                "\n" + " Confirmed cases : " + str(
                webhookresponse['confirmed']) + "\n" + " Death cases : " + str(webhookresponse['deaths']) + \
                                "\n" + " Active cases : " + str(
                webhookresponse['active']) + "\n" + " Recovered cases : " + str(
                webhookresponse['recovered']) + "\n*********"
        print("***World wide Report*** \n\n" + webhookresponse1 + "\n\n*******END********* \n")
        print("***World wide Report*** \n\n" + webhookresponse2 + "\n\n*******END********* \n")
        print("***World wide Report*** \n\n" + webhookresponse3 + "\n\n*******END********* \n")



        log.saveConversations(sessionID, "Indian State Cases", webhookresponse1, intent, db)
        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhookresponse1
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            webhookresponse2
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            webhookresponse3
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "Do you want me to send the detailed report to your e-mail address? Type.. \n 1. Sure \n 2. Not now "
                            # "We have sent the detailed report of {} Covid-19 to your given mail address.Do you have any other Query?".format(cust_country)
                        ]

                    }
                }
            ]
        }


    else:
        return {
            "fulfillmentText": "something went wrong,Lets start from the begning, Say Hi",
        }


def configureDataBase():
    client = MongoClient("mongodb+srv://covid:hyperlink@cluster0.dybcy.mongodb.net/covid19DB?retryWrites=true&w=majority")
    return client.get_database('covid19DB')


def makeAPIRequest(query):
    api = MakeApiRequests.Api()

    if query == "world":
        return api.makeApiWorldwide()
    if query == "state":
        return api.makeApiRequestForIndianStates()

    else:
        return api.makeApiRequestForCounrty(query)


def prepareEmail(contact_list):
    mailclient = EMailClient.GMailClient()
    mailclient.sendEmail(contact_list)


'''if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')'''
if __name__ == "__main__":
    app.run(port=5000, debug=True)# running the app on the local machine on port 8000
