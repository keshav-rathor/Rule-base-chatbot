import json
import os
import traceback
import random

from bson.objectid import ObjectId
from flask import Flask
from flask import request, make_response
from pymongo import MongoClient

#from utils import ButtonList

MONGODB_URI = "mongodb+srv://kamlesh:techmatters123@aflatoun-quiz-pflgi.mongodb.net/test?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
db = client.hrchatbot
candidates = db.Chatbots_Candidates
job=db.Hiring_PublicJobPosition




job_detail={}
name={}

# Flask app should start in global layout
app = Flask(__name__)


# Defining a function which inputs a text and outputs the formatted object to return in facebook response
def make_text_response(message, platform="FACEBOOK"):
    return {
        "text": {
            "text": [
                message
            ]
        },
        "platform": platform
    }


information=["experiance","skills","CTC","Location"]
information_previous=[]
def show(information,information_previous):
    if len(information) != 0:
        information_sample = random.choice(information)
        information_previous.append(information_sample)
        information.remove(information_sample)
    return information_sample


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = process_request(req)
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def process_request(req):
    
    try:
        action = req.get("queryResult").get("action")

        if action == "input.welcome":
            # CLear the previous question list if start over

            return {
                "source": "webhook"
            }
        elif action == "name":
            result = req.get("queryResult")
            parameter = result.get("parameters")
            job_detail.update(parameter)
        # candidates.insert(name)

        elif action == "Jobs":
           result = req.get("queryResult")
           parameter=result.get("parameters")
           job_detail.update(parameter)
            # print("Job details", job_detail)
            # print("Name", name)
            if len(job_detail)>=6:
               print("Got all job details")
               candidates.insert(job_detail)
               show_job = job.find_one({"jobTitle": job_detail["jobTitle"], "locality": job_detail["locality"]})
               print(show_job)
               return {
                   "source": "webhook",
                   "fulfillmentMessages":[
                       {
                           "card": {
                               "title": show_job["jobTitle"],
                               "subtitle": show_job["companyName"] + " | " + show_job["locality"] + " | " + show_job["region"],
                               "imageUri": "https://akm-img-a-in.tosshub.com/sites/btmt/images/stories/jobs660_090518050232_103118054303_022119084317.jpg",
                               "buttons": [
                                   {
                                       "text": "View Job Detail",
                                       "postback": show_job["jobDetailsUrl"]
                                   }
                               ]
                           },
                           "platform": "FACEBOOK"
                       }


                   ]
               }



    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
        return {
            "fulfillmentText": "Oops... 😮 I am not able to help you at the moment, please try again..",
            "source": "webhook"
        }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port {}".format(port))
    app.run(debug=False, port=port, host='0.0.0.0')
