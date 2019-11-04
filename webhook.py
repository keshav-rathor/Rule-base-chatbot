import json
import os
import traceback
import random

from bson.objectid import ObjectId
from flask import Flask
from flask import request, make_response
from pymongo import MongoClient

from content import region_facebook_video, training_response, partnership_response, facts, fun, trivia
from utils import ButtonList

MONGODB_URI = "mongodb+srv://kamlesh:techmatters123@aflatoun-quiz-pflgi.mongodb.net/test?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
db = client.aflatoun
questions = db.questions


job_detail={}

# Empty list for previously asked question
previous_questions = []
previous_explanation = []
flag = 0
training_buttons = ButtonList(training_response.keys(), default="training")
partnership_buttons = ButtonList(partnership_response.keys(), default="partnership")



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
            print(previous_explanation)
            print(previous_questions)
            previous_questions.clear()
            previous_explanation.clear()
            print(previous_explanation)
            print(previous_questions)
            flag = 0
            return {
                "source": "webhook"
            }
          
        elif action == "Jobs" :
           result = req.get("queryResult")
           parameter=result.get("parameters")
           job_detail.update(parameter)
            

      
     
      
        elif action == "show.card":
            result = req.get("queryResult")
            category = result.get("parameters").get("category")
            explanations = questions.aggregate([
                {
                    '$sample': {
                        "size": 40
                    }
                },
                {
                    '$match': {
                        "category": category,
                        "type": "explanation",
                        "_id": {
                            "$nin": previous_explanation
                        }
                    }
                }
            ])

            try:
                explanation = explanations.next()
            except StopIteration:
                explanation = None

            if explanation:
                previous_explanation.append(explanation["_id"])
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        # make_text_response(explanation["description"]),
                        get_response_media(explanation, platform="None"),
                        get_response_media(explanation),
                        {
                            "quickReplies": {
                                "title": "What would you like to do next? 🤔",
                                "quickReplies": [
                                    "Quiz Time 🔎",
                                    "Next Lesson ⛓",
                                    "Entertainment  🥳"
                                ]
                            },
                            "platform": "FACEBOOK"
                        }
                    ]
                }
            else:
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "text": {
                                "text": [
                                    f"That's the spirit 👻 - you have completed the {category} lesson.\nWhat would "
                                    f"you like to do next? 🤔\n8. Take a Quiz 🔎\n10. See Other Topic 👀\n 4. Fun 🎢"
                                ]
                            }
                        },
                        make_text_response(f"That's the spirit 👻 - you have completed the {category} lesson."),
                        {
                            "quickReplies": {
                                "title": "What would you like to do next? 🤔",
                                "quickReplies": [
                                    "Take a Quiz 🔎",
                                    "See Other Topic 👀",
                                    "Entertainment  🥳"
                                ]
                            },
                            "platform": "FACEBOOK"
                        }
                    ]
                }


        elif action == "input.unknown":
            flag += 1
            if flag >= 2:
                flag = 0
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "text": {
                                "text": [
                                    "Anything for you but first you have to be clear about what you are asking "
                                    "for.\nI can help you these following things:\n1. Learn 📝\n2. Train 👨🏼‍🏫\n3. "
                                    "Aflatoun Stories 🌏",
                                ]
                            }
                        },
                        {
                            "text": {
                                "text": [
                                    "I am fully aware of what you want but I don't have knowledge about that.",
                                ]
                            },
                            "platform": "FACEBOOK"
                        },
                        {
                            "quickReplies": {
                                "title": "I can help you these following things",
                                "quickReplies": [
                                    "Learn 📝",
                                    "Train 👨‍🏫",
                                    "Aflatoun Stories 🌏",
                                    "Entertainment 🥳"
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
